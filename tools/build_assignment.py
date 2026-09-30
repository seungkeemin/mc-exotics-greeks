#!/usr/bin/env python3
"""Build the student assignment notebook mechanically from the solution notebook.

The solution notebook is the single source of truth. The assignment notebook is
never edited by hand.

Marker convention
-----------------
In a code cell, the part students fill in is wrapped like this::

    def simulate_terminal(S0, r, sigma, T, Z):
        \"\"\"...\"\"\"
        # [빈칸 1] 위 closed form을 numpy 배열 연산 한 줄로 옮기세요.
        #   · Z 와 같은 shape 의 양수 배열이 출력되어야 합니다.
        # <<<SOL n=1
        return S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
        # SOL>>>

On build, the markers and the solution code between them are removed and a single
``...`` placeholder is left at the same indentation (the minimum needed to keep the
cell valid Python). The instructions live in the ``# [빈칸 n]`` comment block right
before the marker. That block is outside the markers, so it stays identical in both
notebooks.

Everything outside the marker blocks is copied verbatim, so the solution and the
assignment cannot drift apart.

Usage
-----
    python build_assignment.py --solution sol.ipynb --out assignment.ipynb
    python build_assignment.py --solution sol.ipynb --check    # validate only, write nothing
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import nbformat

DEFAULT_SOLUTION = Path("mc_exotics_solution.ipynb")
DEFAULT_ASSIGNMENT = Path("mc_exotics_assignment.ipynb")

OPEN_RE = re.compile(r"^#\s*<<<SOL\s+n=(\d+)\s*$")
CLOSE_RE = re.compile(r"^#\s*SOL>>>\s*$")
DEF_RE = re.compile(r"^\s*def\s+(\w+)\s*\(")
STUB = "..."
GUIDE = "# [빈칸 {n}]"


class BuildError(Exception):
    """Raised when a marker breaks the convention."""


def blank_out(source: str, cell_index: int, blanks: list[dict]) -> str:
    """Replace every SOL block in one code cell with the stub."""
    lines = source.split("\n")
    out: list[str] = []
    i = 0

    while i < len(lines):
        match = OPEN_RE.match(lines[i].strip())
        if match is None:
            out.append(lines[i])
            i += 1
            continue

        number = int(match.group(1))
        indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        i += 1

        n_code = 0
        while i < len(lines) and not CLOSE_RE.match(lines[i].strip()):
            if lines[i].strip():
                n_code += 1
            i += 1
        if i >= len(lines):
            raise BuildError(f"[셀 {cell_index}] ({number}) 의 닫는 마커 '# SOL>>>' 가 없습니다.")
        i += 1  # consume the closing marker

        has_guide = any(GUIDE.format(n=number) in line for line in out)
        out.append(indent + STUB)
        owner = next((m.group(1) for line in reversed(out) if (m := DEF_RE.match(line))), "?")
        blanks.append({"n": number, "cell": cell_index, "func": owner,
                       "n_code": n_code, "has_guide": has_guide})

    return "\n".join(out)


def validate(blanks: list[dict]) -> list[str]:
    """Check that blank numbers are unique, consecutive and ordered, and that each has a guide comment."""
    problems: list[str] = []
    numbers = [b["n"] for b in blanks]

    if len(set(numbers)) != len(numbers):
        problems.append(f"번호가 중복됩니다: {numbers}")
    if numbers != sorted(numbers):
        problems.append(f"노트북 안의 빈칸 순서가 번호 순서와 다릅니다: {numbers}")
    if sorted(numbers) != list(range(1, len(numbers) + 1)):
        problems.append(f"번호가 1부터 연번이 아닙니다: {sorted(numbers)}")

    for b in blanks:
        if not b["has_guide"]:
            problems.append(f"빈칸 {b['n']}: 마커 바로 앞에 '{GUIDE.format(n=b['n'])}' 로 시작하는 "
                            "안내 주석이 없습니다.")
        if b["n_code"] == 0:
            problems.append(f"빈칸 {b['n']}: 마커 안에 정답 코드가 없습니다.")
    return problems


def report(blanks: list[dict]) -> None:
    print(f"{'빈칸':>4}  {'함수':<26}{'정답 줄 수':>10}{'노트북 셀':>10}")
    print("-" * 55)
    for b in blanks:
        print(f"{b['n']:>4}  {b['func']:<26}{b['n_code']:>10}{b['cell']:>10}")
    print("-" * 55)
    print(f"빈칸 총 {len(blanks)}개")


def build(solution: Path, assignment: Path, check_only: bool) -> int:
    if not solution.exists():
        print(f"오류: 해답 노트북을 찾을 수 없습니다 — {solution}", file=sys.stderr)
        return 2

    nb = nbformat.read(solution, as_version=4)
    blanks: list[dict] = []

    for index, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        cell.source = blank_out(cell.source, index, blanks)
        cell.outputs = []
        cell.execution_count = None

    report(blanks)
    problems = validate(blanks)
    if problems:
        print("\n검사 실패:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    if check_only:
        print("\n검사 통과 (--check 모드이므로 파일을 쓰지 않았습니다).")
        return 0

    nb.metadata.pop("widgets", None)
    nbformat.write(nb, assignment)
    print(f"\n빈칸본을 생성했습니다: {assignment}")
    print("모든 출력(outputs)과 실행 번호는 비웠습니다.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--solution", type=Path, default=DEFAULT_SOLUTION,
                        help="입력 해답 노트북 (기본: mc_exotics_solution.ipynb)")
    parser.add_argument("--out", type=Path, default=DEFAULT_ASSIGNMENT,
                        help="출력 빈칸본 (기본: mc_exotics_assignment.ipynb)")
    parser.add_argument("--check", action="store_true",
                        help="정합성 검사만 하고 파일을 쓰지 않음")
    args = parser.parse_args()

    try:
        return build(args.solution, args.out, args.check)
    except BuildError as exc:
        print(f"빌드 오류: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

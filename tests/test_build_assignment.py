import sys
from pathlib import Path

import nbformat
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import build_assignment as ba  # noqa: E402

SOLUTION_CELL = """\
def simulate_terminal(S0, r, sigma, T, Z):
    \"\"\"doc\"\"\"
    # [빈칸 1] guide
    # <<<SOL n=1
    return S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    # SOL>>>
"""


def _write_solution(path, *sources):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_markdown_cell("# title")]
    nb.cells += [nbformat.v4.new_code_cell(s) for s in sources]
    nb.cells[1].outputs = [nbformat.v4.new_output("stream", text="answer output")]
    nb.cells[1].execution_count = 7
    nbformat.write(nb, path)


def test_build_removes_solution_and_keeps_everything_else(tmp_path):
    sol, out = tmp_path / "sol.ipynb", tmp_path / "out.ipynb"
    _write_solution(sol, SOLUTION_CELL)

    assert ba.build(sol, out, check_only=False) == 0

    cell = nbformat.read(out, as_version=4).cells[1]
    assert "np.exp" not in cell.source
    assert "SOL" not in cell.source
    assert "    ..." in cell.source
    assert "# [빈칸 1] guide" in cell.source
    assert cell.outputs == [] and cell.execution_count is None


def test_check_rejects_missing_guide_and_gaps(tmp_path):
    no_guide = SOLUTION_CELL.replace("# [빈칸 1] guide\n", "").replace("n=1", "n=2")
    sol = tmp_path / "sol.ipynb"
    _write_solution(sol, no_guide)
    assert ba.build(sol, tmp_path / "out.ipynb", check_only=True) == 1


def test_unclosed_marker_raises():
    with pytest.raises(ba.BuildError):
        ba.blank_out("# <<<SOL n=1\nx = 1\n", 0, [])

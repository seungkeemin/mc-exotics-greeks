import numpy as np
import pytest

# Same contract and simulation settings as the notebook.
S0, K, B = 100.0, 100.0, 85.0
R, SIGMA, T = 0.03, 0.20, 1.0
SEED = 20260828
N_TERMINAL = 500000
N_PATH, N_STEPS = 20000, 252
H_SPOT, H_VOL = 3.0, 0.02


@pytest.fixture(scope="session")
def Z_terminal():
    return np.random.default_rng(SEED).standard_normal(N_TERMINAL)


@pytest.fixture(scope="session")
def Z_path():
    return np.random.default_rng(SEED + 10).standard_normal((N_PATH, N_STEPS))

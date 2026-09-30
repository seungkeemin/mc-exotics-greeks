import numpy as np


def simulate_terminal(S0, r, sigma, T, Z):
    """Terminal GBM price S_T under the risk-neutral measure from standard normals Z.

    Uses the exact solution, so there is no discretisation error. Z is passed in
    (not drawn here) so that bump-and-revalue can reuse the same draws.
    """
    return S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)


def simulate_paths(S0, r, sigma, T, Z):
    """GBM paths of shape (n_paths, n_steps + 1) from Z of shape (n_paths, n_steps).

    Column 0 is t=0 and equals S0 on every path.
    """
    n_paths, n_steps = Z.shape
    dt = T / n_steps
    log_increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    S_after_start = S0 * np.exp(np.cumsum(log_increments, axis=1))
    return np.concatenate([np.full((n_paths, 1), S0), S_after_start], axis=1)

import numpy as np

from .paths import simulate_paths, simulate_terminal
from .stats import mc_stats


def digital_call_mc(S_T, K, r, T):
    """(price, standard error) of a cash-or-nothing digital call from terminal samples S_T."""
    discounted_payoff = np.exp(-r * T) * (S_T > K)
    return mc_stats(discounted_payoff)


def digital_price(spot, vol, Z, *, K, r, T):
    """Digital call price as a function of (spot, vol, Z), the pricer shape fd_greeks expects.

    Bind the contract terms with functools.partial(digital_price, K=K, r=r, T=T).
    """
    S_T = simulate_terminal(spot, r, vol, T, Z)
    return digital_call_mc(S_T, K, r, T)[0]


def vanilla_call_payoff(S_paths, K):
    """Undiscounted vanilla call payoff on each path."""
    return np.maximum(S_paths[:, -1] - K, 0.0)


def down_out_call_payoff(S_paths, K, B):
    """Undiscounted down-and-out call payoff on each path (discrete daily monitoring)."""
    survived = S_paths.min(axis=1) > B
    return np.where(survived, np.maximum(S_paths[:, -1] - K, 0.0), 0.0)


def down_in_call_payoff(S_paths, K, B):
    """Undiscounted down-and-in call payoff on each path.

    Defined from its own knock-in condition, not as vanilla minus down-and-out,
    so that the in-out parity is something the code verifies rather than assumes.
    """
    knocked_in = ~(S_paths.min(axis=1) > B)
    return np.where(knocked_in, np.maximum(S_paths[:, -1] - K, 0.0), 0.0)


def barrier_prices(spot, vol, Z, *, K, B, r, T):
    """Prices [vanilla, down-and-out, down-and-in] from one set of simulated paths.

    Bind the contract terms with functools.partial(barrier_prices, K=K, B=B, r=r, T=T).
    """
    paths = simulate_paths(spot, r, vol, T, Z)
    discount = np.exp(-r * T)
    return discount * np.array([
        vanilla_call_payoff(paths, K).mean(),
        down_out_call_payoff(paths, K, B).mean(),
        down_in_call_payoff(paths, K, B).mean(),
    ])

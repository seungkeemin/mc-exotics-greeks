from functools import partial

import numpy as np

from mc_exotics import (
    barrier_prices,
    bs_call_greeks,
    digital_call_analytic,
    digital_call_mc,
    down_in_call_payoff,
    down_out_call_payoff,
    fd_greeks,
    mc_stats,
    simulate_paths,
    simulate_terminal,
    vanilla_call_payoff,
)

from conftest import B, H_SPOT, H_VOL, K, N_PATH, N_STEPS, R, S0, SEED, SIGMA, T


def test_digital_mc_matches_closed_form(Z_terminal):
    S_T = simulate_terminal(S0, R, SIGMA, T, Z_terminal)
    price, se = digital_call_mc(S_T, K, R, T)
    exact = digital_call_analytic(S0, K, R, SIGMA, T)
    assert abs((price - exact) / se) < 3


def test_in_out_parity_holds_path_by_path(Z_path):
    paths = simulate_paths(S0, R, SIGMA, T, Z_path)
    gap = (down_out_call_payoff(paths, K, B) + down_in_call_payoff(paths, K, B)
           - vanilla_call_payoff(paths, K))
    assert np.abs(gap).max() < 1e-10

    # The parity must also survive bump-and-revalue: the Greeks are linear in price.
    pricer = partial(barrier_prices, K=K, B=B, r=R, T=T)
    for g in fd_greeks(pricer, S0, SIGMA, Z_path, H_SPOT, H_VOL):
        assert abs(g[1] + g[2] - g[0]) < 1e-10


def test_same_seed_gives_identical_results():
    def run():
        Z = np.random.default_rng(SEED + 10).standard_normal((2000, N_STEPS))
        return barrier_prices(S0, SIGMA, Z, K=K, B=B, r=R, T=T)

    np.testing.assert_array_equal(run(), run())


def test_vanilla_fd_greeks_within_3_se_of_black_scholes(Z_path):
    # Delta and vega from central differences are path-wise averages of payoff
    # differences under common random numbers, so their standard error is the
    # standard error of those per-path differences.
    discount = np.exp(-R * T)

    def payoff(spot, vol):
        return discount * vanilla_call_payoff(simulate_paths(spot, R, vol, T, Z_path), K)

    delta_samples = (payoff(S0 + H_SPOT, SIGMA) - payoff(S0 - H_SPOT, SIGMA)) / (2 * H_SPOT)
    vega_samples = (payoff(S0, SIGMA + H_VOL) - payoff(S0, SIGMA - H_VOL)) / (2 * H_VOL)
    delta_exact, _, vega_exact = bs_call_greeks(S0, K, R, SIGMA, T)

    for samples, exact in ((delta_samples, delta_exact), (vega_samples, vega_exact)):
        estimate, se = mc_stats(samples)
        assert abs(estimate - exact) < 3 * se

    # The per-path estimator is the same number fd_greeks reports.
    pricer = partial(barrier_prices, K=K, B=B, r=R, T=T)
    delta, _, vega = fd_greeks(pricer, S0, SIGMA, Z_path, H_SPOT, H_VOL)
    np.testing.assert_allclose([delta[0], vega[0]],
                               [delta_samples.mean(), vega_samples.mean()], rtol=1e-12)


def test_paths_start_at_spot_and_have_expected_shape(Z_path):
    paths = simulate_paths(S0, R, SIGMA, T, Z_path)
    assert paths.shape == (N_PATH, N_STEPS + 1)
    assert np.all(paths[:, 0] == S0)


def test_terminal_mean_is_martingale(Z_terminal):
    mean, se = mc_stats(simulate_terminal(S0, R, SIGMA, T, Z_terminal))
    assert abs((mean - S0 * np.exp(R * T)) / se) < 3

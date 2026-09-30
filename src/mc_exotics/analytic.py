"""Closed-form prices and Greeks (no dividends), used as references for the Monte Carlo results."""

import numpy as np
from scipy.stats import norm


def digital_call_analytic(S0, K, r, sigma, T):
    """Cash-or-nothing digital call: exp(-rT) N(d2)."""
    vol = sigma * np.sqrt(T)
    d2 = (np.log(S0 / K) + (r - 0.5 * sigma**2) * T) / vol
    return np.exp(-r * T) * norm.cdf(d2)


def digital_call_greeks(S0, K, r, sigma, T):
    """(delta, gamma, vega) of a cash-or-nothing digital call."""
    vol = sigma * np.sqrt(T)
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / vol
    d2 = d1 - vol
    base = np.exp(-r * T) * norm.pdf(d2)
    delta = base / (S0 * vol)
    gamma = -base * (d2 + vol) / (S0**2 * sigma**2 * T)
    vega = -base * d1 / sigma
    return delta, gamma, vega


def bs_call(S0, K, r, sigma, T):
    """Black-Scholes call price."""
    vol = sigma * np.sqrt(T)
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / vol
    return S0 * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d1 - vol)


def bs_call_greeks(S0, K, r, sigma, T):
    """(delta, gamma, vega) of a Black-Scholes call."""
    vol = sigma * np.sqrt(T)
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / vol
    delta = norm.cdf(d1)
    gamma = norm.pdf(d1) / (S0 * vol)
    vega = S0 * norm.pdf(d1) * np.sqrt(T)
    return delta, gamma, vega

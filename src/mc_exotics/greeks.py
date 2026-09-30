def fd_greeks(price_fn, spot, vol, Z, h_spot=3.0, h_vol=0.02):
    """Central-difference (delta, gamma, vega) of price_fn(spot, vol, Z).

    All five revaluations receive the same Z, so the estimator uses common random
    numbers and most of the Monte Carlo noise cancels in the differences.
    price_fn may return an array (several products); the Greeks are then arrays too.
    """
    base = price_fn(spot, vol, Z)
    up = price_fn(spot + h_spot, vol, Z)
    down = price_fn(spot - h_spot, vol, Z)
    vol_up = price_fn(spot, vol + h_vol, Z)
    vol_down = price_fn(spot, vol - h_vol, Z)

    delta = (up - down) / (2.0 * h_spot)
    gamma = (up - 2.0 * base + down) / h_spot**2
    vega = (vol_up - vol_down) / (2.0 * h_vol)
    return delta, gamma, vega

import numpy as np


def mc_stats(x):
    """Return (sample mean, standard error of the mean) of independent samples x."""
    x = np.asarray(x, dtype=float)
    return x.mean(), x.std(ddof=1) / np.sqrt(x.size)

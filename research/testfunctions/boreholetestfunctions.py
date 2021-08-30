import numpy as np

_dict = {
    'function':     'Borehole',
    'xdim':         2,
    'thetadim':     4,
    'c_structfail_high': 0.7,
    'c_structfail_low': 1.8,
    'p_randfail_high': 0.75,
    'p_randfail_low': 0.25
}


def query_func_meta():
    return _dict


def borehole_failmodel(x, theta, fail='low'):
    """Given x and theta, return matrix of [row x] times [row theta] of values."""
    if fail == 'high':
        c = _dict['c_structfail_high']
    else:
        c = _dict['c_structfail_low']

    f = borehole_model(x, theta)
    wheretoobig = np.where((f / borehole_true(x)) > c)
    f[wheretoobig[0], wheretoobig[1]] = np.nan

    return f


def borehole_failmodel_random(x, theta, fail='low'):
    if fail == 'high':
        p = _dict['p_randfail_high']
    else:
        p = _dict['p_randfail_low']

    f = borehole_model(x, theta)
    wheretoobig = np.where(np.random.choice([0, 1], f.shape, replace=True, p=[1-p, p]))
    f[wheretoobig[0], wheretoobig[1]] = np.nan

    return f


def borehole_model(x, theta):
    """Given x and theta, return matrix of [row x] times [row theta] of values."""

    theta = tstd2theta(theta)
    x = xstd2x(x)
    p = x.shape[0]
    n = theta.shape[0]

    theta_stacked = np.repeat(theta, repeats=p, axis=0)
    x_stacked = np.tile(x.astype(float), (n, 1))

    f = borehole_vec(x_stacked, theta_stacked).reshape((n, p))
    return f.T


def borehole_true(x):
    """Given x, return matrix of [row x] times 1 of values."""
    # assume true theta is [0.5]^d
    theta0 = np.atleast_2d(np.array([0.5] * 4))
    f0 = borehole_model(x, theta0)

    return f0


def borehole_vec(x, theta):
    """Given x and theta, return vector of values."""
    (Hu, Ld_Kw, Treff, powparam) = np.split(theta, theta.shape[1], axis=1)
    (rw,  Hl) = np.split(x, x.shape[1], axis=1)
    numer = 2 * np.pi *  (Hu - Hl)
    denom1 = 2 * Ld_Kw / rw ** 2
    denom2 = Treff

    f = ((numer / ((denom1 + denom2))) * np.exp(powparam * rw)).reshape(-1)

    return f



def tstd2theta(tstd, hard=True):
    """Given standardized theta in [0, 1]^d, return non-standardized theta."""
    if tstd.ndim < 1.5:
        tstd = tstd[:,None].T
    (Treffs, Hus, LdKw, powparams) = np.split(tstd, tstd.shape[1], axis=1)

    Treff = (0.5-0.05) * Treffs + 0.05
    Hu = Hus * (1110 - 990) + 990
    if hard:
        Ld_Kw = LdKw* (1680/1500 - 1120/15000) + 1120/15000
    else:
        Ld_Kw = LdKw*(1680/9855 - 1120/12045) + 1120/12045

    powparam = powparams * (0.5 - (- 0.5)) + (-0.5)

    theta = np.hstack((Hu, Ld_Kw, Treff, powparam))
    return theta


def xstd2x(xstd):
    """Given standardized x in [0, 1]^2 x {0, 1}, return non-standardized x."""
    if xstd.ndim < 1.5:
        xstd = xstd[:,None].T
    (rws, Hls) = np.split(xstd, xstd.shape[1], axis=1)

    rw = rws * (np.log(0.5) - np.log(0.05)) + np.log(0.05)
    rw = np.exp(rw)
    Hl = Hls * (820 - 700) + 700

    x = np.hstack((rw, Hl))
    return x

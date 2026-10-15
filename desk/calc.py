"""Standard calculations, each with a known-answer test in tests/test_calc.py.

Add a function here only when a study needs it, and add its test in the same commit: a case worked out
by hand, and where one exists, a figure published by an outside source.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from datetime import date

import numpy as np

# ---------------------------------------------------------------- returns


def simple_return(start: float, end: float) -> float:
    """end / start - 1."""
    if start <= 0:
        raise ValueError("start value must be positive")
    return end / start - 1


def cagr(start: float, end: float, years: float) -> float:
    """Compound annual growth rate: (end / start) ** (1 / years) - 1."""
    if start <= 0 or end < 0 or years <= 0:
        raise ValueError("cagr needs start > 0, end >= 0, years > 0")
    return (end / start) ** (1 / years) - 1


def xirr(flows: Sequence[tuple[date, float]], lo: float = -0.9999, hi: float = 100.0, tol: float = 1e-10) -> float:
    """Annualised internal rate of return for dated cash flows (money in negative, money out positive),
    Actual/365, found by bisection. Raises if the flows don't change sign."""
    if not flows:
        raise ValueError("no cash flows")
    t0 = min(d for d, _ in flows)
    ts = [((d - t0).days / 365.0, a) for d, a in flows]
    if not (any(a < 0 for _, a in ts) and any(a > 0 for _, a in ts)):
        raise ValueError("cash flows must include both signs")

    def npv(r: float) -> float:
        return sum(a / (1 + r) ** t for t, a in ts)

    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        raise ValueError("no root in the search range")
    for _ in range(300):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < tol or (hi - lo) < tol:
            return mid
        if f_lo * f_mid < 0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- inference


def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def welch(a: Sequence[float], b: Sequence[float]) -> dict:
    """Welch's t for a difference in means, with the normal-approximation two-sided p (fine for n > ~30 per
    group; say so if a group is smaller). Only for independent observations: never on overlapping windows."""
    a = np.asarray([x for x in a if x is not None and not math.isnan(x)], float)
    b = np.asarray([x for x in b if x is not None and not math.isnan(x)], float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    t = (a.mean() - b.mean()) / math.sqrt(va + vb)
    return {"n_a": len(a), "n_b": len(b), "mean_a": float(a.mean()), "mean_b": float(b.mean()),
            "diff": float(a.mean() - b.mean()), "t": float(t), "p": 2 * (1 - norm_cdf(abs(t)))}


def bootstrap_ci(x: Sequence[float], stat: Callable = np.median, n: int = 5000, level: float = 0.9,
                 seed: int = 7) -> tuple[float, float, float]:
    """(estimate, lo, hi): percentile bootstrap for independent observations."""
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    draws = np.array([stat(x[rng.integers(0, len(x), len(x))]) for _ in range(n)])
    a = (1 - level) / 2
    return float(stat(x)), float(np.quantile(draws, a)), float(np.quantile(draws, 1 - a))


def block_bootstrap_ci(x: Sequence[float], block: int, stat: Callable = np.mean, n: int = 5000,
                       level: float = 0.9, seed: int = 7) -> tuple[float, float, float]:
    """(estimate, lo, hi): moving-block bootstrap for a time-ordered series whose neighbours overlap or
    are correlated (rolling-window returns, monthly SIP starts). `block` should be at least the overlap
    length, e.g. the window in rows."""
    x = np.asarray(x, float)
    m = len(x)
    if block < 1 or block > m:
        raise ValueError("block must be between 1 and len(x)")
    rng = np.random.default_rng(seed)
    k = math.ceil(m / block)
    starts_max = m - block + 1
    draws = np.empty(n)
    for i in range(n):
        idx = (rng.integers(0, starts_max, k)[:, None] + np.arange(block)[None, :]).ravel()[:m]
        draws[i] = stat(x[idx])
    a = (1 - level) / 2
    return float(stat(x)), float(np.quantile(draws, a)), float(np.quantile(draws, 1 - a))


def independent_periods(n_rows: int, window: int) -> int:
    """How many non-overlapping windows fit in a series: the honest sample size for rolling-window results."""
    return n_rows // window


def holm(pvalues: dict[str, float], alpha: float = 0.05) -> dict[str, bool]:
    """Holm-Bonferroni: which hypotheses are rejected at family-wise level alpha."""
    order = sorted(pvalues, key=pvalues.get)
    m = len(order)
    out, still = {}, True
    for i, k in enumerate(order):
        still = still and pvalues[k] <= alpha / (m - i)
        out[k] = still
    return out

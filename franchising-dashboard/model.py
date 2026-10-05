"""Franchising performance equations from Sazwara's MSc thesis.

All performance and cost inputs use the same normalised units. N is an
outlet-scale parameter, as in the fractional-N appendix illustrations.
Effort is held fixed in sensitivity comparisons; it is not re-estimated.
"""
from dataclasses import asdict, dataclass, replace
from math import isfinite

import numpy as np

MODEL_NAMES = {
    "baseline": "1 · Constant overhead",
    "overhead": "2 · Endogenous overhead",
    "duplication": "3 · Overhead and duplication",
}


@dataclass(frozen=True)
class Parameters:
    pi: float = 1.0
    c_op: float = 0.35
    H: float = 0.35
    v: float = 0.15
    N: float = 1.0
    a: float = 0.5
    theta: float = 2.4
    delta: float = 0.10

    def __post_init__(self):
        for name, value in asdict(self).items():
            if not isfinite(value):
                raise ValueError(f"{name} must be finite.")
        for name in ("pi", "c_op", "H"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative.")
        for name in ("v", "a", "delta"):
            if not 0 <= getattr(self, name) <= 1:
                raise ValueError(f"{name} must be between 0 and 1.")
        if self.N <= 0 or self.theta <= 0:
            raise ValueError("N and theta must be positive.")

    @property
    def probability(self):
        return float(-np.expm1(-self.theta * self.a))

    @property
    def effort_cost(self):
        return 0.5 * self.a**2

    @property
    def franchise_payoff(self):
        return self.probability * self.pi - self.effort_cost

    @property
    def vN(self):
        return self.v * self.N


def coefficients(model: str, p: Parameters):
    """Return A, B, C such that P(F) = A + B*F + C*F**2."""
    q = p.franchise_payoff
    if model == "baseline":
        return p.pi - p.c_op, q - p.pi + p.c_op, 0.0
    if model not in MODEL_NAMES:
        raise ValueError(f"Unknown model: {model}")
    penalty = p.delta if model == "duplication" else 0.0
    return (p.pi - p.H - p.vN,
            -p.pi + p.H + 2*p.vN + q - penalty,
            penalty - p.vN)


def performance(F, model: str, p: Parameters):
    """Evaluate the thesis performance function on the closed interval [0, 1]."""
    f = np.asarray(F, dtype=float)
    if not np.all(np.isfinite(f)) or np.any((f < 0) | (f > 1)):
        raise ValueError("Franchising intensity must be finite and in [0, 1].")
    A, B, C = coefficients(model, p)
    return A + B*f + C*f*f


@dataclass(frozen=True)
class CurveSummary:
    shape: str
    maximum: float
    minimum: float
    maximisers: tuple
    minimisers: tuple
    stationary_share: float | None
    stationary_kind: str | None
    all_shares_tied: bool
    curvature: float


def summarise(model: str, p: Parameters):
    """Find global extrema analytically, including endpoints, ties and flatness.

    A stationary point of a convex quadratic is a minimum, so clipping its
    location to [0,1] is not a valid maximisation algorithm.
    """
    A, B, C = coefficients(model, p)
    tol = 1e-12 * max(1.0, abs(A), abs(B), abs(C))
    candidates = [0.0, 1.0]
    stationary, kind = None, None
    if abs(C) > tol:
        x = -B / (2*C)
        if 0 < x < 1:
            stationary = float(x)
            kind = "minimum" if C > 0 else "maximum"
            candidates.append(stationary)
    xs = np.array(candidates)
    ys = performance(xs, model, p)
    maximum, minimum = float(ys.max()), float(ys.min())
    maxima = tuple(float(x) for x, y in zip(xs, ys) if abs(y-maximum) <= tol)
    minima = tuple(float(x) for x, y in zip(xs, ys) if abs(y-minimum) <= tol)
    flat = abs(B) <= tol and abs(C) <= tol
    if flat:
        shape = "Flat: all shares perform equally"
    elif abs(C) <= tol:
        shape = "Linear, increasing" if B > 0 else "Linear, decreasing"
    elif stationary is not None:
        shape = "U-shaped: interior minimum" if C > 0 else "Inverted U: interior maximum"
    else:
        direction = "increasing" if performance(1, model, p) > performance(0, model, p) else "decreasing"
        shape = f"{'Convex' if C > 0 else 'Concave'}, {direction}"
    return CurveSummary(shape, maximum, minimum, maxima, minima, stationary,
                        kind, flat, 2*C)


def with_parameter(p: Parameters, name: str, value: float):
    """Change exactly one input; a vN sweep holds N fixed and changes v."""
    if name == "vN":
        return replace(p, v=value / p.N)
    if name not in asdict(p):
        raise ValueError(f"Unknown parameter: {name}")
    return replace(p, **{name: value})


# Demonstration values chosen for this app, not estimates from firm data.
PRESETS = {
    "Mixed ownership · inverted U": ("overhead", Parameters()),
    "Duplication costs · U shape": ("duplication", Parameters(delta=0.50)),
    "Franchising favoured · rising line": ("baseline", Parameters(c_op=0.55)),
    "Company operation favoured · falling line": ("baseline", Parameters(c_op=0.15)),
}

SWEEP_VALUES = {
    "H": [0.10, 0.35, 0.60, 0.90],
    "N": [0.30, 1.00, 2.00, 4.00],
    "v": [0.05, 0.15, 0.30, 0.60],
    "vN": [0.02, 0.08, 0.18, 0.32],
    "delta": [0.00, 0.05, 0.12, 0.20],
    "pi": [0.60, 0.80, 1.00, 1.20],
    "a": [0.20, 0.40, 0.60, 0.80],
    "theta": [1.00, 2.00, 3.00, 4.00],
    "c_op": [0.15, 0.30, 0.45, 0.60],
}

"""Shared helpers for the event-ideology map (change: map-event-ideology).

The color logic here is the single Python source of truth. Its constants are
also exported to ``color_params.json`` so the MapLibre frontend can mirror the
exact same scheme (Decision 4 in design.md): diverging blue-white-red on the
attendee-weighted mean lean, then blended toward gray in proportion to the
attendee-weighted standard deviation.
"""
from __future__ import annotations

import numpy as np

# --- Color endpoints (RGB 0-255). Mirrored verbatim in the JS frontend. ---
LEFT = (40, 90, 220)      # mean = -1  (blue)
CENTER = (245, 245, 245)  # mean =  0  (near-white)
RIGHT = (215, 45, 40)     # mean = +1  (red)
GRAY = (150, 150, 150)    # high-std target (battleground / no clear signal)
GRAYING_CAP = 0.85        # max blend toward gray (keeps dots visible)


def weighted_mean_std(values, weights):
    """Attendee-weighted mean and (population) std of ``values``.

    Weights are ``n_political``. A single-event location has std 0.0.
    """
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    w = weights.sum()
    if w == 0:
        return float("nan"), 0.0
    mean = float((values * weights).sum() / w)
    var = float((weights * (values - mean) ** 2).sum() / w)
    return mean, float(np.sqrt(max(var, 0.0)))


def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def bivariate_color(mean, std, s_ref, graying_cap=GRAYING_CAP):
    """Return an (r, g, b) 0-255 tuple for a location.

    1. mean -> diverging blue-white-red
    2. blend toward GRAY by clamp(std / s_ref, 0, 1) * graying_cap
    """
    if mean < 0:
        base = _lerp(CENTER, LEFT, min(-mean, 1.0))
    else:
        base = _lerp(CENTER, RIGHT, min(mean, 1.0))
    g = min(std / s_ref, 1.0) * graying_cap if s_ref > 0 else 0.0
    r, gr, b = _lerp(base, GRAY, g)
    return (round(r), round(gr), round(b))


def color_params(s_ref):
    """Serializable parameter bundle shared with the frontend."""
    return {
        "scheme": "diverging-blue-white-red + graying-by-std",
        "left_rgb": list(LEFT),
        "center_rgb": list(CENTER),
        "right_rgb": list(RIGHT),
        "gray_rgb": list(GRAY),
        "graying_cap": GRAYING_CAP,
        "s_ref": float(s_ref),
        "mean_field": "average_normalized",
        "weight_field": "n_political",
        "opacity_field": "percent_political",
    }

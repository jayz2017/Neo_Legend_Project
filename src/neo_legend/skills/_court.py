"""Basketball court drawing helpers."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle
import numpy as np

from neo_legend.skills._plotting import seeded_rng


def draw_half_court(
    ax: plt.Axes,
    *,
    line_color: str = "#f3f1e8",
    line_width: float = 1.2,
    alpha: float = 0.78,
) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(-250, 250)
    ax.set_ylim(-20, 470)
    ax.set_axis_off()

    court_patches = [
        Rectangle((-250, 0), 500, 470, fill=False),
        Rectangle((-80, 0), 160, 190, fill=False),
        Rectangle((-60, 0), 120, 190, fill=False),
        Circle((0, 52.5), 7.5, fill=False),
        Circle((0, 52.5), 2.5, fill=True, color=line_color, alpha=alpha),
        Arc((0, 190), 120, 120, theta1=0, theta2=180),
        Arc((0, 190), 120, 120, theta1=180, theta2=360, linestyle="dashed"),
        Arc((0, 52.5), 475, 475, theta1=22, theta2=158),
        Arc((0, 422.5), 120, 120, theta1=180, theta2=360),
    ]

    for patch in court_patches:
        patch.set_edgecolor(line_color)
        patch.set_linewidth(line_width)
        patch.set_alpha(alpha)
        ax.add_patch(patch)

    ax.plot([-30, 30], [40, 40], color=line_color, lw=line_width * 2.5, alpha=alpha)
    ax.plot([-220, -220], [0, 140], color=line_color, lw=line_width, alpha=alpha)
    ax.plot([220, 220], [0, 140], color=line_color, lw=line_width, alpha=alpha)
    ax.plot([-250, 250], [0, 0], color=line_color, lw=line_width, alpha=alpha)


def sample_shots(seed: int = 7, count: int = 520) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = seeded_rng(seed)
    rim_count = count // 3
    wing_count = count // 3
    arc_count = count - rim_count - wing_count

    rim_x = rng.normal(0, 45, rim_count)
    rim_y = rng.normal(78, 45, rim_count)

    wing_angles = rng.uniform(np.deg2rad(35), np.deg2rad(145), wing_count)
    wing_radius = rng.normal(235, 24, wing_count)
    wing_x = wing_radius * np.cos(wing_angles)
    wing_y = 52.5 + wing_radius * np.sin(wing_angles)

    arc_x = rng.choice([-1, 1], arc_count) * rng.normal(165, 35, arc_count)
    arc_y = rng.normal(245, 72, arc_count)

    x = np.clip(np.concatenate([rim_x, wing_x, arc_x]), -235, 235)
    y = np.clip(np.concatenate([rim_y, wing_y, arc_y]), 8, 435)
    value = np.sin(x / 48) + np.cos(y / 70) + rng.normal(0, 0.42, count)
    return x, y, value

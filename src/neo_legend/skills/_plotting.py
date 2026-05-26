"""Shared Matplotlib helpers for render skills."""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_hex
from matplotlib.figure import Figure
import numpy as np

DPI = 100


def create_figure(width: int, height: int, background: str) -> Figure:
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI, facecolor=background)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return fig


def add_canvas(fig: Figure) -> plt.Axes:
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    return ax


def save_png(fig: Figure) -> bytes:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=fig.dpi, facecolor=fig.get_facecolor(), pad_inches=0)
    plt.close(fig)
    return buffer.getvalue()


def make_gradient(colors: Iterable[str], name: str) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list(name, list(colors))


def cmap_color(colors: list[str], value: float) -> str:
    cmap = make_gradient(colors, "local_gradient")
    return to_hex(cmap(float(np.clip(value, 0, 1))))


def seeded_rng(seed: int = 2026) -> np.random.Generator:
    return np.random.default_rng(seed)


def add_reference_footer(canvas: plt.Axes, text: str, color: str = "#d6d6d6") -> None:
    canvas.text(
        0.5,
        0.025,
        text,
        color=color,
        fontsize=11,
        ha="center",
        va="center",
        alpha=0.72,
        fontweight="bold",
    )

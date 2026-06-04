from __future__ import annotations

"""Shared commercial report styling helpers for chart renderers."""


from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_hex, to_rgb
from matplotlib.patches import FancyBboxPatch, Rectangle


@dataclass(frozen=True)
class ReportTheme:
    name: str
    background: str
    background_alt: str
    panel: str
    panel_alt: str
    text: str
    muted: str
    grid: str
    border: str
    primary: str
    secondary: str
    accent: str
    good: str
    bad: str
    palette: tuple[str, ...]
    dark: bool = True


@dataclass(frozen=True)
class ReportText:
    title: str
    subtitle: str | None
    kicker: str
    theme_label: str | None
    footer: str


REPORT_THEMES: dict[str, ReportTheme] = {
    "midnight": ReportTheme(
        name="Midnight Boardroom",
        background="#070a12",
        background_alt="#101827",
        panel="#0f1724",
        panel_alt="#162033",
        text="#f8fafc",
        muted="#93a4b8",
        grid="#2b3b52",
        border="#31445f",
        primary="#36d5ff",
        secondary="#b86bff",
        accent="#f6d365",
        good="#58d68d",
        bad="#ff647c",
        palette=("#36d5ff", "#b86bff", "#f6d365", "#58d68d", "#ff647c", "#7dd3fc"),
    ),
    "champagne": ReportTheme(
        name="Champagne Ledger",
        background="#f7f2e8",
        background_alt="#efe4d1",
        panel="#fffaf2",
        panel_alt="#f4eadb",
        text="#172033",
        muted="#667085",
        grid="#d8cdbc",
        border="#c7b69e",
        primary="#b88746",
        secondary="#1f6f8b",
        accent="#9c3d54",
        good="#2f8f6b",
        bad="#b54755",
        palette=("#b88746", "#1f6f8b", "#9c3d54", "#2f8f6b", "#6b5b95", "#d49a6a"),
        dark=False,
    ),
    "sapphire": ReportTheme(
        name="Sapphire Executive",
        background="#06141f",
        background_alt="#0b2433",
        panel="#0d2433",
        panel_alt="#123449",
        text="#edf7fb",
        muted="#8fb5c6",
        grid="#244c61",
        border="#2d6278",
        primary="#4cc9f0",
        secondary="#7ae582",
        accent="#ffb703",
        good="#80ed99",
        bad="#ff5d73",
        palette=("#4cc9f0", "#7ae582", "#ffb703", "#f72585", "#b8f2e6", "#6c63ff"),
    ),
    "imperial": ReportTheme(
        name="Imperial Portfolio",
        background="#080705",
        background_alt="#17110c",
        panel="#15100c",
        panel_alt="#21170f",
        text="#fff8e7",
        muted="#b9aa8a",
        grid="#463920",
        border="#6c5426",
        primary="#d6a84f",
        secondary="#8ecae6",
        accent="#d1495b",
        good="#7bc47f",
        bad="#d95d39",
        palette=("#d6a84f", "#8ecae6", "#d1495b", "#7bc47f", "#e9c46a", "#b5838d"),
    ),
    "aurora": ReportTheme(
        name="Aurora Capital",
        background="#0b1020",
        background_alt="#161336",
        panel="#121a2d",
        panel_alt="#1d2440",
        text="#f4f7ff",
        muted="#a5aec8",
        grid="#2f385a",
        border="#4a5a86",
        primary="#00f5d4",
        secondary="#f15bb5",
        accent="#fee440",
        good="#00bb7e",
        bad="#ff5a5f",
        palette=("#00f5d4", "#f15bb5", "#fee440", "#9b5de5", "#00bbf9", "#ff6b6b"),
    ),
}


STYLE_THEME_MAP: dict[str, str] = {
    "neon_glow": "midnight",
    "crystal_metal": "champagne",
    "gradient_rainbow": "aurora",
    "versus_battle": "midnight",
    "mirror_compare": "champagne",
    "evolution_track": "sapphire",
    "glass_3d": "midnight",
    "neon_tubes": "aurora",
    "gradient_sky": "champagne",
    "crystal_pillars": "imperial",
    "crystal_stream": "midnight",
    "neon_pulse": "aurora",
    "sunset_gradient": "champagne",
    "ocean_depths": "sapphire",
    "water_drops": "sapphire",
    "fireflies": "midnight",
    "galaxy_stars": "aurora",
    "crystal_orbs": "imperial",
    "neon_streams": "aurora",
    "energy_flow": "sapphire",
    "crystal_rivers": "champagne",
    "golden_paths": "imperial",
    "executive_trend": "midnight",
    "champagne_forecast": "champagne",
    "aurora_stream": "aurora",
    "executive_month": "midnight",
    "earnings_calendar": "champagne",
    "correlation_board": "sapphire",
    "risk_heat_matrix": "champagne",
    "capital_flows": "imperial",
    "sector_rotation": "midnight",
    "macro_quadrants": "midnight",
    "portfolio_pairs": "champagne",
    "wall_street_stack": "midnight",
    "portfolio_stack": "champagne",
}


def resolve_report_theme(data: dict[str, Any], style: str, default: str = "midnight") -> ReportTheme:
    requested = str(data.get("report_theme") or data.get("color_theme") or "").strip().lower()
    if requested == "random":
        seed_text = str(data.get("report_theme_seed") or data.get("color_theme_seed") or style)
        index = sum(ord(ch) for ch in seed_text) % len(REPORT_THEMES)
        return list(REPORT_THEMES.values())[index]
    if requested in REPORT_THEMES:
        return REPORT_THEMES[requested]
    return REPORT_THEMES[STYLE_THEME_MAP.get(style, default)]


def resolve_report_text(
    data: dict[str, Any],
    request_title: str | None,
    request_subtitle: str | None,
    *,
    default_title: str,
    default_subtitle: str | None,
    default_kicker: str,
    default_footer: str,
) -> ReportText:
    """Resolve configurable header text from request fields and data payload."""

    sources = _report_text_sources(data)
    title = request_title or _first_text(sources, "title", "report_title", "header_title") or default_title
    subtitle = (
        request_subtitle
        if request_subtitle is not None
        else _first_text(sources, "subtitle", "report_subtitle", "header_subtitle") or default_subtitle
    )
    kicker = (
        _first_text(
            sources,
            "kicker",
            "eyebrow",
            "report_kicker",
            "header_kicker",
            "section_label",
        )
        or default_kicker
    )
    theme_label = _first_text(
        sources,
        "theme_label",
        "report_theme_label",
        "header_theme_label",
        "right_label",
        "brand_label",
    )
    footer = _first_text(sources, "footer", "footer_text", "report_footer") or default_footer
    return ReportText(
        title=title,
        subtitle=subtitle,
        kicker=kicker,
        theme_label=theme_label,
        footer=footer,
    )


def _report_text_sources(data: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for key in ("report_header", "header", "header_text"):
        value = data.get(key)
        if isinstance(value, dict):
            sources.append(value)
    sources.append(data)
    return sources


def _first_text(sources: list[dict[str, Any]], *keys: str) -> str | None:
    for source in sources:
        for key in keys:
            value = source.get(key)
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
    return None


def blend(color_a: str, color_b: str, amount: float) -> str:
    rgb_a = np.array(to_rgb(color_a), dtype=float)
    rgb_b = np.array(to_rgb(color_b), dtype=float)
    rgb = rgb_a + (rgb_b - rgb_a) * float(np.clip(amount, 0.0, 1.0))
    return to_hex(rgb)


def lighten(color: str, amount: float) -> str:
    return blend(color, "#ffffff", amount)


def darken(color: str, amount: float) -> str:
    return blend(color, "#000000", amount)


def format_metric(value: float) -> str:
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 10_000:
        return f"{value / 1_000:.1f}K"
    if abs(value) >= 100:
        return f"{value:,.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def draw_report_background(canvas: plt.Axes, theme: ReportTheme) -> None:
    canvas.set_facecolor(theme.background)
    for idx in range(48):
        y0 = idx / 48
        amount = idx / 47
        color = blend(theme.background, theme.background_alt, amount * 0.55)
        canvas.add_patch(Rectangle((0, y0), 1, 1 / 48, facecolor=color, edgecolor="none", zorder=-20))

    band_color = blend(theme.background_alt, theme.panel, 0.35)
    canvas.add_patch(Rectangle((0, 0.86), 1, 0.14, facecolor=band_color, edgecolor="none", alpha=0.62, zorder=-19))
    canvas.add_patch(Rectangle((0, 0), 1, 0.055, facecolor=band_color, edgecolor="none", alpha=0.38, zorder=-19))

    line_color = theme.border if theme.dark else blend(theme.border, theme.background, 0.35)
    for x in np.linspace(0.08, 0.92, 8):
        canvas.plot([x, x + 0.045], [0.055, 0.055], color=line_color, lw=0.8, alpha=0.18)
    for y in (0.86, 0.055):
        canvas.plot([0.055, 0.945], [y, y], color=line_color, lw=1.0, alpha=0.34)


def draw_report_header(
    canvas: plt.Axes,
    theme: ReportTheme,
    title: str,
    subtitle: str | None,
    kicker: str,
    *,
    theme_label: str | None = None,
) -> None:
    canvas.text(
        0.065,
        0.945,
        kicker.upper(),
        color=theme.accent,
        fontsize=10,
        fontweight="bold",
        ha="left",
        va="center",
        alpha=0.92,
    )
    canvas.text(
        0.065,
        0.905,
        title,
        color=theme.text,
        fontsize=34,
        fontweight="black",
        ha="left",
        va="center",
    )
    if subtitle:
        canvas.text(
            0.065,
            0.865,
            subtitle,
            color=theme.muted,
            fontsize=13,
            fontweight="semibold",
            ha="left",
            va="center",
        )

    right_label = theme_label or theme.name
    if right_label:
        canvas.text(
            0.935,
            0.914,
            right_label.upper(),
            color=theme.muted,
            fontsize=10,
            fontweight="bold",
            ha="right",
            va="center",
            alpha=0.75,
        )
    canvas.plot([0.065, 0.29], [0.835, 0.835], color=theme.primary, lw=3.0, alpha=0.92)
    canvas.plot([0.30, 0.47], [0.835, 0.835], color=theme.accent, lw=3.0, alpha=0.68)


def draw_panel_frame(canvas: plt.Axes, rect: tuple[float, float, float, float], theme: ReportTheme) -> None:
    x, y, w, h = rect
    shadow_color = "#000000" if theme.dark else "#b8aa99"
    canvas.add_patch(
        FancyBboxPatch(
            (x + 0.006, y - 0.008),
            w,
            h,
            boxstyle="round,pad=0.010,rounding_size=0.018",
            facecolor=shadow_color,
            edgecolor="none",
            alpha=0.18,
            zorder=-7,
        )
    )
    canvas.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.010,rounding_size=0.018",
            facecolor=theme.panel,
            edgecolor=theme.border,
            linewidth=1.1,
            alpha=0.94,
            zorder=-6,
        )
    )


def add_report_axes(
    fig: plt.Figure,
    canvas: plt.Axes,
    rect: tuple[float, float, float, float],
    theme: ReportTheme,
    *,
    polar: bool = False,
) -> plt.Axes:
    draw_panel_frame(canvas, rect, theme)
    if polar:
        ax = fig.add_axes(rect, projection="polar", facecolor=theme.panel)
    else:
        ax = fig.add_axes(rect, facecolor=theme.panel)
    return ax


def style_cartesian_axes(
    ax: plt.Axes,
    theme: ReportTheme,
    *,
    xlabel: str = "",
    ylabel: str = "",
    x_rotation: int = 0,
) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(theme.border)
    ax.spines["bottom"].set_color(theme.border)
    ax.spines["left"].set_linewidth(1.0)
    ax.spines["bottom"].set_linewidth(1.0)
    ax.tick_params(axis="both", colors=theme.muted, labelsize=10, length=0)
    ax.grid(axis="y", color=theme.grid, linewidth=0.8, alpha=0.44)
    ax.set_axisbelow(True)
    ax.set_xlabel(xlabel, color=theme.muted, fontsize=11, fontweight="bold", labelpad=10)
    ax.set_ylabel(ylabel, color=theme.muted, fontsize=11, fontweight="bold", labelpad=10)
    for label in ax.get_xticklabels():
        label.set_rotation(x_rotation)
        label.set_ha("right" if x_rotation else "center")


def draw_kpi_strip(
    canvas: plt.Axes,
    theme: ReportTheme,
    items: list[tuple[str, str, str]],
    *,
    y: float = 0.775,
) -> None:
    if not items:
        return
    max_items = min(len(items), 4)
    width = 0.20
    gap = 0.015
    start_x = 0.065
    for idx, (label, value, color) in enumerate(items[:max_items]):
        x = start_x + idx * (width + gap)
        canvas.add_patch(
            FancyBboxPatch(
                (x, y - 0.039),
                width,
                0.072,
                boxstyle="round,pad=0.008,rounding_size=0.012",
                facecolor=theme.panel_alt,
                edgecolor=blend(color, theme.border, 0.55),
                linewidth=0.9,
                alpha=0.88,
            )
        )
        canvas.text(x + 0.014, y + 0.015, label.upper(), color=theme.muted, fontsize=8, fontweight="bold", ha="left")
        canvas.text(x + 0.014, y - 0.014, value, color=color, fontsize=18, fontweight="black", ha="left", va="center")


def draw_series_legend(
    canvas: plt.Axes,
    theme: ReportTheme,
    items: list[tuple[str, str]],
    *,
    y: float = 0.095,
    x: float = 0.5,
) -> None:
    if not items:
        return
    total = min(0.74, max(0.22, len(items) * 0.17))
    start = x - total / 2
    canvas.add_patch(
        FancyBboxPatch(
            (start - 0.018, y - 0.026),
            total + 0.036,
            0.052,
            boxstyle="round,pad=0.006,rounding_size=0.012",
            facecolor=theme.panel_alt,
            edgecolor=theme.border,
            linewidth=0.8,
            alpha=0.84,
        )
    )
    spacing = total / max(len(items), 1)
    for idx, (label, color) in enumerate(items):
        lx = start + idx * spacing + 0.018
        canvas.plot([lx, lx + 0.030], [y, y], color=color, lw=4, solid_capstyle="round")
        canvas.text(lx + 0.040, y, label, color=theme.text, fontsize=10, fontweight="bold", ha="left", va="center")


def add_footer(canvas: plt.Axes, theme: ReportTheme, text: str = "NEO LEGEND | COMMERCIAL REPORT VISUAL") -> None:
    canvas.text(0.065, 0.029, text, color=theme.muted, fontsize=9, fontweight="bold", ha="left", alpha=0.72)


def value_range(values: np.ndarray, pad_ratio: float = 0.12) -> tuple[float, float]:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return 0.0, 1.0
    vmin = float(np.min(finite))
    vmax = float(np.max(finite))
    if np.isclose(vmin, vmax):
        pad = max(abs(vmax) * 0.1, 1.0)
        return vmin - pad, vmax + pad
    pad = (vmax - vmin) * pad_ratio
    if vmin >= 0:
        return 0.0, vmax + pad
    return vmin - pad, vmax + pad


def gradient_colors(start: str, end: str, steps: int) -> list[str]:
    return [blend(start, end, i / max(steps - 1, 1)) for i in range(max(steps, 1))]

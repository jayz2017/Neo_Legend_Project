"""Total Points By Location hex-bin heatmap renderer skill."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._court import draw_half_court, sample_shots
from neo_legend._plotting import add_canvas, create_figure, make_gradient, save_png
from neo_legend.base import BaseLegendSkill, StyleDefinition


class PointsLocationSkill(BaseLegendSkill):
    legend_type = "points_location"
    display_name = "Total Points By Location"
    default_style = "default"
    default_size = (1179, 1454)
    style_definitions = (
        StyleDefinition("default", "Cyan hex-bin points location heatmap.", ("0ece60f1e357e60d332c2983bac940dd.jpg",)),
        StyleDefinition("warm_gradient", "Warm orange-red gradient alternative."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        content = self._render_png(request, style, width, height)
        return self.result(content, style)

    def _render_png(self, request: RenderRequest, style: str, width: int, height: int) -> bytes:
        bg_color = "#0a1929"
        fig = create_figure(width, height, bg_color)
        canvas = add_canvas(fig)
        title_text = request.title or "TOTAL POINTS BY LOCATION"
        subtitle_text = request.subtitle or "2020-21 Season | By @KirkGoldsberry"

        canvas.text(
            0.5,
            0.905,
            title_text,
            color="#ffffff",
            fontsize=52,
            fontweight="bold",
            ha="center",
            va="center",
        )
        canvas.text(
            0.5,
            0.855,
            subtitle_text,
            color="#8899aa",
            fontsize=18,
            fontweight="bold",
            ha="center",
            va="center",
        )

        court_ax = fig.add_axes([0.06, 0.12, 0.88, 0.58], facecolor=bg_color)
        draw_half_court(court_ax, line_color="#c8d6e5", line_width=1.1, alpha=0.7)

        custom_shots = request.data.get("shots")
        if custom_shots:
            x_arr = np.array([s["x"] for s in custom_shots])
            y_arr = np.array([s["y"] for s in custom_shots])
            value_arr = np.array([s.get("points", 1.0) for s in custom_shots])
        else:
            seed = int(request.data.get("seed", 42))
            count = int(request.data.get("count", 800))
            x_arr, y_arr, value_arr = sample_shots(seed=seed, count=count)

        if style == "default":
            cmap = make_gradient(["#0d3b4c", "#1a5f7a", "#57c4b4", "#a8e6cf"], "cyan_heat")
            hex_colors = ["#0d3b4c", "#1a5f7a", "#57c4b4", "#a8e6cf"]
        else:
            cmap = make_gradient(["#4a1c00", "#b84a00", "#ff6b35", "#ffb347"], "warm_heat")
            hex_colors = ["#4a1c00", "#b84a00", "#ff6b35", "#ffb347"]

        court_ax.hexbin(
            x_arr,
            y_arr,
            C=value_arr,
            reduce_C_function=np.sum,
            gridsize=28,
            extent=(-250, 250, 0, 470),
            mincnt=1,
            cmap=cmap,
            linewidths=0.25,
            edgecolors="#1a2a3a",
            alpha=0.88,
        )

        self._draw_color_legend(canvas, hex_colors)
        self._draw_brand_badge(canvas)
        return save_png(fig)

    @staticmethod
    def _draw_color_legend(canvas: plt.Axes, colors: list[str]) -> None:
        labels = [
            ("Less Than 200", colors[0]),
            ("200-400", colors[1]),
            ("400-600", colors[2]),
            ("600-800", colors[3]),
            ("More Than 800", colors[3]),
        ]
        n = len(labels)
        start_x = 0.13
        spacing = 0.74 / max(n - 1, 1)
        base_y = 0.072

        for i, (label, color) in enumerate(labels):
            cx = start_x + i * spacing
            canvas.plot(cx, base_y, marker="h", markersize=11, color=color, markeredgecolor="#ffffff", markeredgewidth=0.45)
            canvas.text(cx, base_y - 0.032, label, color="#99aabb", fontsize=10, ha="center", va="top", fontweight="bold")

    @staticmethod
    def _draw_brand_badge(canvas: plt.Axes) -> None:
        circle = plt.Circle((0.065, 0.04), 0.028, facecolor="#000000", edgecolor="#333344", linewidth=0.8, transform=canvas.transAxes, clip_on=False)
        canvas.add_patch(circle)
        canvas.text(0.065, 0.04, "BU", color="#ffffff", fontsize=8, fontweight="bold", ha="center", va="center")
        canvas.text(0.105, 0.04, "BASKETBALL UNIVERSE", color="#778899", fontsize=9, fontweight="bold", ha="left", va="center")
        canvas.text(0.295, 0.04, "\u2665", color="#ff6b9d", fontsize=14, ha="center", va="center")

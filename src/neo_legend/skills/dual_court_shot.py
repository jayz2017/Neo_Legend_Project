"""Dual court comparison renderer skill."""

from __future__ import annotations

from typing import Any

import numpy as np

from neo_legend.models import RenderRequest, RenderResult
from neo_legend.skills._court import draw_half_court, sample_shots
from neo_legend.skills._plotting import add_canvas, create_figure, make_gradient, save_png
from neo_legend.skills.base import BaseLegendSkill, StyleDefinition


class DualCourtShotSkill(BaseLegendSkill):
    legend_type = "dual_court_shot"
    display_name = "Dual Court Shooting Comparison"
    default_style = "year_over_year"
    default_size = (1179, 1471)
    style_definitions = (
        StyleDefinition(
            "year_over_year",
            "Two stacked half-court shot maps with headline metrics.",
            ("3c1084f8f059bd51ab35a52c527d08f5.jpg",),
        ),
        StyleDefinition("split_hex", "Two stacked hex-density courts with bolder color contrast."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        fig = create_figure(width, height, "#030404")
        canvas = add_canvas(fig)

        canvas.text(
            0.52,
            0.94,
            (request.title or "JADEN MCDANIELS").upper(),
            color="#f8f7ee",
            fontsize=44,
            fontweight="black",
            ha="center",
        )
        canvas.text(
            0.52,
            0.895,
            (request.subtitle or "MINNESOTA TIMBERWOLVES / YEAR OVER YEAR").upper(),
            color="#c7c4bd",
            fontsize=16,
            fontweight="bold",
            ha="center",
        )
        canvas.plot([0.06, 0.94], [0.872, 0.872], color="#aa9f73", lw=1, alpha=0.6)

        panels = self._panels(request.data)
        self._draw_panel(fig, canvas, 0.535, panels[0], style)
        self._draw_panel(fig, canvas, 0.09, panels[1], style)

        canvas.text(
            0.88,
            0.032,
            "FG% VS. LEAGUE BY ZONE",
            color="#f2f1e8",
            fontsize=11,
            fontweight="bold",
            ha="center",
        )
        canvas.text(0.06, 0.032, "@KIRKGOLDSBERRY", color="#f2f1e8", fontsize=11, ha="left")
        return self.result(save_png(fig), style)

    @staticmethod
    def _draw_panel(
        fig,
        canvas,
        bottom: float,
        panel: dict[str, Any],
        style: str,
    ) -> None:
        season = str(panel.get("season", "2024-25"))
        attempts = str(panel.get("attempts", "79 GAMES / 808 ATTEMPTS"))
        seed = int(panel.get("seed", 12))
        canvas.text(0.05, bottom + 0.33, season, color="#f4f3ec", fontsize=28, fontweight="black")
        canvas.text(0.05, bottom + 0.305, attempts, color="#d2cec9", fontsize=10, fontweight="bold")

        metric_x = [0.66, 0.78, 0.91]
        metric_labels = ["FG%", "3P%", "eFG%"]
        metrics = panel.get("metrics") if isinstance(panel.get("metrics"), dict) else {}
        metric_values = [str(metrics.get(label, "")) for label in metric_labels]
        if not all(metric_values):
            metric_values = ["47.6%", "33.2%", "53.7%"] if seed == 12 else ["51.8%", "42.0%", "58.4%"]
        for x_pos, label, value in zip(metric_x, metric_labels, metric_values, strict=True):
            canvas.text(x_pos, bottom + 0.335, label, color="#e6dcc0", fontsize=9, ha="center")
            canvas.text(
                x_pos,
                bottom + 0.306,
                value,
                color="#f6f5ec",
                fontsize=22,
                fontweight="black",
                ha="center",
            )

        if seed != 12:
            canvas.text(
                0.12,
                bottom + 0.17,
                "MOST\nIMPROVED",
                color="#e8fff0",
                fontsize=13,
                ha="center",
                va="center",
                bbox={"boxstyle": "round,pad=0.7", "facecolor": "#2db84d", "edgecolor": "none"},
            )

        court_ax = fig.add_axes([0.14, bottom, 0.72, 0.31], facecolor="#030404")
        draw_half_court(court_ax, line_color="#f1eee5", line_width=1.0, alpha=0.74)
        x, y, value = sample_shots(seed=seed, count=500)
        if style == "split_hex":
            cmap = make_gradient(["#50a0d8", "#fff8cf", "#ef243a"], "split_hex")
            court_ax.scatter(x, y, c=value, cmap=cmap, s=32, marker="h", alpha=0.88, lw=0)
        else:
            sizes = np.interp(value, (value.min(), value.max()), (9, 48))
            colors = np.where(value > 0.5, "#f8f7d4", np.where(value < -0.5, "#e5273f", "#77bde5"))
            court_ax.scatter(x, y, s=sizes, c=colors, alpha=0.86, lw=0)

        for label, px, py in [("31%", -205, 22), ("42%", 170, 345), ("53%", -145, 195), ("60%", 45, 55)]:
            court_ax.text(px, py, label, color="#f5f3eb", fontsize=12, fontweight="bold")

    @staticmethod
    def _panels(data: dict[str, Any]) -> list[dict[str, Any]]:
        panels = data.get("panels")
        if isinstance(panels, list):
            valid_panels = [panel for panel in panels if isinstance(panel, dict)]
            if len(valid_panels) >= 2:
                return valid_panels[:2]
        return [
            {
                "season": "2024-25",
                "attempts": "79 GAMES / 808 ATTEMPTS",
                "seed": 12,
                "metrics": {"FG%": "47.6%", "3P%": "33.2%", "eFG%": "53.7%"},
            },
            {
                "season": "2025-26",
                "attempts": "71 GAMES / 774 ATTEMPTS",
                "seed": 44,
                "metrics": {"FG%": "51.8%", "3P%": "42.0%", "eFG%": "58.4%"},
            },
        ]

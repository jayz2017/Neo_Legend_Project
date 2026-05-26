"""Heatmap table renderer skill."""

from __future__ import annotations

from typing import Any

from matplotlib.patches import Circle, Rectangle

from neo_legend.models import RenderRequest, RenderResult
from neo_legend.skills._plotting import add_canvas, cmap_color, create_figure, save_png
from neo_legend.skills.base import BaseLegendSkill, StyleDefinition


class TableSkill(BaseLegendSkill):
    legend_type = "table"
    display_name = "Heatmap Ranking Table"
    default_style = "heatmap_light"
    default_size = (1179, 1481)
    style_definitions = (
        StyleDefinition(
            "heatmap_light",
            "White-background ranking table with heat colored stat cells.",
            (
                "fe96ef95bd423017d90a51b1b8b2e445.jpg",
                "a1cb23fc1b0420d211ffc5ad48ba5034.jpg",
            ),
        ),
        StyleDefinition("scoreboard_dark", "Dark scoreboard-style table with high-contrast cells."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        background = "#ffffff" if style == "heatmap_light" else "#080a0d"
        text_color = "#050505" if style == "heatmap_light" else "#f6f6f0"
        fig = create_figure(width, height, background)
        canvas = add_canvas(fig)

        canvas.text(
            0.08,
            0.94,
            (request.title or "LEADERS IN POINTS CREATED").upper(),
            color=text_color,
            fontsize=40,
            fontweight="black",
            ha="left",
        )
        canvas.text(
            0.08,
            0.895,
            (request.subtitle or "PLAYOFFS").upper(),
            color="#7a7a7a" if style == "heatmap_light" else "#bdbdbd",
            fontsize=36,
            fontweight="black",
            ha="left",
        )

        rows = self._rows(request.data)
        columns = ["PTS\nCREATED", "TS%", "AST/\nTOV", "MPG"]
        table_left = 0.09
        table_top = 0.82
        row_h = 0.047
        logo_w = 0.08
        name_w = 0.30
        cell_w = 0.115

        canvas.text(
            table_left + logo_w + 0.03,
            table_top + 0.025,
            "Name",
            color=text_color,
            fontsize=21,
            fontweight="bold",
        )
        for idx, col in enumerate(columns):
            canvas.text(
                table_left + logo_w + name_w + cell_w * idx + cell_w / 2,
                table_top + 0.025,
                col,
                color=text_color,
                fontsize=19,
                fontweight="bold",
                ha="center",
            )

        for row_idx, row in enumerate(rows):
            y = table_top - row_h * (row_idx + 1)
            line_color = "#dedede" if style == "heatmap_light" else "#242a33"
            canvas.plot(
                [table_left, table_left + logo_w + name_w + cell_w * len(columns)],
                [y, y],
                color=line_color,
                lw=0.8,
            )
            self._draw_logo(canvas, table_left + 0.035, y + row_h / 2, row["team"], row["team_color"])
            canvas.text(
                table_left + logo_w + 0.03,
                y + row_h / 2,
                row["name"],
                color=text_color,
                fontsize=22,
                va="center",
                ha="left",
            )
            values = [row["pts_created"], row["ts"], row["ast_tov"], row["mpg"]]
            for col_idx, value in enumerate(values):
                x = table_left + logo_w + name_w + cell_w * col_idx
                fill = self._cell_color(col_idx, float(value), style)
                canvas.add_patch(Rectangle((x, y), cell_w, row_h, facecolor=fill, edgecolor=line_color, lw=0.7))
                suffix = "%" if col_idx == 1 else ""
                canvas.text(
                    x + cell_w / 2,
                    y + row_h / 2,
                    f"{value:.1f}{suffix}" if col_idx != 1 else f"{value:.0f}{suffix}",
                    color="#050505" if style == "heatmap_light" else "#ffffff",
                    fontsize=21,
                    fontweight="bold" if col_idx == 0 else "normal",
                    ha="center",
                    va="center",
                )

        footer_color = "#777777" if style == "heatmap_light" else "#b0b0b0"
        canvas.text(0.09, 0.045, "Data via generated sample set", color=footer_color, fontsize=18, ha="left")
        canvas.text(0.72, 0.045, "Neo Legend", color="#29b98f", fontsize=34, fontweight="black", ha="left")
        return self.result(save_png(fig), style)

    @staticmethod
    def _draw_logo(canvas, x: float, y: float, label: str, color: str) -> None:
        canvas.add_patch(Circle((x, y), 0.018, facecolor=color, edgecolor="#ffffff", lw=1.2))
        canvas.text(x, y, label[:3].upper(), color="#ffffff", fontsize=7, fontweight="bold", ha="center", va="center")

    @staticmethod
    def _cell_color(column_index: int, value: float, style: str) -> str:
        if column_index == 0:
            t = min(max((value - 32) / 24, 0), 1)
            colors = ["#fff5bf", "#ffd400"] if style == "heatmap_light" else ["#4d3300", "#ffd400"]
            return cmap_color(colors, t)
        if column_index == 1:
            t = min(max((value - 48) / 22, 0), 1)
            return cmap_color(["#f6c8d0", "#f7f1bd", "#a6efb7"], t)
        if column_index == 2:
            t = min(max((value - 0.8) / 3.0, 0), 1)
            return cmap_color(["#f7b7c3", "#fff1b8", "#a6eeb7"], t)
        t = 1 - min(max((value - 31) / 10, 0), 1)
        return cmap_color(["#f7b7c3", "#fff1b8", "#b7f2c0"], t)

    @staticmethod
    def _rows(data: dict[str, Any]) -> list[dict[str, Any]]:
        rows = data.get("rows")
        if isinstance(rows, list) and rows:
            return [row for row in rows if isinstance(row, dict)]

        def row(
            team: str,
            team_color: str,
            name: str,
            pts_created: float,
            ts: float,
            ast_tov: float,
            mpg: float,
        ) -> dict[str, Any]:
            return {
                "team": team,
                "team_color": team_color,
                "name": name,
                "pts_created": pts_created,
                "ts": ts,
                "ast_tov": ast_tov,
                "mpg": mpg,
            }

        return [
            row("OKC", "#007ac1", "SGA", 55.3, 68, 3.6, 35.7),
            row("DET", "#c8102e", "Cunningham", 51.1, 60, 1.2, 40.4),
            row("DEN", "#0e2240", "Jokic", 50.0, 55, 2.5, 39.5),
            row("TOR", "#ce1141", "Barnes", 44.4, 61, 2.5, 39.0),
            row("LAL", "#552583", "James", 43.4, 53, 1.9, 38.7),
            row("ORL", "#0077c0", "Banchero", 42.7, 52, 1.8, 39.0),
            row("NYK", "#f58426", "Brunson", 41.6, 60, 2.5, 34.3),
            row("BOS", "#008348", "Tatum", 41.3, 61, 2.4, 36.3),
            row("PHI", "#006bb6", "Maxey", 40.6, 58, 3.7, 39.1),
            row("PHI", "#ed174c", "Embiid", 40.2, 53, 3.2, 34.2),
            row("DEN", "#fec524", "Murray", 38.4, 48, 2.6, 39.7),
            row("LAC", "#1d428a", "Harden", 37.2, 62, 1.2, 37.0),
            row("SAC", "#5a2d81", "Fox", 36.5, 55, 2.5, 35.0),
            row("BOS", "#008348", "Brown", 35.6, 55, 0.9, 35.6),
            row("SAS", "#000000", "Castle", 34.9, 58, 1.9, 32.0),
        ]

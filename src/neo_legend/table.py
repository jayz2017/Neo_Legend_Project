"""Heatmap table renderer skill."""

from __future__ import annotations

import random
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any

from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, Rectangle
from PIL import Image, ImageOps

from neo_legend._plotting import add_canvas, cmap_color, create_figure, save_png
from neo_legend.base import BaseLegendSkill, StyleDefinition
from neo_legend.models import RenderRequest, RenderResult

LEAGUE_TABLE_THEMES: dict[str, dict[str, str]] = {
    "clean_contrast": {
        "canvas": "#ffffff",
        "header": "#062236",
        "header_edge": "#315569",
        "average": "#eef3f7",
        "average_edge": "#cbd7df",
        "first_row": "#e7f6ff",
        "first_edge": "#d4ecfa",
        "row_odd": "#ffffff",
        "row_even": "#f8fbfd",
        "cell_edge": "#edf2f6",
        "text": "#06111a",
        "low": "#1187ff",
        "mid": "#ffffff",
        "high": "#ff8a00",
    },
    "emerald_coral": {
        "canvas": "#ffffff",
        "header": "#10352f",
        "header_edge": "#2d6b5f",
        "average": "#eef6f2",
        "average_edge": "#cce1d7",
        "first_row": "#e6fbf3",
        "first_edge": "#d1efe3",
        "row_odd": "#ffffff",
        "row_even": "#f7fcfa",
        "cell_edge": "#e9f3ef",
        "text": "#07140f",
        "low": "#18a6d9",
        "mid": "#ffffff",
        "high": "#ff6f3c",
    },
    "royal_gold": {
        "canvas": "#ffffff",
        "header": "#1f254d",
        "header_edge": "#4b5591",
        "average": "#f0f2fb",
        "average_edge": "#d2d6eb",
        "first_row": "#eef4ff",
        "first_edge": "#dce8fb",
        "row_odd": "#ffffff",
        "row_even": "#f9faff",
        "cell_edge": "#eef0fa",
        "text": "#070b1c",
        "low": "#0b97c9",
        "mid": "#ffffff",
        "high": "#d99a00",
    },
    "ink_ruby": {
        "canvas": "#ffffff",
        "header": "#17212b",
        "header_edge": "#41505f",
        "average": "#f1f4f6",
        "average_edge": "#d1d9df",
        "first_row": "#edf7fb",
        "first_edge": "#d8ebf1",
        "row_odd": "#ffffff",
        "row_even": "#fafcfd",
        "cell_edge": "#edf1f4",
        "text": "#071018",
        "low": "#1c8cf0",
        "mid": "#ffffff",
        "high": "#e0465d",
    },
}


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
        StyleDefinition(
            "league_standings_gradient",
            "Single-line header table with configurable average-centered gradient columns.",
        ),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        if style == "league_standings_gradient":
            return self.result(self._render_league_standings_gradient(request, width, height), style)

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

    def _render_league_standings_gradient(
        self,
        request: RenderRequest,
        width: int,
        height: int,
    ) -> bytes:
        data = request.data
        left_image_config = self._left_image_config(data)
        if left_image_config:
            side_width = self._left_image_width(left_image_config, width)
            chart_width = max(width - side_width, 1)
            table_bytes = self._render_league_table_bytes(data, chart_width, height)
            return self._compose_left_image(
                table_bytes=table_bytes,
                config=left_image_config,
                total_width=width,
                height=height,
                side_width=side_width,
            )
        return self._render_league_table_bytes(data, width, height)

    def _render_league_table_bytes(
        self,
        data: dict[str, Any],
        width: int,
        height: int,
    ) -> bytes:
        theme = self._league_theme(data)
        fig = create_figure(width, height, theme["canvas"])
        canvas = add_canvas(fig)

        columns = self._league_columns(data)
        rows = self._league_rows(data)
        average_row = data.get("average_row")
        if not isinstance(average_row, dict):
            average_row = self._computed_average_row(columns, rows)
        gradients = self._gradient_configs(data, columns, rows, average_row, theme=theme)

        left = float(data.get("left", 0.003))
        right = float(data.get("right", 0.997))
        top = float(data.get("top", 0.996))
        bottom = float(data.get("bottom", 0.018))
        header_groups = self._header_groups(data, columns)
        header_h = float(data.get("header_height", 0.118 if header_groups else 0.096))
        row_count = len(rows) + (1 if average_row else 0)
        row_h = min(
            float(data.get("row_height", 0.052)),
            max((top - bottom - header_h) / max(row_count, 1), 0.018),
        )

        widths = self._column_widths(columns, left, right)
        x_positions = self._column_positions(columns, left, right)
        font = self._cjk_font()
        header_fontsize = self._font_size(width, height, row_h, min_size=8.0, max_size=14.0, scale=0.34)
        body_fontsize = self._font_size(width, height, row_h, min_size=8.0, max_size=13.0, scale=0.30)

        header_y = top - header_h
        header_color = str(data.get("header_color", theme["header"]))
        header_edge = str(data.get("header_edge_color", theme["header_edge"]))
        if header_groups:
            self._draw_grouped_header(
                canvas=canvas,
                columns=columns,
                groups=header_groups,
                x_positions=x_positions,
                widths=widths,
                header_y=header_y,
                header_h=header_h,
                font=font,
                fontsize=header_fontsize,
                fill=header_color,
                edge=header_edge,
                child_ratio=float(data.get("child_header_ratio", 0.52)),
            )
        else:
            self._draw_flat_header(
                canvas=canvas,
                columns=columns,
                x_positions=x_positions,
                widths=widths,
                header_y=header_y,
                header_h=header_h,
                font=font,
                fontsize=header_fontsize,
                fill=header_color,
                edge=header_edge,
            )

        y = header_y
        if average_row:
            y -= row_h
            self._draw_league_row(
                canvas=canvas,
                columns=columns,
                row=average_row,
                row_index=-1,
                x_positions=x_positions,
                widths=widths,
                y=y,
                row_h=row_h,
                gradients={},
                font=font,
                fontsize=body_fontsize,
                is_average=True,
                theme=theme,
            )

        for row_index, row in enumerate(rows):
            y -= row_h
            self._draw_league_row(
                canvas=canvas,
                columns=columns,
                row=row,
                row_index=row_index,
                x_positions=x_positions,
                widths=widths,
                y=y,
                row_h=row_h,
                gradients=gradients,
                font=font,
                fontsize=body_fontsize,
                is_average=False,
                theme=theme,
            )

        return save_png(fig)

    def _draw_flat_header(
        self,
        canvas,
        columns: list[dict[str, Any]],
        x_positions: list[float],
        widths: list[float],
        header_y: float,
        header_h: float,
        font: FontProperties | None,
        fontsize: float,
        fill: str,
        edge: str,
    ) -> None:
        for column, x, col_w in zip(columns, x_positions, widths, strict=True):
            canvas.add_patch(Rectangle((x, header_y), col_w, header_h, facecolor=fill, edgecolor=edge, lw=1.1))
            self._draw_text(
                canvas,
                x + col_w / 2,
                header_y + header_h / 2,
                str(column["label"]),
                font,
                color="#ffffff",
                fontsize=fontsize,
                fontweight="bold",
                ha="center",
                va="center",
            )

    def _draw_grouped_header(
        self,
        canvas,
        columns: list[dict[str, Any]],
        groups: list[dict[str, Any]],
        x_positions: list[float],
        widths: list[float],
        header_y: float,
        header_h: float,
        font: FontProperties | None,
        fontsize: float,
        fill: str,
        edge: str,
        child_ratio: float,
    ) -> None:
        key_to_index = {str(column["key"]): index for index, column in enumerate(columns)}
        child_h = header_h * max(min(child_ratio, 0.72), 0.28)
        parent_h = header_h - child_h
        grouped_keys: set[str] = set()

        for group in groups:
            group_keys = [key for key in group["columns"] if key in key_to_index]
            if not group_keys:
                continue
            grouped_keys.update(group_keys)
            x, width = self._span_bounds(group_keys, key_to_index, x_positions, widths)
            children = [child for child in group.get("children", []) if child.get("columns")]
            show_children = bool(group.get("show_children", True)) and bool(children)

            if show_children:
                canvas.add_patch(
                    Rectangle((x, header_y + child_h), width, parent_h, facecolor=fill, edgecolor=edge, lw=1.1)
                )
                self._draw_text(
                    canvas,
                    x + width / 2,
                    header_y + child_h + parent_h / 2,
                    str(group["label"]),
                    font,
                    color="#ffffff",
                    fontsize=fontsize,
                    fontweight="bold",
                    ha="center",
                    va="center",
                )
                for child in children:
                    child_keys = [key for key in child["columns"] if key in key_to_index]
                    if not child_keys:
                        continue
                    child_x, child_width = self._span_bounds(child_keys, key_to_index, x_positions, widths)
                    canvas.add_patch(
                        Rectangle((child_x, header_y), child_width, child_h, facecolor=fill, edgecolor=edge, lw=1.1)
                    )
                    self._draw_text(
                        canvas,
                        child_x + child_width / 2,
                        header_y + child_h / 2,
                        str(child["label"]),
                        font,
                        color="#ffffff",
                        fontsize=max(fontsize * 0.86, 7.0),
                        fontweight="bold",
                        ha="center",
                        va="center",
                    )
            elif bool(group.get("show_children", True)):
                canvas.add_patch(
                    Rectangle((x, header_y + child_h), width, parent_h, facecolor=fill, edgecolor=edge, lw=1.1)
                )
                self._draw_text(
                    canvas,
                    x + width / 2,
                    header_y + child_h + parent_h / 2,
                    str(group["label"]),
                    font,
                    color="#ffffff",
                    fontsize=fontsize,
                    fontweight="bold",
                    ha="center",
                    va="center",
                )
                for key in group_keys:
                    index = key_to_index[key]
                    canvas.add_patch(
                        Rectangle(
                            (x_positions[index], header_y),
                            widths[index],
                            child_h,
                            facecolor=fill,
                            edgecolor=edge,
                            lw=1.1,
                        )
                    )
                    self._draw_text(
                        canvas,
                        x_positions[index] + widths[index] / 2,
                        header_y + child_h / 2,
                        str(columns[index]["label"]),
                        font,
                        color="#ffffff",
                        fontsize=max(fontsize * 0.86, 7.0),
                        fontweight="bold",
                        ha="center",
                        va="center",
                    )
            else:
                canvas.add_patch(Rectangle((x, header_y), width, header_h, facecolor=fill, edgecolor=edge, lw=1.1))
                self._draw_text(
                    canvas,
                    x + width / 2,
                    header_y + header_h / 2,
                    str(group["label"]),
                    font,
                    color="#ffffff",
                    fontsize=fontsize,
                    fontweight="bold",
                    ha="center",
                    va="center",
                )

        for index, column in enumerate(columns):
            key = str(column["key"])
            if key in grouped_keys:
                continue
            canvas.add_patch(
                Rectangle(
                    (x_positions[index], header_y),
                    widths[index],
                    header_h,
                    facecolor=fill,
                    edgecolor=edge,
                    lw=1.1,
                )
            )
            self._draw_text(
                canvas,
                x_positions[index] + widths[index] / 2,
                header_y + header_h / 2,
                str(column["label"]),
                font,
                color="#ffffff",
                fontsize=fontsize,
                fontweight="bold",
                ha="center",
                va="center",
            )

    def _draw_league_row(
        self,
        canvas,
        columns: list[dict[str, Any]],
        row: dict[str, Any],
        row_index: int,
        x_positions: list[float],
        widths: list[float],
        y: float,
        row_h: float,
        gradients: dict[str, dict[str, Any]],
        font: FontProperties | None,
        fontsize: float,
        is_average: bool,
        theme: dict[str, str],
    ) -> None:
        if is_average:
            row_fill = theme["average"]
            edge = theme["average_edge"]
        elif row_index == 0:
            row_fill = theme["first_row"]
            edge = theme["first_edge"]
        else:
            row_fill = theme["row_odd"] if row_index % 2 else theme["row_even"]
            edge = theme["cell_edge"]

        for column, x, col_w in zip(columns, x_positions, widths, strict=True):
            key = str(column["key"])
            fill = row_fill
            value = row.get(key)
            if not is_average and key in gradients:
                numeric_value = self._to_float(value)
                if numeric_value is not None:
                    fill = self._diverging_cell_color(
                        numeric_value,
                        midpoint=gradients[key]["midpoint"],
                        spread=gradients[key]["spread"],
                        higher_is_better=gradients[key]["higher_is_better"],
                        low_color=gradients[key]["low_color"],
                        mid_color=gradients[key]["mid_color"],
                        high_color=gradients[key]["high_color"],
                    )

            canvas.add_patch(Rectangle((x, y), col_w, row_h, facecolor=fill, edgecolor=edge, lw=0.65))
            align = str(column.get("align", "center"))
            if align == "left":
                text_x = x + col_w * 0.08
                ha = "left"
            elif align == "right":
                text_x = x + col_w * 0.92
                ha = "right"
            else:
                text_x = x + col_w / 2
                ha = "center"

            text = self._format_cell_value(value, column, is_average=is_average)
            self._draw_text(
                canvas,
                text_x,
                y + row_h / 2,
                text,
                font,
                color=theme["text"],
                fontsize=fontsize,
                fontweight="bold" if bool(column.get("bold")) else "normal",
                ha=ha,
                va="center",
            )

    @staticmethod
    def _span_bounds(
        keys: list[str],
        key_to_index: dict[str, int],
        x_positions: list[float],
        widths: list[float],
    ) -> tuple[float, float]:
        indexes = sorted(key_to_index[key] for key in keys if key in key_to_index)
        if not indexes:
            return 0.0, 0.0
        first = indexes[0]
        last = indexes[-1]
        return x_positions[first], x_positions[last] + widths[last] - x_positions[first]

    @staticmethod
    def _header_groups(data: dict[str, Any], columns: list[dict[str, Any]]) -> list[dict[str, Any]]:
        column_keys = {str(column["key"]) for column in columns}
        raw_groups = data.get("header_groups")
        if isinstance(raw_groups, list):
            groups: list[dict[str, Any]] = []
            for raw_group in raw_groups:
                if not isinstance(raw_group, dict):
                    continue
                children = TableSkill._header_children(raw_group, column_keys)
                group_columns = TableSkill._header_group_columns(raw_group, children, column_keys)
                if not group_columns:
                    continue
                groups.append(
                    {
                        "label": str(raw_group.get("label", raw_group.get("title", ""))),
                        "columns": group_columns,
                        "children": children,
                        "show_children": bool(raw_group.get("show_children", raw_group.get("children_visible", True))),
                    }
                )
            return groups

        groups = []
        current_parent: str | None = None
        current_columns: list[str] = []
        for column in columns:
            parent = column.get("parent")
            key = str(column["key"])
            if parent:
                parent_label = str(parent)
                if parent_label != current_parent:
                    if current_parent and current_columns:
                        groups.append(
                            {
                                "label": current_parent,
                                "columns": current_columns,
                                "children": [],
                                "show_children": True,
                            }
                        )
                    current_parent = parent_label
                    current_columns = [key]
                else:
                    current_columns.append(key)
            elif current_parent and current_columns:
                groups.append(
                    {
                        "label": current_parent,
                        "columns": current_columns,
                        "children": [],
                        "show_children": True,
                    }
                )
                current_parent = None
                current_columns = []
        if current_parent and current_columns:
            groups.append(
                {
                    "label": current_parent,
                    "columns": current_columns,
                    "children": [],
                    "show_children": True,
                }
            )
        return groups

    @staticmethod
    def _header_children(raw_group: dict[str, Any], column_keys: set[str]) -> list[dict[str, Any]]:
        raw_children = raw_group.get("children", raw_group.get("subheaders", []))
        if not isinstance(raw_children, list):
            return []
        children: list[dict[str, Any]] = []
        for raw_child in raw_children:
            if not isinstance(raw_child, dict):
                continue
            raw_columns = raw_child.get("columns", raw_child.get("keys", []))
            if not isinstance(raw_columns, list):
                continue
            child_columns = [str(key) for key in raw_columns if str(key) in column_keys]
            if child_columns:
                children.append({"label": str(raw_child.get("label", raw_child.get("title", ""))), "columns": child_columns})
        return children

    @staticmethod
    def _header_group_columns(
        raw_group: dict[str, Any],
        children: list[dict[str, Any]],
        column_keys: set[str],
    ) -> list[str]:
        raw_columns = raw_group.get("columns", raw_group.get("keys"))
        if isinstance(raw_columns, list):
            return [str(key) for key in raw_columns if str(key) in column_keys]
        columns: list[str] = []
        for child in children:
            columns.extend(child["columns"])
        return columns

    @staticmethod
    def _league_theme(data: dict[str, Any]) -> dict[str, str]:
        raw_theme = str(data.get("color_theme", data.get("theme", "random"))).strip().lower()
        if raw_theme == "random":
            theme_names = sorted(LEAGUE_TABLE_THEMES)
            seed = data.get("theme_seed")
            rng = random.Random(str(seed)) if seed is not None else random.SystemRandom()
            raw_theme = rng.choice(theme_names)
        if raw_theme not in LEAGUE_TABLE_THEMES:
            raw_theme = "clean_contrast"
        data["_resolved_color_theme"] = raw_theme
        theme = dict(LEAGUE_TABLE_THEMES[raw_theme])

        overrides = data.get("theme_overrides")
        if isinstance(overrides, dict):
            for key, value in overrides.items():
                if key in theme and isinstance(value, str):
                    theme[key] = value
        return theme

    @staticmethod
    def _available_league_themes() -> list[dict[str, str]]:
        return [dict(theme) for theme in LEAGUE_TABLE_THEMES.values()]

    @staticmethod
    def _league_columns(data: dict[str, Any]) -> list[dict[str, Any]]:
        columns = data.get("columns")
        if isinstance(columns, list) and columns:
            normalized = []
            for column in columns:
                if not isinstance(column, dict) or "key" not in column:
                    continue
                normalized.append(
                    {
                        "key": str(column["key"]),
                        "label": str(column.get("label", column["key"])),
                        "width": float(column.get("width", 1.0)),
                        "align": str(column.get("align", "center")),
                        "format": column.get("format"),
                        "average_format": column.get("average_format"),
                        "bold": bool(column.get("bold", False)),
                        "gradient": column.get("gradient", False),
                        "parent": column.get("parent"),
                    }
                )
            if normalized:
                return normalized

        return [
            {"key": "rank", "label": "排名", "width": 0.055, "format": "int"},
            {"key": "team", "label": "球队", "width": 0.150, "align": "center", "bold": True},
            {"key": "games", "label": "场数", "width": 0.105, "format": "int", "average_format": ".1f"},
            {"key": "wins", "label": "胜场", "width": 0.105, "format": "int", "average_format": ".1f"},
            {"key": "losses", "label": "负场", "width": 0.105, "format": "int", "average_format": ".1f"},
            {"key": "pace", "label": "节奏", "width": 0.130, "format": ".1f"},
            {"key": "off_rating", "label": "百回合得分", "width": 0.145, "format": ".1f"},
            {"key": "def_rating", "label": "百回合失分", "width": 0.145, "format": ".1f"},
            {"key": "net_rating", "label": "百回合净胜分", "width": 0.160, "format": ".1f"},
        ]

    @staticmethod
    def _league_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
        rows = data.get("rows")
        if isinstance(rows, list) and rows:
            return [row for row in rows if isinstance(row, dict)]

        teams = [
            ("上海久事", 42, 38, 4, 95.1, 126.4, 105.4, 21.0),
            ("浙江浙商证券", 42, 33, 9, 90.8, 120.1, 107.9, 12.3),
            ("北京北汽", 42, 29, 13, 88.5, 122.8, 111.8, 11.0),
            ("浙江稠州金租", 42, 27, 15, 87.1, 118.6, 110.5, 8.2),
            ("广东东阳光", 42, 27, 15, 94.4, 119.0, 112.5, 6.5),
            ("深圳马可波罗", 42, 30, 12, 97.3, 121.8, 115.5, 6.3),
            ("青岛崂山啤酒", 42, 25, 17, 90.4, 115.5, 111.2, 4.4),
            ("山东高速", 42, 24, 18, 94.0, 118.3, 114.4, 4.0),
            ("山西汾酒", 42, 22, 20, 94.5, 117.9, 114.9, 3.1),
            ("辽宁本钢", 42, 23, 19, 88.5, 116.0, 113.7, 2.3),
            ("宁波町渥", 42, 21, 21, 89.5, 114.8, 112.8, 2.0),
            ("广州朗肽海本", 42, 18, 24, 90.7, 115.4, 116.5, -1.2),
            ("新疆伊力特", 42, 14, 28, 91.3, 112.9, 114.8, -1.9),
            ("福建晋江文旅", 42, 17, 25, 94.4, 116.3, 119.3, -2.9),
            ("天津先行者", 42, 13, 29, 91.8, 121.4, 126.0, -4.7),
            ("北京控股", 42, 18, 24, 91.9, 115.7, 121.2, -5.5),
            ("南京天之蓝", 42, 14, 28, 94.4, 113.8, 120.5, -6.7),
        ]
        return [
            {
                "rank": index,
                "team": team,
                "games": games,
                "wins": wins,
                "losses": losses,
                "pace": pace,
                "off_rating": off_rating,
                "def_rating": def_rating,
                "net_rating": net_rating,
            }
            for index, (team, games, wins, losses, pace, off_rating, def_rating, net_rating) in enumerate(teams, start=1)
        ]

    @staticmethod
    def _computed_average_row(
        columns: list[dict[str, Any]],
        rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        average_row: dict[str, Any] = {}
        if not rows:
            return average_row
        for column in columns:
            key = str(column["key"])
            values = [TableSkill._to_float(row.get(key)) for row in rows]
            numeric_values = [value for value in values if value is not None]
            if numeric_values:
                average_row[key] = sum(numeric_values) / len(numeric_values)
        team_key = next((str(column["key"]) for column in columns if str(column["key"]) in {"team", "name"}), None)
        if team_key:
            average_row[team_key] = "联盟平均"
        return average_row

    @staticmethod
    def _gradient_configs(
        data: dict[str, Any],
        columns: list[dict[str, Any]],
        rows: list[dict[str, Any]],
        average_row: dict[str, Any],
        theme: dict[str, str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        theme = theme or LEAGUE_TABLE_THEMES["clean_contrast"]
        has_gradient_config = "gradient_columns" in data or "gradients" in data
        raw = data.get("gradient_columns", data.get("gradients", {}))
        configs: dict[str, dict[str, Any]] = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                if value is False or value is None:
                    continue
                if isinstance(value, dict) and value.get("enabled") is False:
                    continue
                configs[str(key)] = dict(value) if isinstance(value, dict) else {}
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, str):
                    configs[item] = {}
                elif isinstance(item, dict):
                    if item.get("enabled") is False:
                        continue
                    key = item.get("key", item.get("column"))
                    if key:
                        config = dict(item)
                        config.pop("key", None)
                        config.pop("column", None)
                        configs[str(key)] = config

        if not has_gradient_config:
            column_keys = {str(column["key"]) for column in columns}
            if {"off_rating", "def_rating", "net_rating"}.issubset(column_keys):
                configs = {
                    "off_rating": {"higher_is_better": True},
                    "def_rating": {"higher_is_better": False},
                    "net_rating": {"higher_is_better": True},
                }

        for column in columns:
            if column.get("gradient") and str(column["key"]) not in configs:
                configs[str(column["key"])] = {}

        resolved: dict[str, dict[str, Any]] = {}
        for key, config in configs.items():
            midpoint = TableSkill._resolve_midpoint(key, config, rows, average_row)
            values = [TableSkill._to_float(row.get(key)) for row in rows]
            numeric_values = [value for value in values if value is not None]
            if midpoint is None or not numeric_values:
                continue
            configured_spread = TableSkill._to_float(config.get("max_deviation", config.get("spread")))
            spread = configured_spread or max(abs(value - midpoint) for value in numeric_values) or 1.0
            higher_is_better = bool(config.get("higher_is_better", not bool(config.get("lower_is_better", False))))
            resolved[key] = {
                "midpoint": midpoint,
                "spread": spread,
                "higher_is_better": higher_is_better,
                "low_color": str(config.get("low_color", theme["low"])),
                "mid_color": str(config.get("mid_color", theme["mid"])),
                "high_color": str(config.get("high_color", theme["high"])),
            }
        return resolved

    @staticmethod
    def _resolve_midpoint(
        key: str,
        config: dict[str, Any],
        rows: list[dict[str, Any]],
        average_row: dict[str, Any],
    ) -> float | None:
        raw_midpoint = config.get("midpoint", "average")
        numeric_midpoint = TableSkill._to_float(raw_midpoint)
        if numeric_midpoint is not None:
            return numeric_midpoint
        average_value = TableSkill._to_float(average_row.get(key))
        if raw_midpoint in {None, "average", "mean"} and average_value is not None:
            return average_value
        values = [TableSkill._to_float(row.get(key)) for row in rows]
        numeric_values = [value for value in values if value is not None]
        if not numeric_values:
            return None
        return sum(numeric_values) / len(numeric_values)

    @staticmethod
    def _diverging_cell_color(
        value: float,
        midpoint: float,
        spread: float,
        higher_is_better: bool = True,
        low_color: str = "#2f91ff",
        mid_color: str = "#f5f7fa",
        high_color: str = "#ff9400",
    ) -> str:
        if spread <= 0:
            return mid_color
        distance = max(min((value - midpoint) / spread, 1.0), -1.0)
        if not higher_is_better:
            distance *= -1.0
        if distance >= 0:
            return cmap_color([mid_color, high_color], distance)
        return cmap_color([mid_color, low_color], abs(distance))

    @staticmethod
    def _column_widths(columns: list[dict[str, Any]], left: float, right: float) -> list[float]:
        total_weight = sum(max(float(column.get("width", 1.0)), 0.001) for column in columns)
        available = right - left
        return [available * max(float(column.get("width", 1.0)), 0.001) / total_weight for column in columns]

    @staticmethod
    def _column_positions(columns: list[dict[str, Any]], left: float, right: float) -> list[float]:
        positions: list[float] = []
        cursor = left
        for width in TableSkill._column_widths(columns, left, right):
            positions.append(cursor)
            cursor += width
        return positions

    @staticmethod
    def _format_cell_value(value: Any, column: dict[str, Any], is_average: bool = False) -> str:
        if value is None:
            return ""
        cell_format = column.get("average_format") if is_average and column.get("average_format") else column.get("format")
        if cell_format in {None, "", "raw"}:
            return str(value)
        numeric_value = TableSkill._to_float(value)
        if numeric_value is None:
            return str(value)
        if cell_format in {"int", "integer"}:
            return f"{numeric_value:.0f}"
        if cell_format in {"float1", "one_decimal"}:
            return f"{numeric_value:.1f}"
        if isinstance(cell_format, str) and cell_format.startswith("."):
            return f"{numeric_value:{cell_format}}"
        if isinstance(cell_format, str) and "{" in cell_format:
            return cell_format.format(value=numeric_value)
        return str(value)

    @staticmethod
    def _left_image_config(data: dict[str, Any]) -> dict[str, Any] | None:
        raw = data.get("left_image", data.get("left_image_path"))
        if raw is None:
            return None
        if isinstance(raw, str):
            raw = {"path": raw}
        if not isinstance(raw, dict) or not raw.get("path"):
            return None
        image_path = Path(str(raw["path"])).expanduser()
        if not image_path.is_absolute():
            image_path = Path.cwd() / image_path
        if not image_path.exists():
            return None
        config = dict(raw)
        config["path"] = image_path
        return config

    @staticmethod
    def _left_image_width(config: dict[str, Any], total_width: int) -> int:
        configured_pixels = TableSkill._to_float(config.get("width_px", config.get("width")))
        if configured_pixels is not None:
            side_width = int(configured_pixels)
        else:
            ratio = TableSkill._to_float(config.get("width_ratio", config.get("ratio"))) or 0.28
            side_width = int(total_width * ratio)
        min_chart_width = int(TableSkill._to_float(config.get("min_chart_width")) or 320)
        return max(1, min(side_width, max(total_width - min_chart_width, 1)))

    @staticmethod
    def _compose_left_image(
        table_bytes: bytes,
        config: dict[str, Any],
        total_width: int,
        height: int,
        side_width: int,
    ) -> bytes:
        background = str(config.get("background", "#ffffff"))
        canvas = Image.new("RGBA", (total_width, height), background)
        table_image = Image.open(BytesIO(table_bytes)).convert("RGBA")
        canvas.alpha_composite(table_image, (side_width, 0))

        padding = int(TableSkill._to_float(config.get("padding")) or 0)
        box_w = max(side_width - padding * 2, 1)
        box_h = max(height - padding * 2, 1)
        source = Image.open(config["path"]).convert("RGBA")
        fit = str(config.get("fit", "contain")).lower()
        if fit == "cover":
            fitted = ImageOps.fit(source, (box_w, box_h), method=Image.Resampling.LANCZOS)
        else:
            fitted = ImageOps.contain(source, (box_w, box_h), method=Image.Resampling.LANCZOS)

        align_y = str(config.get("vertical_align", "center")).lower()
        if align_y == "top":
            y = padding
        elif align_y == "bottom":
            y = height - padding - fitted.height
        else:
            y = padding + (box_h - fitted.height) // 2
        x = padding + (box_w - fitted.width) // 2
        canvas.alpha_composite(fitted, (x, y))

        output = BytesIO()
        canvas.convert("RGB").save(output, format="PNG")
        return output.getvalue()

    @staticmethod
    def _font_size(
        width: int,
        height: int,
        row_h: float,
        min_size: float,
        max_size: float,
        scale: float,
    ) -> float:
        row_pixels = row_h * height
        size = min(width / 82.0, row_pixels * scale)
        return max(min(size, max_size), min_size)

    @staticmethod
    def _draw_text(canvas, x: float, y: float, text: str, font: FontProperties | None, **kwargs: Any) -> None:
        if font is not None:
            kwargs["fontproperties"] = font
        canvas.text(x, y, text, **kwargs)

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if isinstance(value, bool) or value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    @lru_cache(maxsize=1)
    def _cjk_font() -> FontProperties | None:
        font_paths = (
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
            r"C:\Windows\Fonts\NotoSansCJK-Regular.ttc",
        )
        for font_path in font_paths:
            if Path(font_path).exists():
                return FontProperties(fname=font_path)
        return None

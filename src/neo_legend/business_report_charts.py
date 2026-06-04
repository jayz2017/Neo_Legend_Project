from __future__ import annotations

"""Additional Wall Street style report charts."""


from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, PathPatch, Rectangle, Wedge
from matplotlib.path import Path

from neo_legend._plotting import add_canvas, create_figure, save_png, seeded_rng
from neo_legend.base import BaseLegendSkill, StyleDefinition
from neo_legend.models import RenderRequest, RenderResult
from neo_legend.report_style import (
    add_footer,
    add_report_axes,
    blend,
    darken,
    draw_kpi_strip,
    draw_panel_frame,
    draw_report_background,
    draw_report_header,
    draw_series_legend,
    format_metric,
    lighten,
    resolve_report_text,
    resolve_report_theme,
    style_cartesian_axes,
    value_range,
)


class CalendarChartSkill(BaseLegendSkill):
    legend_type = "calendar_chart"
    display_name = "Executive Calendar Chart"
    default_style = "executive_month"
    default_size = (1400, 900)
    style_definitions = (
        StyleDefinition("executive_month", "Commercial report calendar with event markers and KPI summary."),
        StyleDefinition("earnings_calendar", "Wall Street earnings and macro-event calendar layout."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._extract_data(request.data)
        theme = resolve_report_theme(request.data, style)

        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)
        report_text = resolve_report_text(
            request.data,
            request.title,
            request.subtitle,
            default_title=data["month_label"],
            default_subtitle="Catalyst calendar for commercial reporting",
            default_kicker="Event Calendar",
            default_footer="NEO LEGEND | EXECUTIVE CALENDAR REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )
        self._draw_calendar(fig, canvas, data, theme)
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        if data.get("events"):
            return {
                "month_label": data.get("month_label", "May 2026"),
                "start_weekday": int(data.get("start_weekday", 4)),
                "days": int(data.get("days", 31)),
                "events": data["events"],
            }
        rng = seeded_rng(522)
        event_types = ["EPS", "RATE", "M&A", "IPO"]
        events = []
        for day in range(1, 32):
            count = int(rng.choice([0, 0, 1, 1, 2, 3], p=[0.25, 0.18, 0.26, 0.16, 0.10, 0.05]))
            for _ in range(count):
                events.append(
                    {
                        "day": day,
                        "type": str(rng.choice(event_types)),
                        "impact": float(rng.uniform(0.35, 1.0)),
                    }
                )
        return {"month_label": "May 2026", "start_weekday": 4, "days": 31, "events": events}

    @staticmethod
    def _draw_calendar(fig: plt.Figure, canvas: plt.Axes, data: dict[str, Any], theme) -> None:
        events = data["events"]
        event_days = {int(event["day"]) for event in events}
        peak_day = max(event_days, key=lambda day: sum(1 for event in events if int(event["day"]) == day)) if event_days else 0
        draw_kpi_strip(
            canvas,
            theme,
            [
                ("events", str(len(events)), theme.primary),
                ("active days", str(len(event_days)), theme.accent),
                ("peak day", f"{peak_day:02d}" if peak_day else "-", theme.secondary),
            ],
        )

        rect = (0.09, 0.135, 0.82, 0.58)
        draw_panel_frame(canvas, rect, theme)
        ax = fig.add_axes(rect, facecolor=theme.panel)
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 6.6)
        ax.set_axis_off()

        weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for idx, label in enumerate(weekdays):
            ax.text(idx + 0.5, 6.24, label, color=theme.muted, fontsize=10, fontweight="bold", ha="center")

        marker_colors = {
            "EPS": theme.primary,
            "RATE": theme.accent,
            "M&A": theme.good,
            "IPO": theme.secondary,
        }
        markers = {"EPS": "o", "RATE": "^", "M&A": "s", "IPO": "D"}
        events_by_day: dict[int, list[dict[str, Any]]] = {}
        for event in events:
            events_by_day.setdefault(int(event["day"]), []).append(event)

        start = int(data["start_weekday"])
        days = int(data["days"])
        for day in range(1, days + 1):
            slot = start + day - 1
            col = slot % 7
            row = 5 - slot // 7
            x = col
            y = row
            face = blend(theme.panel, theme.panel_alt, 0.35 if day in event_days else 0.12)
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=face, edgecolor=theme.grid, lw=0.8, alpha=0.96))
            ax.text(x + 0.10, y + 0.80, f"{day:02d}", color=theme.muted, fontsize=9, fontweight="bold", ha="left", va="top")
            day_events = events_by_day.get(day, [])[:4]
            for idx, event in enumerate(day_events):
                mx = x + 0.22 + (idx % 2) * 0.34
                my = y + 0.32 + (idx // 2) * 0.24
                event_type = str(event.get("type", "EPS"))
                color = marker_colors.get(event_type, theme.primary)
                ax.scatter([mx], [my], s=110 * float(event.get("impact", 0.7)), marker=markers.get(event_type, "o"), color=color, edgecolors=theme.text, linewidths=0.5, zorder=5)

        legend_items = list(marker_colors.items())
        draw_series_legend(canvas, theme, legend_items, y=0.085)


class MatrixBubbleChartSkill(BaseLegendSkill):
    legend_type = "matrix_bubble_chart"
    display_name = "Correlation Bubble Matrix"
    default_style = "correlation_board"
    default_size = (1400, 900)
    style_definitions = (
        StyleDefinition("correlation_board", "Wall Street correlation matrix with sized bubbles."),
        StyleDefinition("risk_heat_matrix", "Risk heat matrix with diverging impact colors."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._extract_data(request.data)
        theme = resolve_report_theme(request.data, style)

        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)
        values = np.array(data["values"], dtype=float)
        report_text = resolve_report_text(
            request.data,
            request.title,
            request.subtitle,
            default_title="Cross-Asset Correlation Matrix",
            default_subtitle="Bubble size encodes magnitude, color encodes direction",
            default_kicker="Correlation Matrix",
            default_footer="NEO LEGEND | CORRELATION MATRIX REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )
        draw_kpi_strip(
            canvas,
            theme,
            [
                ("max positive", format_metric(float(np.max(values))), theme.bad),
                ("max negative", format_metric(float(np.min(values))), theme.primary),
                ("avg abs", format_metric(float(np.mean(np.abs(values)))), theme.accent),
            ],
        )
        self._draw_matrix(fig, canvas, data, values, theme)
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        if data.get("values"):
            return data
        rng = seeded_rng(409)
        rows = [f"Y{i}" for i in range(1, 7)]
        columns = [f"X{i}" for i in range(1, 11)]
        values = rng.uniform(-0.95, 0.95, size=(len(rows), len(columns)))
        return {"rows": rows, "columns": columns, "values": values.round(2).tolist()}

    @staticmethod
    def _draw_matrix(fig: plt.Figure, canvas: plt.Axes, data: dict[str, Any], values: np.ndarray, theme) -> None:
        rows = [str(row) for row in data["rows"]]
        columns = [str(column) for column in data["columns"]]
        ax = add_report_axes(fig, canvas, (0.09, 0.135, 0.82, 0.58), theme)
        ax.set_xlim(-0.5, len(columns) - 0.5)
        ax.set_ylim(len(rows) - 0.5, -0.5)
        ax.set_xticks(range(len(columns)))
        ax.set_yticks(range(len(rows)))
        ax.set_xticklabels(columns, color=theme.muted, fontsize=9, fontweight="bold")
        ax.set_yticklabels(rows, color=theme.muted, fontsize=9, fontweight="bold")
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        for x in np.arange(-0.5, len(columns), 1):
            ax.axvline(x, color=theme.grid, lw=0.75, alpha=0.55, zorder=1)
        for y in np.arange(-0.5, len(rows), 1):
            ax.axhline(y, color=theme.grid, lw=0.75, alpha=0.55, zorder=1)
        ax.axvline(len(columns) - 0.5, color=theme.grid, lw=0.75, alpha=0.55, zorder=1)
        ax.axhline(len(rows) - 0.5, color=theme.grid, lw=0.75, alpha=0.55, zorder=1)

        for row_index in range(len(rows)):
            for col_index in range(len(columns)):
                value = float(values[row_index, col_index])
                if value >= 0:
                    color = blend(theme.panel_alt, theme.bad, abs(value))
                else:
                    color = blend(theme.panel_alt, theme.primary, abs(value))
                size = 180 + abs(value) * 1450
                ax.scatter([col_index], [row_index], s=size, color=color, edgecolors=lighten(color, 0.18), linewidths=0.8, zorder=4)
                text_color = theme.text if abs(value) > 0.58 else theme.muted
                ax.text(col_index, row_index, f"{value:+.2f}".replace("+", ""), color=text_color, fontsize=8, fontweight="bold", ha="center", va="center", zorder=5)


class ChordChartSkill(BaseLegendSkill):
    legend_type = "chord_chart"
    display_name = "Capital Flow Chord"
    default_style = "capital_flows"
    default_size = (1200, 1000)
    style_definitions = (
        StyleDefinition("capital_flows", "Circular capital flow chord report."),
        StyleDefinition("sector_rotation", "Sector rotation chord with muted institutional palette."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._extract_data(request.data)
        theme = resolve_report_theme(request.data, style)
        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)
        report_text = resolve_report_text(
            request.data,
            request.title,
            request.subtitle,
            default_title="Capital Flow Chord",
            default_subtitle="Inter-segment allocation intensity and direction",
            default_kicker="Chord Flow",
            default_footer="NEO LEGEND | CAPITAL FLOW CHORD REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )
        self._draw_chord(fig, canvas, data, theme)
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        if data.get("nodes") and data.get("matrix"):
            return data
        nodes = ["A", "B", "C", "D", "E", "F", "G"]
        matrix = [
            [0, 18, 14, 4, 12, 3, 9],
            [9, 0, 12, 5, 4, 2, 11],
            [14, 10, 0, 7, 15, 5, 4],
            [4, 8, 9, 0, 7, 2, 3],
            [13, 4, 16, 6, 0, 5, 8],
            [3, 2, 5, 2, 4, 0, 5],
            [10, 9, 4, 2, 7, 5, 0],
        ]
        return {"nodes": nodes, "matrix": matrix}

    @staticmethod
    def _draw_chord(fig: plt.Figure, canvas: plt.Axes, data: dict[str, Any], theme) -> None:
        matrix = np.array(data["matrix"], dtype=float)
        nodes = [str(node) for node in data["nodes"]]
        totals = matrix.sum(axis=1) + matrix.sum(axis=0)
        draw_kpi_strip(
            canvas,
            theme,
            [
                ("total flow", format_metric(float(matrix.sum())), theme.primary),
                ("segments", str(len(nodes)), theme.accent),
                ("largest", nodes[int(np.argmax(totals))], theme.secondary),
            ],
        )
        ax = fig.add_axes((0.17, 0.10, 0.66, 0.68), facecolor="none")
        ax.set_xlim(-1.18, 1.18)
        ax.set_ylim(-1.18, 1.18)
        ax.set_aspect("equal")
        ax.set_axis_off()

        total = float(totals.sum()) or 1.0
        gap = 2.5
        start_angle = 92.0
        spans: list[tuple[float, float]] = []
        cursor = start_angle
        for value in totals:
            span = max(12.0, 360.0 * float(value) / total - gap)
            spans.append((cursor, cursor + span))
            cursor += span + gap

        colors = [theme.palette[index % len(theme.palette)] for index in range(len(nodes))]
        for index, (theta1, theta2) in enumerate(spans):
            color = colors[index]
            ax.add_patch(Wedge((0, 0), 1.0, theta1, theta2, width=0.12, facecolor=color, edgecolor=lighten(color, 0.25), lw=1.0, alpha=0.96))
            mid = np.deg2rad((theta1 + theta2) / 2)
            ax.text(1.08 * np.cos(mid), 1.08 * np.sin(mid), nodes[index], color=theme.text, fontsize=11, fontweight="black", ha="center", va="center")

        max_flow = float(np.max(matrix)) or 1.0
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                value = float(matrix[i, j] + matrix[j, i])
                if value <= 0:
                    continue
                a1 = np.deg2rad(sum(spans[i]) / 2)
                a2 = np.deg2rad(sum(spans[j]) / 2)
                p1 = np.array([0.86 * np.cos(a1), 0.86 * np.sin(a1)])
                p2 = np.array([0.86 * np.cos(a2), 0.86 * np.sin(a2)])
                verts = [tuple(p1), tuple(p1 * 0.35), tuple(p2 * 0.35), tuple(p2)]
                path = Path(verts, [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
                color = blend(colors[i], colors[j], 0.38)
                ax.add_patch(
                    PathPatch(
                        path,
                        facecolor="none",
                        edgecolor=color,
                        lw=1.5 + value / max_flow * 16,
                        alpha=0.16 + value / max_flow * 0.30,
                        capstyle="round",
                        zorder=2,
                    )
                )


class ScatterMatrixChartSkill(BaseLegendSkill):
    legend_type = "scatter_matrix_chart"
    display_name = "Executive Scatter Matrix"
    default_style = "macro_quadrants"
    default_size = (1400, 1000)
    style_definitions = (
        StyleDefinition("macro_quadrants", "Four-panel macro scatter matrix with institutional styling."),
        StyleDefinition("portfolio_pairs", "Portfolio pairwise scatter matrix with highlighted clusters."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._extract_data(request.data)
        theme = resolve_report_theme(request.data, style)
        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)
        report_text = resolve_report_text(
            request.data,
            request.title,
            request.subtitle,
            default_title="Macro Pair Matrix",
            default_subtitle="Small multiples for cross-metric inspection",
            default_kicker="Scatter Matrix",
            default_footer="NEO LEGEND | SCATTER MATRIX REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )
        self._draw_scatter_matrix(fig, canvas, data, theme)
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        if data.get("panels"):
            return data
        rng = seeded_rng(771)
        income = rng.lognormal(mean=10.0, sigma=0.55, size=220)
        life = 38 + np.log1p(income) * 3.5 + rng.normal(0, 3.2, 220)
        population = rng.lognormal(mean=17.2, sigma=1.15, size=220)
        risk = rng.normal(0, 1, 220)
        return {
            "panels": [
                {"title": "Life Expectancy vs Income", "x_label": "Income", "y_label": "Life Expectancy", "x": income.tolist(), "y": life.tolist()},
                {"title": "Income by Country Risk", "x_label": "Country Risk", "y_label": "Income", "x": risk.tolist(), "y": income.tolist()},
                {"title": "Population vs Income", "x_label": "Income", "y_label": "Population", "x": income.tolist(), "y": population.tolist()},
                {"title": "Population vs Life Expectancy", "x_label": "Life Expectancy", "y_label": "Population", "x": life.tolist(), "y": population.tolist()},
            ]
        }

    @staticmethod
    def _draw_scatter_matrix(fig: plt.Figure, canvas: plt.Axes, data: dict[str, Any], theme) -> None:
        panels = data["panels"][:4]
        all_points = sum(len(panel["x"]) for panel in panels)
        draw_kpi_strip(
            canvas,
            theme,
            [
                ("panels", str(len(panels)), theme.primary),
                ("points", format_metric(float(all_points)), theme.accent),
                ("layout", "2x2", theme.secondary),
            ],
        )
        rects = [(0.075, 0.445, 0.39, 0.28), (0.545, 0.445, 0.39, 0.28), (0.075, 0.135, 0.39, 0.28), (0.545, 0.135, 0.39, 0.28)]
        for index, (panel, rect) in enumerate(zip(panels, rects, strict=False)):
            ax = add_report_axes(fig, canvas, rect, theme)
            x = np.array(panel["x"], dtype=float)
            y = np.array(panel["y"], dtype=float)
            color = theme.palette[index % len(theme.palette)]
            ax.scatter(x, y, s=14, color=color, alpha=0.46, edgecolors="none", zorder=4)
            if len(x) > 2:
                coef = np.polyfit(x, y, deg=1)
                xs = np.linspace(float(np.min(x)), float(np.max(x)), 80)
                ax.plot(xs, coef[0] * xs + coef[1], color=lighten(color, 0.15), lw=2.0, alpha=0.85, zorder=5)
            ax.set_title(str(panel.get("title", "")), color=theme.text, fontsize=10, fontweight="black", loc="left", pad=8)
            ax.set_xlim(*value_range(x))
            ax.set_ylim(*value_range(y))
            style_cartesian_axes(ax, theme, xlabel=str(panel.get("x_label", "")), ylabel=str(panel.get("y_label", "")), x_rotation=0)


class StackedBarChartSkill(BaseLegendSkill):
    legend_type = "stacked_bar_chart"
    display_name = "Rounded Stacked Bar Chart"
    default_style = "wall_street_stack"
    default_size = (1400, 900)
    style_definitions = (
        StyleDefinition("wall_street_stack", "Rounded stacked bar chart for executive reports."),
        StyleDefinition("portfolio_stack", "Portfolio allocation stacked bars with premium theme."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._extract_data(request.data)
        theme = resolve_report_theme(request.data, style)
        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)
        report_text = resolve_report_text(
            request.data,
            request.title,
            request.subtitle,
            default_title="Segment Contribution",
            default_subtitle="Stacked category composition with total ranking",
            default_kicker="Stacked Bar",
            default_footer="NEO LEGEND | STACKED BAR REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )
        self._draw_stacked_bar(fig, canvas, data, theme)
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        if data.get("series"):
            return data
        return {
            "categories": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "series": [
                {"label": "Core", "values": [120, 200, 150, 80, 70, 110, 128]},
                {"label": "Growth", "values": [10, 44, 62, 0, 0, 0, 0]},
                {"label": "Hedge", "values": [28, 0, 0, 18, 8, 0, 0]},
                {"label": "Event", "values": [30, 18, 0, 20, 10, 50, 10]},
            ],
        }

    @staticmethod
    def _draw_stacked_bar(fig: plt.Figure, canvas: plt.Axes, data: dict[str, Any], theme) -> None:
        categories = [str(item) for item in data["categories"]]
        series = data["series"]
        values = np.array([item["values"] for item in series], dtype=float)
        totals = values.sum(axis=0)
        draw_kpi_strip(
            canvas,
            theme,
            [
                ("total", format_metric(float(totals.sum())), theme.primary),
                ("peak", format_metric(float(totals.max())), theme.accent),
                ("avg day", format_metric(float(totals.mean())), theme.secondary),
            ],
        )
        ax = add_report_axes(fig, canvas, (0.075, 0.165, 0.86, 0.55), theme)
        x = np.arange(len(categories))
        width = 0.48
        bottom = np.zeros(len(categories))
        legend_items: list[tuple[str, str]] = []
        for index, item in enumerate(series):
            color = item.get("color") or theme.palette[index % len(theme.palette)]
            legend_items.append((str(item.get("label", f"Series {index + 1}")), color))
            current = np.array(item["values"], dtype=float)
            for col_index, value in enumerate(current):
                if value <= 0:
                    continue
                top_segment = index == len(series) - 1 or np.all(values[index + 1 :, col_index] <= 0)
                boxstyle = "round,pad=0.0,rounding_size=0.16" if top_segment else "square,pad=0.0"
                ax.add_patch(
                    FancyBboxPatch(
                        (x[col_index] - width / 2, bottom[col_index]),
                        width,
                        value,
                        boxstyle=boxstyle,
                        facecolor=color,
                        edgecolor=darken(color, 0.25),
                        linewidth=0.8,
                        alpha=0.94,
                        zorder=4,
                    )
                )
            bottom += current
        for x_pos, total in zip(x, totals, strict=False):
            ax.text(x_pos, total + totals.max() * 0.025, format_metric(float(total)), color=theme.text, fontsize=9, fontweight="black", ha="center")
        ax.set_ylim(0, float(totals.max()) * 1.22)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        style_cartesian_axes(ax, theme, xlabel="Period", ylabel="Contribution")
        draw_series_legend(canvas, theme, legend_items)

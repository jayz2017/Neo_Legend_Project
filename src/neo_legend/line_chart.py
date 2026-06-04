from __future__ import annotations

"""Commercial report line chart renderer."""


from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from neo_legend._plotting import add_canvas, create_figure, save_png
from neo_legend.base import BaseLegendSkill, StyleDefinition
from neo_legend.models import RenderRequest, RenderResult
from neo_legend.report_style import (
    add_footer,
    add_report_axes,
    draw_kpi_strip,
    draw_report_background,
    draw_report_header,
    draw_series_legend,
    format_metric,
    resolve_report_text,
    resolve_report_theme,
    style_cartesian_axes,
    value_range,
)


class LineChartSkill(BaseLegendSkill):
    legend_type = "line_chart"
    display_name = "Luxury Line Chart"
    default_style = "executive_trend"
    default_size = (1400, 900)
    style_definitions = (
        StyleDefinition("executive_trend", "Dark executive trend line with endpoint callouts."),
        StyleDefinition("champagne_forecast", "Warm light report line with benchmark and forecast feel."),
        StyleDefinition("aurora_stream", "High-contrast aurora line chart with multi-series support."),
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
            default_title="Trend Performance",
            default_subtitle="Time-series movement with benchmark context",
            default_kicker="Line Chart",
            default_footer="NEO LEGEND | LINE CHART REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )
        self._render_report_line(fig, canvas, data, theme)
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        categories = data.get("categories", ["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
        series = data.get("series")
        if not series:
            series = [
                {
                    "label": data.get("label", "Performance"),
                    "values": data.get("values", [42, 48, 45, 58, 64, 71]),
                    "color": data.get("color"),
                }
            ]
        return {
            "categories": categories,
            "series": series,
            "x_label": data.get("x_label", "Period"),
            "y_label": data.get("y_label", "Value"),
            "benchmark": data.get("benchmark"),
        }

    def _render_report_line(self, fig: plt.Figure, canvas: plt.Axes, data: dict[str, Any], theme) -> None:
        categories = [str(item) for item in data["categories"]]
        series = data["series"]
        all_values = np.array(
            [float(value) for item in series for value in item.get("values", [])],
            dtype=float,
        )
        ymin, ymax = value_range(all_values)
        yspan = ymax - ymin

        draw_kpi_strip(
            canvas,
            theme,
            [
                ("latest", format_metric(float(series[0]["values"][-1])) if series and series[0].get("values") else "0", theme.primary),
                ("peak", format_metric(float(np.max(all_values))) if all_values.size else "0", theme.accent),
                ("average", format_metric(float(np.mean(all_values))) if all_values.size else "0", theme.secondary),
            ],
        )

        ax = add_report_axes(fig, canvas, (0.075, 0.165, 0.86, 0.55), theme)
        x = np.arange(len(categories))
        legend_items: list[tuple[str, str]] = []
        for index, item in enumerate(series):
            values = np.array([float(value) for value in item.get("values", [])], dtype=float)
            n = min(len(categories), len(values))
            if n == 0:
                continue
            local_x = x[:n]
            local_values = values[:n]
            color = item.get("color") or theme.palette[index % len(theme.palette)]
            legend_items.append((str(item.get("label", f"Series {index + 1}")), color))
            if n > 1:
                smooth_x = np.linspace(float(local_x.min()), float(local_x.max()), 260)
                smooth_y = np.interp(smooth_x, local_x, local_values)
            else:
                smooth_x = local_x.astype(float)
                smooth_y = local_values
            for width, alpha in ((8.0, 0.07), (4.5, 0.18), (2.8, 0.94)):
                ax.plot(smooth_x, smooth_y, color=color, lw=width, alpha=alpha, solid_capstyle="round", zorder=5 + index)
            if index == 0:
                ax.fill_between(smooth_x, smooth_y, ymin, color=color, alpha=0.10, zorder=3)
            ax.scatter(
                local_x,
                local_values,
                s=70,
                color=theme.panel,
                edgecolors=color,
                linewidths=2.0,
                zorder=10,
            )
            peak_index = int(np.argmax(local_values))
            ax.annotate(
                format_metric(float(local_values[peak_index])),
                (local_x[peak_index], local_values[peak_index]),
                textcoords="offset points",
                xytext=(0, 14),
                color=theme.text,
                fontsize=8.5,
                fontweight="bold",
                ha="center",
                bbox={
                    "boxstyle": "round,pad=0.22",
                    "facecolor": theme.panel_alt,
                    "edgecolor": color,
                    "linewidth": 0.8,
                    "alpha": 0.9,
                },
                zorder=12,
            )
            ax.text(
                local_x[-1] + 0.06,
                local_values[-1],
                str(item.get("label", f"Series {index + 1}")),
                color=color,
                fontsize=9,
                fontweight="black",
                ha="left",
                va="center",
                zorder=12,
            )

        benchmark = data.get("benchmark")
        if benchmark is not None:
            benchmark_value = float(benchmark)
            ax.axhline(benchmark_value, color=theme.accent, lw=1.3, ls=(0, (5, 4)), alpha=0.74)
            ax.text(
                len(categories) - 0.45,
                benchmark_value + yspan * 0.018,
                f"Benchmark {format_metric(benchmark_value)}",
                color=theme.accent,
                fontsize=9,
                fontweight="bold",
                ha="right",
                va="bottom",
            )

        ax.set_xlim(-0.25, max(len(categories) - 0.4, 1.0))
        ax.set_ylim(ymin, ymax)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        style_cartesian_axes(
            ax,
            theme,
            xlabel=str(data.get("x_label", "Period")),
            ylabel=str(data.get("y_label", "Value")),
            x_rotation=0 if len(categories) <= 8 else 25,
        )
        draw_series_legend(canvas, theme, legend_items)

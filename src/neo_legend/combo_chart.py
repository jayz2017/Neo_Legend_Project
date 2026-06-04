from __future__ import annotations

"""
奢华组合图渲染器 (Luxury Combo Chart Renderer)
==================================================
功能：柱状图 + 折线图双轴组合，支持 crystal_stream(水晶流)、neon_pulse(霓虹脉冲)、sunset_gradient(日落渐变)、ocean_depths(海洋深度) 四种样式。
特色：twinx() 双 Y 轴、贝塞尔曲线平滑插值、多层辉光效果。
"""


from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._plotting import (
    add_canvas,
    add_reference_footer,
    cmap_color,
    create_figure,
    save_png,
)
from neo_legend.base import BaseLegendSkill, StyleDefinition
from neo_legend.report_style import (
    add_footer,
    add_report_axes,
    draw_kpi_strip,
    draw_report_background,
    draw_report_header,
    draw_series_legend,
    format_metric,
    gradient_colors,
    lighten,
    resolve_report_text,
    resolve_report_theme,
    style_cartesian_axes,
    value_range,
)


class ComboChartSkill(BaseLegendSkill):
    """奢华组合图渲染器 — 柱+线双轴可视化，支持 4 种奢华视觉风格。"""

    legend_type = "combo_chart"            # 图例类型标识
    display_name = "Luxury Combo Chart"     # 显示名称
    default_style = "crystal_stream"      # 默认样式：水晶流
    default_size = (1400, 900)             # 默认输出尺寸（宽 x 高）
    style_definitions = (
        StyleDefinition(
            "crystal_stream",
            "Crystal glow effect with ice-blue bars and golden bezier curve.",
        ),
        StyleDefinition(
            "neon_pulse",
            "Neon tube bars with pulse-ring data points and dashed trend line.",
        ),
        StyleDefinition(
            "sunset_gradient",
            "Warm sunset gradient bars with golden smooth spline curve.",
        ),
        StyleDefinition(
            "ocean_depths",
            "Deep ocean blue bars with wave-modulated cyan line and bubbles.",
        ),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        """主渲染入口：解析样式、提取数据并构建报告风格图表。"""
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
            default_title="Performance Overview",
            default_subtitle="Primary volume with secondary trend signal",
            default_kicker="Combo Chart",
            default_footer="NEO LEGEND | COMBO CHART REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )
        self._render_report_combo(fig, canvas, data, theme)
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    def _render_report_combo(self, fig: plt.Figure, canvas: plt.Axes, data: dict[str, Any], theme) -> None:
        """报告风格组合图核心渲染：构建双 Y 轴（柱+线），绘制渐变柱体与平滑折线。"""
        categories = [str(item) for item in data["categories"]]
        bar_values = np.array(data["bar_values"], dtype=float)
        line_values = np.array(data["line_values"], dtype=float)
        n = min(len(categories), len(bar_values), len(line_values))
        categories = categories[:n]
        bar_values = bar_values[:n]
        line_values = line_values[:n]

        draw_kpi_strip(
            canvas,
            theme,
            [
                ("bar total", format_metric(float(np.sum(bar_values))) if n else "0", theme.primary),
                ("line peak", format_metric(float(np.max(line_values))) if n else "0", theme.accent),
                ("line avg", format_metric(float(np.mean(line_values))) if n else "0", theme.secondary),
            ],
        )

        ax1 = add_report_axes(fig, canvas, (0.075, 0.165, 0.86, 0.55), theme)   # 主轴（柱状图）
        ax2 = ax1.twinx()                                              # 副轴（折线图，共享 X 轴）
        ax2.patch.set_alpha(0)                                         # 副轴背景透明
        x = np.arange(n)
        bar_width = 0.56
        bar_ymin, bar_ymax = value_range(bar_values)                   # 柱状图 Y 轴范围
        line_ymin, line_ymax = value_range(line_values)               # 折线图 Y 轴范围
        bar_span = bar_ymax - bar_ymin

        for idx, (x_pos, value) in enumerate(zip(x, bar_values, strict=False)):
            color = theme.palette[idx % len(theme.palette)]
            ax1.add_patch(
                FancyBboxPatch(                                           # 柱体阴影层
                    (x_pos - bar_width / 2 + 0.035, 0 - bar_span * 0.008),
                    bar_width,
                    float(value),
                    boxstyle="round,pad=0.0,rounding_size=0.035",
                    facecolor="#000000",
                    edgecolor="none",
                    alpha=0.14,
                    zorder=2,
                )
            )
            for step, seg_color in enumerate(gradient_colors(lighten(color, 0.28), color, 24)):
                y0 = float(value) * step / 24                           # 垂直渐变分段
                y1 = float(value) * (step + 1) / 24
                ax1.add_patch(
                    plt.Rectangle(
                        (x_pos - bar_width / 2, y0),
                        bar_width,
                        y1 - y0 + bar_span * 0.0002,
                        facecolor=seg_color,
                        edgecolor="none",
                        alpha=0.88,
                        zorder=4,
                    )
                )
            ax1.text(
                x_pos,
                float(value) + bar_span * 0.025,
                format_metric(float(value)),
                color=theme.text,
                fontsize=8.5,
                fontweight="black",
                ha="center",
                va="bottom",
                zorder=8,
            )

        if n > 1:
            smooth_x = np.linspace(float(x.min()), float(x.max()), 240)   # 高密度插值点（用于平滑曲线）
            smooth_y = np.interp(smooth_x, x, line_values)              # 线性插值作为基线
        else:
            smooth_x = x.astype(float)
            smooth_y = line_values
        for width, alpha in ((7.0, 0.08), (4.2, 0.18), (2.5, 0.92)):       # 多层辉光折线
            ax2.plot(
                smooth_x,
                smooth_y,
                color=theme.accent,
                linewidth=width,
                alpha=alpha,
                solid_capstyle="round",
                zorder=7,
            )
        ax2.fill_between(smooth_x, smooth_y, line_ymin, color=theme.accent, alpha=0.08, zorder=3)
        ax2.scatter(
            x,
            line_values,
            s=72,
            color=theme.panel,
            edgecolors=theme.accent,
            linewidths=2.2,
            zorder=9,
        )
        if n:
            peak_index = int(np.argmax(line_values))                     # 折线峰值点索引
            ax2.annotate(
                f"Peak {format_metric(float(line_values[peak_index]))}",
                (x[peak_index], line_values[peak_index]),
                textcoords="offset points",
                xytext=(0, 18),
                ha="center",
                color=theme.text,
                fontsize=9,
                fontweight="bold",
                bbox={
                    "boxstyle": "round,pad=0.24",
                    "facecolor": theme.panel_alt,
                    "edgecolor": theme.accent,
                    "linewidth": 0.8,
                    "alpha": 0.92,
                },
            )

        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.set_ylim(bar_ymin, bar_ymax)
        ax2.set_ylim(line_ymin, line_ymax)
        style_cartesian_axes(
            ax1,
            theme,
            xlabel=str(data.get("x_label", "Period")),
            ylabel=str(data["bar_label"]),
            x_rotation=0 if n <= 7 else 25,
        )
        ax2.spines["top"].set_visible(False)                            # 隐藏副轴顶部边框
        ax2.spines["left"].set_visible(False)                           # 隐藏副轴左侧边框（与主轴重合）
        ax2.spines["right"].set_color(theme.border)                      # 副轴右侧边框使用主题色
        ax2.tick_params(axis="y", colors=theme.accent, labelsize=10, length=0)
        ax2.set_ylabel(str(data["line_label"]), color=theme.accent, fontsize=11, fontweight="bold", labelpad=10)
        if n:
            ax1.axhline(float(np.mean(bar_values)), color=theme.primary, lw=1.0, ls=(0, (4, 4)), alpha=0.42)
            ax2.axhline(float(np.mean(line_values)), color=theme.accent, lw=1.0, ls=(0, (4, 4)), alpha=0.38)
        draw_series_legend(
            canvas,
            theme,
            [(str(data["bar_label"]), theme.primary), (str(data["line_label"]), theme.accent)],
        )

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        """提取分类、柱状值、折线值及标签；缺失时返回默认演示数据。"""
        return {
            "categories": data.get("categories", ["Jan", "Feb", "Mar", "Apr", "May"]),
            "bar_values": data.get("bar_values", [120, 145, 132, 168, 155]),
            "line_values": data.get("line_values", [45, 52, 48, 62, 58]),
            "bar_label": data.get("bar_label", "Revenue ($K)"),
            "line_label": data.get("line_label", "Growth Rate (%)"),
        }

    # ── Style 1: Crystal Stream ──────────────────────────────────────

    def _render_crystal_stream(self, fig, canvas, data: dict) -> None:
        """水晶流样式：冰蓝渐变柱体 + 金色贝塞尔平滑曲线 + 星形数据点标注。"""
        categories = data["categories"]
        bar_values = np.array(data["bar_values"], dtype=float)
        line_values = np.array(data["line_values"], dtype=float)
        n = len(categories)

        ax1 = fig.add_axes([0.09, 0.13, 0.84, 0.70], facecolor="#16213e")
        ax2 = ax1.twinx()

        x = np.arange(n)
        bar_width = 0.52
        bar_colors = ["#66fcf1", "#45e4c9", "#25cdb3", "#05dfd7", "#00c4b4"][:n]

        for i in range(n):
            gradient_colors = self._vertical_gradient("#66fcf1", "#05dfd7", 60, bottom_alpha=0.7, top_alpha=0.25)
            for j, gc in enumerate(gradient_colors):                       # 60段垂直渐变柱体
                seg_height = bar_values[i] / len(gradient_colors)
                rect = plt.Rectangle(
                    (x[i] - bar_width / 2, j * seg_height),
                    bar_width,
                    seg_height,
                    facecolor=gc,
                    edgecolor="none",
                    zorder=3,
                )
                ax1.add_patch(rect)
            top_rect = FancyBboxPatch(                                    # 顶部圆角封口
                (x[i] - bar_width / 2, bar_values[i]),
                bar_width,
                0,
                boxstyle="round,pad=0.02,rounding_size=0.5",
                facecolor="#66fcf1",
                edgecolor="none",
                alpha=0.35,
                zorder=4,
            )
            ax1.add_patch(top_rect)

        smooth_x = np.linspace(x.min(), x.max(), 300)                    # 300 点高密度采样
        try:
            from scipy.interpolate import make_interp_spline
            spl = make_interp_spline(x, line_values, k=min(3, n - 1))  # 三次 B 样条（贝塞尔）插值
            smooth_y = spl(smooth_x)
        except Exception:
            smooth_y = np.interp(smooth_x, x, line_values)           # 回退到线性插值

        line_color = "#ffd700"

        for lw, alpha in [(6, 0.06), (3.5, 0.18), (1.8, 0.75)]:
            ax2.plot(smooth_x, smooth_y, color=line_color, linewidth=lw, alpha=alpha, solid_capstyle="round", zorder=6)

        ax2.fill_between(smooth_x, smooth_y, alpha=0.08, color=line_color, zorder=2)

        for i, (xi, yi) in enumerate(zip(x, line_values)):
            ax2.plot(xi, yi, marker="*", markersize=15, color="#fff", markeredgecolor=line_color, markeredgewidth=2.2, zorder=8)
            bbox_props = dict(boxstyle="round,pad=0.25", facecolor="#1a2744", edgecolor=line_color, alpha=0.88, linewidth=1)
            ax2.annotate(f"{yi:.0f}", (xi, yi), textcoords="offset points", xytext=(0, 16), fontsize=10, color="#fff", ha="center", va="bottom", fontweight="bold", bbox=bbox_props, zorder=9)

        self._apply_crystal_axis_style(ax1, ax2, categories, bar_values, line_values, data["bar_label"], data["line_label"])
        self._draw_legend_box(canvas, [
            ("\u25a0", "#66fcf1", data["bar_label"]),
            ("\u2501", "#ffd700", data["line_label"]),
        ], y=0.068)

    @staticmethod
    def _apply_crystal_axis_style(ax1, ax2, categories, bar_vals, line_vals, bar_label, line_label) -> None:
        """应用水晶流样式轴配置：深蓝背景、双色坐标轴。"""
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels(categories, color="#a0c4d4", fontsize=13, fontweight="medium")
        ax1.set_ylabel(bar_label, color="#66fcf1", fontsize=13, fontweight="bold", labelpad=12)
        ax2.set_ylabel(line_label, color="#ffd700", fontsize=13, fontweight="bold", labelpad=12)
        ax1.tick_params(axis="y", colors="#66fcf1", labelsize=11)
        ax2.tick_params(axis="y", colors="#ffd700", labelsize=11)
        ax1.set_ylim(0, max(bar_vals) * 1.22)
        ax2.set_ylim(0, max(line_vals) * 1.35)
        for spine in ax1.spines.values():
            spine.set_color("#2a4066")
            spine.set_linewidth(1.2)
        for spine in ax2.spines.values():
            spine.set_color("#2a4066")
            spine.set_linewidth(1.2)
        ax1.grid(axis="y", color="#1e3a5f", linewidth=0.6, alpha=0.5, linestyle="-", zorder=0)
        ax1.set_axisbelow(True)

    # ── Style 2: Neon Pulse ──────────────────────────────────────────

    def _render_neon_pulse(self, fig, canvas, data: dict) -> None:
        """霓虹脉冲样式：黑色背景、发光边框柱体、脉冲环数据点、趋势箭头指示。"""
        categories = data["categories"]
        bar_values = np.array(data["bar_values"], dtype=float)
        line_values = np.array(data["line_values"], dtype=float)
        n = len(categories)

        fig.patch.set_facecolor("#0a0a0a")
        canvas.patch.set_facecolor("#0a0a0a")

        ax1 = fig.add_axes([0.09, 0.13, 0.84, 0.70], facecolor="#0a0a0a")
        ax2 = ax1.twinx()

        x = np.arange(n)
        bar_width = 0.50
        neon_colors = ["#ff0055", "#00ff99", "#00ccff", "#ffcc00", "#ff00ff"]
        neon_colors = (neon_colors * ((n // len(neon_colors)) + 1))[:n]

        for i in range(n):
            nc = neon_colors[i]
            for glow_w, glow_a in [(5, 0.08), (3, 0.15), (1.5, 0.4)]:      # 多层发光边框
                glow_rect = plt.Rectangle(
                    (x[i] - bar_width / 2 - glow_w * 0.01, 0),
                    bar_width + glow_w * 0.02,
                    bar_values[i],
                    facecolor="none",
                    edgecolor=nc,
                    linewidth=glow_w,
                    alpha=glow_a,
                    zorder=3,
                )
                ax1.add_patch(glow_rect)
            inner_rect = plt.Rectangle(                                   # 半透明内核
                (x[i] - bar_width / 2 + 0.03, 0.02),
                bar_width - 0.06,
                bar_values[i] - 0.04,
                facecolor=nc,
                alpha=0.12,
                edgecolor="none",
                zorder=4,
            )
            ax1.add_patch(inner_rect)
            border_rect = plt.Rectangle(                                  # 实色边框轮廓
                (x[i] - bar_width / 2, 0),
                bar_width,
                bar_values[i],
                facecolor="none",
                edgecolor=nc,
                linewidth=2.2,
                alpha=0.92,
                zorder=5,
            )
            ax1.add_patch(border_rect)

        smooth_x = np.linspace(x.min(), x.max(), 300)
        try:
            from scipy.interpolate import make_interp_spline
            spl = make_interp_spline(x, line_values, k=min(3, n - 1))
            smooth_y = spl(smooth_x)
        except Exception:
            smooth_y = np.interp(smooth_x, x, line_values)

        accent_color = "#ffff00"
        ax2.plot(smooth_x, smooth_y, color=accent_color, linewidth=2.2, linestyle=(0, (8, 4)), zorder=7, solid_capstyle="round")

        peak_idx = int(np.argmax(line_values))
        px, py = float(x[peak_idx]), float(line_values[peak_idx])
        for r_factor, ring_a in [(1.8, 0.06), (1.3, 0.12), (0.85, 0.22)]:   # 峰值脉冲环
            circle = plt.Circle((px, py), r_factor * 2, fill=False, edgecolor=accent_color, linewidth=1.2, alpha=ring_a, zorder=6)
            ax2.add_patch(circle)

        for i, (xi, yi) in enumerate(zip(x, line_values)):
            for r_factor, ring_a in [(1.6, 0.07), (1.1, 0.15), (0.6, 0.35)]:   # 各数据点脉冲环
                circle = plt.Circle((xi, yi), r_factor * 1.8, fill=False, edgecolor=accent_color, linewidth=0.9, alpha=ring_a, zorder=6)
                ax2.add_patch(circle)
            ax2.plot(xi, yi, "o", markersize=7, color=accent_color, markeredgecolor="#fff", markeredgewidth=1.2, zorder=9)

            if i < n - 1:
                dy = line_values[i + 1] - line_values[i]                 # 相邻点差值判断趋势
                arrow_dir = "up" if dy > 0 else "down" if dy < 0 else None
                if arrow_dir:
                    mid_x = (xi + x[i + 1]) / 2
                    mid_y = (yi + line_values[i + 1]) / 2
                    symbol = "\u25b2" if arrow_dir == "up" else "\u25bc"
                    sym_color = "#00ff88" if arrow_dir == "up" else "#ff4466"
                    ax2.text(mid_x, mid_y + (2 if arrow_dir == "up" else -2.5), symbol, color=sym_color, fontsize=11, ha="center", va="center", fontweight="bold", zorder=10)

        self._apply_neon_axis_style(ax1, ax2, categories, bar_values, line_values, data["bar_label"], data["line_label"])
        self._draw_legend_box(canvas, [
            ("\u25a1", "#ff0055", data["bar_label"]),
            ("\u2505", "#ffff00", data["line_label"]),
        ], y=0.068, bg="#0a0a0a")

    @staticmethod
    def _apply_neon_axis_style(ax1, ax2, categories, bar_vals, line_vals, bar_label, line_label) -> None:
        """应用霓虹脉冲样式轴配置。"""
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels(categories, color="#ccddff", fontsize=13, fontweight="medium")
        ax1.set_ylabel(bar_label, color="#ff0055", fontsize=13, fontweight="bold", labelpad=12)
        ax2.set_ylabel(line_label, color="#ffff00", fontsize=13, fontweight="bold", labelpad=12)
        ax1.tick_params(axis="y", colors="#ff0055", labelsize=11)
        ax2.tick_params(axis="y", colors="#ffff00", labelsize=11)
        ax1.set_ylim(0, max(bar_vals) * 1.22)
        ax2.set_ylim(0, max(line_vals) * 1.35)
        for spine in ax1.spines.values():
            spine.set_color("#333344")
            spine.set_linewidth(1.3)
        for spine in ax2.spines.values():
            spine.set_color("#333344")
            spine.set_linewidth(1.3)
        ax1.grid(axis="y", color="#1a1a2e", linewidth=0.65, alpha=0.55, linestyle="--", zorder=0)
        ax1.set_axisbelow(True)

    # ── Style 3: Sunset Gradient ─────────────────────────────────────

    def _render_sunset_gradient(self, fig, canvas, data: dict) -> None:
        """日落渐变样式：暖色背景渐变、红橙渐变柱体、金色平滑曲线、太阳光晕装饰。"""
        categories = data["categories"]
        bar_values = np.array(data["bar_values"], dtype=float)
        line_values = np.array(data["line_values"], dtype=float)
        n = len(categories)

        ax1 = fig.add_axes([0.09, 0.13, 0.84, 0.70])
        ax2 = ax1.twinx()

        gradient = np.linspace(0, 1, 256).reshape(1, -1)
        ax1.imshow(gradient, aspect="auto", cmap=self._make_cmap(["#2c3e50", "#e74c3c", "#f39c12"]), extent=[-0.6, n - 0.4, 0, max(bar_values) * 1.22], alpha=0.20, zorder=0, origin="lower")

        x = np.arange(n)
        bar_width = 0.50
        sunset_bar_colors = ["#f39c12", "#e74c3c", "#c0392b", "#d35400", "#e67e22"]
        sunset_bar_colors = (sunset_bar_colors * ((n // len(sunset_bar_colors)) + 1))[:n]

        for i in range(n):
            grad_colors = self._vertical_gradient(sunset_bar_colors[i], "#c0392b", 50, bottom_alpha=0.82, top_alpha=0.48)
            seg_h = bar_values[i] / len(grad_colors)
            for j, gc in enumerate(grad_colors):
                rect = plt.Rectangle(
                    (x[i] - bar_width / 2, j * seg_h),
                    bar_width,
                    seg_h,
                    facecolor=gc,
                    edgecolor="none",
                    zorder=3,
                )
                ax1.add_patch(rect)

        smooth_x = np.linspace(x.min(), x.max(), 300)
        try:
            from scipy.interpolate import make_interp_spline
            spl = make_interp_spline(x, line_values, k=min(3, n - 1))
            smooth_y = spl(smooth_x)
        except Exception:
            smooth_y = np.interp(smooth_x, x, line_values)

        gold = "#ffd700"
        ax2.fill_between(smooth_x, smooth_y, alpha=0.12, color=gold, zorder=2)
        ax2.plot(smooth_x, smooth_y, color=gold, linewidth=3.5, solid_capstyle="round", zorder=7)

        avg_val = np.mean(line_values)
        ax2.axhline(y=avg_val, color=gold, linewidth=1, linestyle=":", alpha=0.35, zorder=1)
        ax2.text(n - 0.35, avg_val + 1, f"Avg: {avg_val:.1f}", color=gold, fontsize=9, alpha=0.6, va="bottom", fontweight="bold")

        for i, (xi, yi) in enumerate(zip(x, line_values)):
            ax2.plot(xi, yi, "o", markersize=12, color="#fff", markeredgecolor=gold, markeredgewidth=2.5, zorder=9)
            bbox_props = dict(boxstyle="round,pad=0.22", facecolor="#4a2c20", edgecolor=gold, alpha=0.85, linewidth=1)
            ax2.annotate(f"{yi:.0f}", (xi, yi), textcoords="offset points", xytext=(0, 14), fontsize=10, color="#fffef0", ha="center", va="bottom", fontweight="bold", bbox=bbox_props, zorder=10)

        sun_x, sun_y = n - 0.55, max(line_values) * 1.12
        for sr, sa in [(0.28, 0.04), (0.20, 0.08), (0.13, 0.15), (0.07, 0.30)]:   # 太阳光晕（多层同心圆）
            sun_glow = plt.Circle((sun_x, max(bar_values) * 1.02 + 2), sr * (max(bar_values) * 0.08), color="#ffd700", alpha=sa, zorder=1)
            ax1.add_patch(sun_glow)

        self._apply_sunset_axis_style(ax1, ax2, categories, bar_values, line_values, data["bar_label"], data["line_label"])
        self._draw_legend_box(canvas, [
            ("\u25a0", "#e74c3c", data["bar_label"]),
            ("\u2501", "#ffd700", data["line_label"]),
        ], y=0.068)

    @staticmethod
    def _apply_sunset_axis_style(ax1, ax2, categories, bar_vals, line_vals, bar_label, line_label) -> None:
        """应用日落渐变样式轴配置。"""
        ax1.set_facecolor("#1a1a2e")
        ax2.set_facecolor("none")
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels(categories, color="#f5deb3", fontsize=13, fontweight="medium")
        ax1.set_ylabel(bar_label, color="#e74c3c", fontsize=13, fontweight="bold", labelpad=12)
        ax2.set_ylabel(line_label, color="#ffd700", fontsize=13, fontweight="bold", labelpad=12)
        ax1.tick_params(axis="y", colors="#e74c3c", labelsize=11)
        ax2.tick_params(axis="y", colors="#ffd700", labelsize=11)
        ax1.set_ylim(0, max(bar_vals) * 1.22)
        ax2.set_ylim(0, max(line_vals) * 1.35)
        for spine in ax1.spines.values():
            spine.set_color("#5c3a3a")  # 设置坐标轴边框颜色为深红褐色
            spine.set_linewidth(1.2)      # 边框线宽
        for spine in ax2.spines.values():
            spine.set_color("#5c3a3a")  # 设置副坐标轴边框颜色
            spine.set_linewidth(1.2)      # 副轴边框线宽
        ax1.grid(axis="y", color="#3d2a1a", linewidth=0.6, alpha=0.45, linestyle="-", zorder=0)
        ax1.set_axisbelow(True)

    # ── Style 4: Ocean Depths ─────────────────────────────────────────

    def _render_ocean_depths(self, fig, canvas, data: dict) -> None:
        """海洋深度样式：深海蓝背景、波浪调制折线、气泡装饰、青色光晕数据点。"""
        categories = data["categories"]
        bar_values = np.array(data["bar_values"], dtype=float)
        line_values = np.array(data["line_values"], dtype=float)
        n = len(categories)

        ax1 = fig.add_axes([0.09, 0.13, 0.84, 0.70])
        ax2 = ax1.twinx()

        gradient = np.linspace(0, 1, 256).reshape(-1, 1)
        ax1.imshow(gradient, aspect="auto", cmap=self._make_cmap(["#0a1628", "#1a3a52", "#2e86ab"]), extent=[-0.6, n - 0.4, 0, max(bar_values) * 1.22], alpha=0.30, zorder=0, origin="lower")

        x = np.arange(n)
        bar_width = 0.50
        ocean_colors = ["#0077b6", "#00b4d8", "#48cae4", "#90e0ef", "#ade8f4"]
        ocean_colors = (ocean_colors * ((n // len(ocean_colors)) + 1))[:n]

        for i in range(n):
            depth_factor = (i + 1) / n                                 # 深度因子：越靠后的柱子越深/越不透明
            base_alpha = 0.45 + depth_factor * 0.35
            grad_colors = self._vertical_gradient(ocean_colors[i], "#0077b6", 45, bottom_alpha=base_alpha, top_alpha=base_alpha * 0.55)
            seg_h = bar_values[i] / len(grad_colors)
            for j, gc in enumerate(grad_colors):
                wave_offset = 0.4 * np.sin(j * 0.4 + i * 1.2) * (seg_h * 0.15)   # 正弦波偏移模拟水波
                rect = plt.Rectangle(
                    (x[i] - bar_width / 2, j * seg_h + wave_offset),
                    bar_width,
                    seg_h,
                    facecolor=gc,
                    edgecolor="none",
                    zorder=3,
                )
                ax1.add_patch(rect)

        smooth_x = np.linspace(x.min(), x.max(), 400)
        try:
            from scipy.interpolate import make_interp_spline
            spl = make_interp_spline(x, line_values, k=min(3, n - 1))
            base_smooth_y = spl(smooth_x)
        except Exception:
            base_smooth_y = np.interp(smooth_x, x, line_values)

        amplitude = max(line_values) * 0.025                               # 波浪振幅
        frequency = 2.5                                                # 波浪频率
        wave_y = base_smooth_y + amplitude * np.sin(frequency * smooth_x)  # 正弦调制

        cyan = "#00f5d4"
        ax2.plot(smooth_x, wave_y, color=cyan, linewidth=2.8, solid_capstyle="round", zorder=7)
        ax2.fill_between(smooth_x, wave_y, alpha=0.10, color=cyan, zorder=2)

        rng = np.random.default_rng(seed=42)
        n_bubbles = 15
        for _ in range(n_bubbles):                                     # 随机气泡装饰
            bx = rng.uniform(-0.4, n - 0.6)
            by = rng.uniform(min(line_values) * 0.3, max(bar_values) * 0.75)
            br = rng.uniform(0.15, 0.9)
            ba = rng.uniform(0.08, 0.24)
            bc = rng.choice(["#ffffff", "#ade8f4", "#90e0ef", "#48cae4"])
            bubble = plt.Circle((bx, by), br, facecolor=bc, edgecolor="none", alpha=ba, zorder=1)
            ax1.add_patch(bubble)

        for i, (xi, yi) in enumerate(zip(x, line_values)):
            for br_factor, balpha in [(1.4, 0.10), (0.9, 0.20), (0.5, 0.38)]:  # 数据点光晕
                halo = plt.Circle((xi, yi), br_factor * 2.2, facecolor="none", edgecolor=cyan, linewidth=0.8, alpha=balpha, zorder=5)
                ax2.add_patch(halo)
            ax2.plot(xi, yi, "o", markersize=9, color="#0a1628", markeredgecolor=cyan, markeredgewidth=2.2, zorder=9)
            bbox_props = dict(boxstyle="round,pad=0.22", facecolor="#0d2137", edgecolor=cyan, alpha=0.86, linewidth=1)
            ax2.annotate(f"{yi:.0f}", (xi, yi), textcoords="offset points", xytext=(0, 14), fontsize=10, color="#e0ffff", ha="center", va="bottom", fontweight="bold", bbox=bbox_props, zorder=10)

        self._apply_ocean_axis_style(ax1, ax2, categories, bar_values, line_values, data["bar_label"], data["line_label"])
        self._draw_legend_box(canvas, [
            ("\u25a0", "#00b4d8", data["bar_label"]),
            ("\u2501", "#00f5d4", data["line_label"]),
        ], y=0.068)

    @staticmethod
    def _apply_ocean_axis_style(ax1, ax2, categories, bar_vals, line_vals, bar_label, line_label) -> None:
        """应用海洋深度样式轴配置。"""
        ax1.set_facecolor("#0a1628")
        ax2.set_facecolor("none")
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels(categories, color="#90e0ef", fontsize=13, fontweight="medium")
        ax1.set_ylabel(bar_label, color="#00b4d8", fontsize=13, fontweight="bold", labelpad=12)
        ax2.set_ylabel(line_label, color="#00f5d4", fontsize=13, fontweight="bold", labelpad=12)
        ax1.tick_params(axis="y", colors="#00b4d8", labelsize=11)
        ax2.tick_params(axis="y", colors="#00f5d4", labelsize=11)
        ax1.set_ylim(0, max(bar_vals) * 1.22)
        ax2.set_ylim(0, max(line_vals) * 1.35)
        for spine in ax1.spines.values():
            spine.set_color("#1a3a52")  # 深蓝色边框
            spine.set_linewidth(1.2)
        for spine in ax2.spines.values():
            spine.set_color("#1a3a52")  # 副轴深蓝边框
            spine.set_linewidth(1.2)
        ax1.grid(axis="y", color="#163250", linewidth=0.55, alpha=0.45, linestyle="-", zorder=0)
        ax1.set_axisbelow(True)

    # ── Shared Helpers ────────────────────────────────────────────────

    @staticmethod
    def _vertical_gradient(top_color: str, bottom_color: str, steps: int, bottom_alpha: float = 1.0, top_alpha: float = 1.0) -> list[str]:
        """生成垂直渐变色列表：从底部颜色过渡到顶部颜色，同时控制透明度变化。"""
        from matplotlib.colors import to_rgb, to_hex
        t_rgb = np.array(to_rgb(top_color))
        b_rgb = np.array(to_rgb(bottom_color))
        colors = []
        for i in range(steps):
            frac = i / max(steps - 1, 1)
            rgb = b_rgb + (t_rgb - b_rgb) * frac                         # RGB 线性插值
            alpha = bottom_alpha + (top_alpha - bottom_alpha) * frac       # Alpha 线性插值
            r, g, b = rgb
            hex_color = to_hex((r, g, b, alpha))
            colors.append(hex_color)
        return colors

    @staticmethod
    def _make_cmap(colors: list[str]):
        """从颜色列表创建 LinearSegmentedColormap 对象。"""
        from matplotlib.colors import LinearSegmentedColormap
        return LinearSegmentedColormap.from_list("_tmp", colors)

    @staticmethod
    def _draw_legend_box(canvas, items: list[tuple[str, str, str]], y: float, bg: str = "#16213e") -> None:
        """绘制自定义图例框：带背景色的符号+标签行。"""
        n_items = len(items)
        total_w = min(n_items * 0.22, 0.65)
        start_x = 0.5 - total_w / 2
        item_spacing = total_w / n_items if n_items > 1 else 0

        legend_bg = plt.Rectangle((start_x - 0.025, y - 0.018), total_w + 0.05, 0.042, facecolor=bg, edgecolor="#3a4a6a", linewidth=0.8, alpha=0.75, zorder=12, transform=canvas.transAxes, clip_on=False)
        canvas.add_patch(legend_bg)

        for idx, (symbol, color, label) in enumerate(items):
            lx = start_x + idx * item_spacing + item_spacing * 0.08
            ly = y + 0.002
            canvas.text(lx, ly, symbol, color=color, fontsize=14, fontweight="bold", ha="left", va="center", zorder=13)
            canvas.text(lx + 0.026, ly, label, color="#c8d4e4", fontsize=11, ha="left", va="center", zorder=13)

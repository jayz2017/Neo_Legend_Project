from __future__ import annotations

"""
华丽雷达图渲染器 (Luxury Radar Chart Renderer)
==================================================
功能：多维度蜘蛛网雷达图，支持 neon_glow(霓虹发光)、crystal_metal(晶体金属)、gradient_rainbow(彩虹渐变) 三种奢华样式。
特色：多层辉光效果、金属质感渐变、HSV 色彩过渡。
"""


import colorsys
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyBboxPatch, PathPatch
from matplotlib.path import Path

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._plotting import (
    add_canvas,
    add_reference_footer,
    create_figure,
    make_gradient,
    save_png,
    seeded_rng,
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
    resolve_report_text,
    resolve_report_theme,
)


class RadarChartSkill(BaseLegendSkill):
    """华丽雷达图渲染器 — 极坐标系多维数据可视化，支持 3 种霓虹/金属/彩虹视觉风格。"""

    legend_type = "radar_chart"         # 图例类型标识
    display_name = "Luxury Radar Chart" # 显示名称
    default_style = "neon_glow"        # 默认样式：霓虹发光
    default_size = (1200, 1400)        # 默认输出尺寸（宽 x 高）
    style_definitions = (
        StyleDefinition("neon_glow", "Neon glow effect with deep dark background and luminous lines."),
        StyleDefinition(
            "crystal_metal",
            "Crystal metallic texture with silver gradients and reflective highlights.",
        ),
        StyleDefinition("gradient_rainbow", "Rainbow gradient with HSV color transitions and star markers."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        """主渲染入口：解析样式并委托给 PNG 渲染管线。"""
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        content = self._render_png(request, style, width, height)
        return self.result(content, style)

    def _render_png(self, request: RenderRequest, style: str, width: int, height: int) -> bytes:
        """报告风格雷达图主渲染管线：构建极坐标轴、绘制数据多边形及装饰元素。"""
        data = self._extract_data(request.data)
        categories = data["categories"]
        datasets = data["datasets"]
        theme = resolve_report_theme(request.data, style)
        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)

        report_text = resolve_report_text(
            request.data,
            request.title,
            request.subtitle,
            default_title="PLAYER RADAR PROFILE",
            default_subtitle="MULTIDIMENSIONAL ANALYSIS",
            default_kicker="Radar Profile",
            default_footer="NEO LEGEND | RADAR PROFILE REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )

        all_values = np.array(
            [float(value) for dataset in datasets for value in dataset.get("values", [])],
            dtype=float,
        )
        draw_kpi_strip(
            canvas,
            theme,
            [
                ("dimensions", str(len(categories)), theme.primary),
                ("top score", format_metric(float(np.max(all_values))) if all_values.size else "0", theme.accent),
                ("average", format_metric(float(np.mean(all_values))) if all_values.size else "0", theme.secondary),
            ],
        )

        radar_ax = add_report_axes(fig, canvas, (0.125, 0.165, 0.75, 0.56), theme, polar=True)

        n_cats = len(categories)
        angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()   # 均匀分布角度（弧度）
        angles += angles[:1]                     # 首尾相接，形成闭合路径
        max_observed = float(np.max(all_values)) if all_values.size else 100.0
        max_value = float(data.get("max_value") or max(max_observed * 1.12, 100.0))

        radar_ax.set_theta_offset(np.pi / 2)      # 角度偏移 π/2，使第一个维度指向正上方（12点钟方向）
        radar_ax.set_theta_direction(-1)          # 顺时针方向排列维度
        radar_ax.set_ylim(0, max_value)
        radar_ax.set_xticks(angles[:-1])
        radar_ax.set_xticklabels([str(category).upper() for category in categories])
        radar_ax.tick_params(axis="x", colors=theme.text, labelsize=10, pad=10)
        for tick in radar_ax.get_xticklabels():
            tick.set_fontweight("bold")
        ring_values = np.linspace(max_value / 4, max_value, 4)     # 同心圆环刻度值（25%、50%、75%、100%）
        radar_ax.set_yticks(ring_values)
        radar_ax.set_yticklabels([format_metric(value) for value in ring_values], color=theme.muted, fontsize=8)
        radar_ax.grid(color=theme.grid, lw=0.9, alpha=0.52)
        radar_ax.spines["polar"].set_color(theme.border)
        radar_ax.spines["polar"].set_linewidth(1.2)
        radar_ax.set_facecolor(theme.panel)

        legend_items: list[tuple[str, str]] = []
        for index, dataset in enumerate(datasets):
            values = [float(value) for value in dataset["values"][:n_cats]]
            if len(values) < n_cats:
                values.extend([0.0] * (n_cats - len(values)))       # 数据不足时补零
            closed_values = values + values[:1]                      # 闭合多边形（首尾点重合）
            color = dataset.get("color") or theme.palette[index % len(theme.palette)]
            legend_items.append((str(dataset.get("label", f"Series {index + 1}")).upper(), color))
            for width_line, alpha in ((7.0, 0.07), (4.2, 0.18), (2.6, 0.96)):
                radar_ax.plot(
                    angles,
                    closed_values,
                    color=color,
                    linewidth=width_line,
                    alpha=alpha,
                    solid_capstyle="round",
                    zorder=5 + index,
                )
            radar_ax.fill(angles, closed_values, color=color, alpha=0.12, zorder=3)
            radar_ax.scatter(
                angles[:-1],
                values,
                color=theme.panel,
                edgecolors=color,
                s=64,
                linewidths=2,
                zorder=12,
            )
            if n_cats <= 7:
                for angle, value in zip(angles[:-1], values, strict=False):
                    radar_ax.text(
                        angle,
                        min(value + max_value * 0.045, max_value * 1.02),   # 标签偏移量随数值自适应
                        format_metric(value),
                        color=color,
                        fontsize=8,
                        fontweight="bold",
                        ha="center",
                        va="center",
                        zorder=13,
                    )

        draw_series_legend(canvas, theme, legend_items, y=0.095)
        add_footer(canvas, theme, report_text.footer)
        return save_png(fig)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        """从请求数据中提取分类和序列；若无有效数据则生成随机演示数据。"""
        if data.get("categories") and data.get("datasets"):
            return data

        rng = seeded_rng(42)
        categories = data.get("categories", ["Score", "Rebound", "Assist", "Steal", "Block"])
        n_cats = len(categories)
        base_colors = ["#ff6b6b", "#4ecdc4", "#ffe66d", "#95e1d3", "#f38181"]
        datasets = [
            {
                "label": f"Player {chr(65 + i)}",
                "values": [int(rng.integers(50, 98)) for _ in range(n_cats)],
                "color": base_colors[i % len(base_colors)],
            }
            for i in range(2)
        ]
        return {"categories": categories, "datasets": datasets}

    def _draw_neon_glow(
        self,
        ax: plt.Axes,
        categories: list[str],
        datasets: list[dict],
        angles: list[float],
        n_cats: int,
    ) -> None:
        """霓虹发光样式渲染：多层线条叠加产生辉光效果，配合彩色维度标签。"""
        ax.set_facecolor("#0a0a1a")

        grid_levels = 5
        for level in range(grid_levels, 0, -1):
            radius = level * 20                          # 同心网格半径递增
            values_grid = [radius] * (n_cats + 1)
            alpha_grid = 0.06 + (grid_levels - level) * 0.03   # 外层更透明
            lw_grid = 0.5 + (grid_levels - level) * 0.2         # 外层线宽更细
            ax.plot(angles, values_grid, color="#3a3a6a", linewidth=lw_grid, alpha=alpha_grid)

        for i, angle in enumerate(angles[:-1]):
            ax.plot([angle, angle], [0, 100], color="#2a2a5a", linewidth=0.8, alpha=0.25)

        neon_colors = ["#00ffff", "#ff00ff", "#ffff00", "#00ff88", "#ff6688"]
        for i, cat in enumerate(categories):
            angle_rad = angles[i]
            x_text = 1.18 * np.cos(angle_rad - np.pi / 2)    # 极坐标→笛卡尔坐标 X
            y_text = 1.18 * np.sin(angle_rad - np.pi / 2)    # 极坐标→笛卡尔坐标 Y
            color = neon_colors[i % len(neon_colors)]
            ax.text(
                angle_rad,
                108,
                cat.upper(),
                color=color,
                fontsize=13,
                fontweight="bold",
                ha="center",
                va="center",
                family="sans-serif",
            )
            ax.text(
                angle_rad,
                108,
                cat.upper(),
                color=color,
                fontsize=13,
                fontweight="bold",
                ha="center",
                va="center",
                family="sans-serif",
                alpha=0.4,
                zorder=1,
            )

        for dataset in datasets:
            values = dataset["values"] + dataset["values"][:1]    # 闭合路径
            color = dataset["color"]

            for lw, alpha in [(4, 0.15), (2.5, 0.4), (1, 0.9)]:
                ax.plot(angles, values, color=color, linewidth=lw, alpha=alpha, solid_capstyle="round")

            fill_alphas = [0.25, 0.12, 0.06]
            for fill_alpha in fill_alphas:
                ax.fill(angles, values, color=color, alpha=fill_alpha)

            for j, (angle, value) in enumerate(zip(angles[:-1], dataset["values"])):
                for size, a in [(25, 0.3), (16, 0.6), (9, 1.0)]:
                    ax.scatter(
                        [angle],
                        [value],
                        s=size,
                        c=[color],
                        edgecolors=["#ffffff"],
                        linewidths=1.2 if size == 9 else 0,
                        alpha=a,
                        zorder=10,
                    )

    def _draw_crystal_metal(
        self,
        ax: plt.Axes,
        categories: list[str],
        datasets: list[dict],
        angles: list[float],
        n_cats: int,
    ) -> None:
        """晶体金属样式渲染：银/金/铜三色渐变填充、菱形数据点、峰值高亮椭圆。"""
        ax.set_facecolor("#1a1a2e")

        grid_levels = 5
        for level in range(grid_levels, 0, -1):
            radius = level * 20
            values_grid = [radius] * (n_cats + 1)
            intensity = 0.15 + (grid_levels - level) * 0.08
            gray = int(80 + (grid_levels - level) * 20)
            grid_color = f"#{gray:02x}{gray:02x}{gray:02x}"
            ax.plot(angles, values_grid, color=grid_color, linewidth=1.0, alpha=intensity)

        for i, angle in enumerate(angles[:-1]):
            ax.plot([angle, angle], [0, 100], color="#555577", linewidth=0.8, alpha=0.3)

        for i, cat in enumerate(categories):
            angle_rad = angles[i]
            ax.text(
                angle_rad,
                108,
                cat.upper(),
                color="#e0e0e0",
                fontsize=13,
                fontweight="bold",
                ha="center",
                va="center",
                family="serif",
            )

        metal_gradients = {
            "default": make_gradient(["#c0c0c0", "#ffffff", "#e8e8e8"], "silver"),
            "gold": make_gradient(["#d4af37", "#ffd700", "#daa520"], "gold"),
            "bronze": make_gradient(["#cd7f32", "#ffaa33", "#b87333"], "bronze"),
        }

        for d_idx, dataset in enumerate(datasets):
            values = dataset["values"] + dataset["values"][:1]
            color = dataset["color"]

            gradient_name = ["default", "gold", "bronze"][d_idx % 3]
            cmap = metal_gradients[gradient_name]

            n_points = len(values)
            for j in range(n_points - 1):                              # 逐段着色实现金属渐变
                seg_values = values[j : j + 2]
                seg_angles = angles[j : j + 2]
                segment_color = cmap(j / max(n_points - 2, 1))
                ax.fill(seg_angles, seg_values, color=segment_color, alpha=0.7)
                ax.plot(seg_angles, seg_angles if False else seg_values, color="#d4af37", linewidth=2, solid_capstyle="round")

            max_value_idx = dataset["values"].index(max(dataset["values"]))   # 定位最高得分维度
            peak_angle = angles[max_value_idx]
            peak_value = dataset["values"][max_value_idx]

            highlight = Ellipse(
                xy=(peak_angle, peak_value),
                width=0.15,
                height=6,
                angle=0,
                facecolor="#ffffff",
                edgecolor="none",
                alpha=0.6,
                zorder=15,
            )
            ax.add_patch(highlight)

            arc_angles = np.linspace(peak_angle - 0.12, peak_angle + 0.12, 30)
            arc_radii = peak_value + 3 * np.cos(np.linspace(0, np.pi, 30)) - 1   # 弧形高光轨迹
            ax.plot(arc_angles, arc_radii, color="#ffffff", linewidth=2, alpha=0.7, zorder=14)

            for j, (angle, value) in enumerate(zip(angles[:-1], dataset["values"])):
                diamond_size = 100 + (value / 100) * 60           # 菱形大小随数值缩放
                ax.scatter(
                    [angle],
                    [value],
                    s=diamond_size,
                    marker="D",
                    c=[color],
                    edgecolors=["#ffffff"],
                    linewidths=1.5,
                    alpha=0.95,
                    zorder=12,
                )
                inner_gray = int(200 + (value / 100) * 55)
                ax.scatter(
                    [angle],
                    [value],
                    s=diamond_size * 0.35,
                    marker="D",
                    c=[f"#{inner_gray:02x}{inner_gray:02x}{inner_gray:02x}"],
                    edgecolors="none",
                    alpha=0.8,
                    zorder=13,
                )

    def _draw_gradient_rainbow(
        self,
        ax: plt.Axes,
        categories: list[str],
        datasets: list[dict],
        angles: list[float],
        n_cats: int,
    ) -> None:
        """彩虹渐变样式渲染：基于 HSV 色彩空间的连续光谱过渡，星形标记点缀。"""
        ax.set_facecolor("#000000")

        grid_levels = 5
        rainbow_spectrum = [colorsys.hsv_to_rgb(i / grid_levels, 0.3, 0.4) for i in range(grid_levels)]
        for level in range(grid_levels, 0, -1):
            radius = level * 20
            values_grid = [radius] * (n_cats + 1)
            rgb = rainbow_spectrum[grid_levels - level]
            grid_color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
            ax.plot(angles, values_grid, color=grid_color, linewidth=0.8, alpha=0.2)

        for i, angle in enumerate(angles[:-1]):
            hue = i / n_cats
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            line_color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
            ax.plot([angle, angle], [0, 100], color=line_color, linewidth=0.6, alpha=0.25)

        for i, cat in enumerate(categories):
            angle_rad = angles[i]
            hue = i / n_cats
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            label_color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
            ax.text(
                angle_rad,
                108,
                cat.upper(),
                color=label_color,
                fontsize=13,
                fontweight="bold",
                ha="center",
                va="center",
                family="sans-serif",
            )

        n_datasets = len(datasets)
        for d_idx, dataset in enumerate(datasets):
            values = dataset["values"] + dataset["values"][:1]
            base_hue = d_idx / max(n_datasets, 1)

            rainbow_colors = []
            for j in range(len(dataset["values"]) + 1):
                hue_offset = (j / n_cats + base_hue) % 1.0              # 色相沿路径偏移
                rgb = colorsys.hsv_to_rgb(hue_offset, 0.85, 0.95)
                hex_color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
                rainbow_colors.append(hex_color)

            for j in range(len(values) - 1):
                seg_values = values[j : j + 2]
                seg_angles = angles[j : j + 2]
                seg_color = rainbow_colors[j]
                ax.plot(
                    seg_angles,
                    seg_values,
                    color=seg_color,
                    linewidth=2.5,
                    alpha=0.9,
                    solid_capstyle="round",
                )

            for j in range(len(values) - 1):
                seg_values = values[j : j + 2]
                seg_angles = angles[j : j + 2]
                seg_color = rainbow_colors[j]
                ax.fill(seg_angles, seg_values, color=seg_color, alpha=0.35)

            for j, (angle, value) in enumerate(zip(angles[:-1], dataset["values"])):
                point_hue = (j / n_cats + base_hue) % 1.0
                rgb = colorsys.hsv_to_rgb(point_hue, 1.0, 1.0)
                point_color = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

                star_sizes = [180, 130, 90]
                star_alphas = [0.3, 0.6, 1.0]
                for size, alpha in zip(star_sizes, star_alphas):
                    ax.scatter(
                        [angle],
                        [value],
                        s=size,
                        marker="*",
                        c=[point_color],
                        edgecolors=["#ffffff"] if size == 90 else ["none"],
                        linewidths=1.5 if size == 90 else 0,
                        alpha=alpha,
                        zorder=10,
                    )

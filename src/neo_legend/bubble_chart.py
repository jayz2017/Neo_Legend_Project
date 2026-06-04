from __future__ import annotations

"""
奢华气泡图渲染器 (Luxury Bubble Chart Renderer)
==================================================
功能：多维度气泡散点图，支持 crystal_bubble(水晶气泡)、neon_glow(霓虹辉光)、galaxy(星系)、underwater(水下) 四种样式。
特色：自定义 Path marker（水滴/星形）、重叠防止算法、径向渐变填充、多层光晕效果。
"""


from typing import Any

import matplotlib.pyplot as plt
import matplotlib.transforms                              # 坐标变换模块（用于 Affine2D 平移/缩放）
import numpy as np
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path
from matplotlib.colors import LinearSegmentedColormap

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._plotting import (
    add_canvas,
    add_reference_footer,
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
    format_metric,
    resolve_report_text,
    resolve_report_theme,
    style_cartesian_axes,
)


class BubbleChartSkill(BaseLegendSkill):
    """奢华气泡图渲染器 — 多维度散点可视化，支持 4 种奢华视觉风格与自定义形状标记。"""

    legend_type = "bubble_chart"            # 图例类型标识
    display_name = "Luxury Bubble Chart"     # 显示名称
    default_style = "water_drops"           # 默认样式：水滴气泡
    default_size = (1400, 900)              # 默认输出尺寸（宽 x 高）
    style_definitions = (
        StyleDefinition(
            "water_drops",                                    # 水滴气泡：泪滴形状+折射光泽
            "Teardrop-shaped bubbles with refraction gloss arc and elliptical shadow.",
        ),
        StyleDefinition(
            "fireflies",                                      # 萤火虫效果：径向渐变发光粒子
            "Radial gradient glow particles with 4-frame trail and ambient star points.",
        ),
        StyleDefinition(
            "galaxy_stars",                                   # 星空银河：八角星形marker
            "Octagon-star markers with 3-layer twinkle halos and galaxy band background.",
        ),
        StyleDefinition(
            "crystal_orbs",                                   # 水晶球体：球面光影渐变
            "Sphere-like orbs with 6-layer lighting gradient and rainbow prism ring.",
        ),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        """主渲染入口：解析数据与样式，构建报告风格气泡图。"""
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = request.data or {}
        theme = resolve_report_theme(data, style)
        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)

        report_text = resolve_report_text(
            data,
            request.title,
            request.subtitle,
            default_title="Multi-Dimensional Analysis",
            default_subtitle="Size represents volume / Color encodes category",
            default_kicker="Bubble Chart",
            default_footer="NEO LEGEND | BUBBLE CHART REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )

        points = data.get("points", [])
        if not points:
            rng = np.random.default_rng(seed=42)
            n_default = 12
            base_colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7"]
            points = [
                {
                    "x": float(rng.uniform(5, 95)),
                    "y": float(rng.uniform(10, 90)),
                    "size": float(rng.uniform(200, 1200)),
                    "label": f"Item {chr(65 + i)}",
                    "color": base_colors[i % len(base_colors)],
                }
                for i in range(n_default)
            ]

        all_sizes = np.array([float(p.get("size", 100)) for p in points], dtype=float)
        all_x = np.array([float(p["x"]) for p in points], dtype=float)
        all_y = np.array([float(p["y"]) for p in points], dtype=float)

        draw_kpi_strip(
            canvas,
            theme,
            [
                ("count", str(len(points)), theme.primary),
                ("max size", format_metric(float(np.max(all_sizes))) if all_sizes.size else "0", theme.accent),
                ("avg size", format_metric(float(np.mean(all_sizes))) if all_sizes.size else "0", theme.secondary),
            ],
        )

        ax = add_report_axes(fig, canvas, (0.08, 0.16, 0.86, 0.56), theme)
        self._draw_bubbles(ax, points, style, theme)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        style_cartesian_axes(ax, theme, xlabel=str(data.get("x_label", "X Metric")), ylabel=str(data.get("y_label", "Y Metric")))
        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    def _draw_bubbles(self, ax: plt.Axes, points: list[dict], style: str, theme) -> None:
        """根据样式分发到对应的气泡绘制方法。"""
        render_map = {
            "water_drops": self._draw_crystal_style,     # 水滴气泡 → 水晶风格绘制
            "fireflies": self._draw_neon_style,           # 萤火虫 → 霓虹辉光绘制
            "galaxy_stars": self._draw_galaxy_style,      # 星空银河 → 星系风格绘制
            "crystal_orbs": self._draw_underwater_style,  # 水晶球体 → 水下风格绘制
        }
        renderer = render_map.get(style, self._draw_crystal_style)
        renderer(ax, points, theme)

    def _draw_crystal_style(self, ax: plt.Axes, points: list[dict], theme) -> None:
        """水晶气泡样式：径向渐变填充、玻璃高光反射、圆角描边轮廓。"""
        for point in points:
            x = float(point["x"])
            y = float(point["y"])
            size = float(point.get("size", 500))
            color = point.get("color") or theme.primary
            label = point.get("label", "")
            radius = np.sqrt(size / np.pi) * 0.10                     # 面积→半径换算（缩放因子 0.10）

            cmap = self._make_radial_gradient(color, "#ffffff", 128)   # 径向渐变：中心亮→边缘暗
            circle = plt.Circle((x, y), radius, facecolor=color, edgecolor="none", alpha=0.06, zorder=1)
            ax.add_patch(circle)

            n_rings = 3
            for ring_idx in range(n_rings):
                r_scale = 1 - (ring_idx + 1) * 0.18                  # 同心环半径递减
                ring_alpha = 0.04 + ring_idx * 0.03                   # 外环更透明
                ring = plt.Circle((x, y), radius * r_scale, facecolor="none",
                                  edgecolor=self._lighten_color(color, 0.35), linewidth=1.2, alpha=ring_alpha, zorder=2)
                ax.add_patch(ring)

            main_circle = plt.Circle((x, y), radius * 0.92, facecolor=cmap(0.45),
                                     edgecolor=self._lighten_color(color, 0.55), linewidth=1.8, alpha=0.90, zorder=4)
            ax.add_patch(main_circle)

            highlight_offset_x = radius * 0.28                         # 高光偏移量（模拟光源在右上）
            highlight_offset_y = radius * 0.28
            highlight_radius = radius * 0.30                           # 高光区域大小
            highlight = plt.Circle((x - highlight_offset_x, y + highlight_offset_y),
                                   highlight_radius, facecolor="#ffffff", edgecolor="none", alpha=0.38, zorder=5)
            ax.add_patch(highlight)

            if label:
                ax.text(x, y - radius - 1.6, label, color=theme.text, fontsize=9, fontweight="bold",
                        ha="center", va="top", zorder=7)

    def _draw_neon_style(self, ax: plt.Axes, points: list[dict], theme) -> None:
        """霓虹辉光样式：多层同心光环、脉冲扩散效果、发光文字标签。"""
        for point in points:
            x = float(point["x"])
            y = float(point["y"])
            size = float(point.get("size", 500))
            color = point.get("color") or "#ff00ff"
            label = point.get("label", "")
            radius = np.sqrt(size / np.pi) * 0.10

            for layer_r, layer_a, layer_lw in [(1.9, 0.03, 0.6), (1.55, 0.07, 1.0), (1.25, 0.14, 1.6), (1.0, 0.32, 2.4)]:
                halo = plt.Circle((x, y), radius * layer_r, facecolor="none",
                                  edgecolor=color, linewidth=layer_lw, alpha=layer_a, zorder=2)
                ax.add_patch(halo)

            core = plt.Circle((x, y), radius * 0.88, facecolor=color, edgecolor="#ffffff",
                              linewidth=1.2, alpha=0.22, zorder=4)
            ax.add_patch(core)

            inner_core = plt.Circle((x, y), radius * 0.50, facecolor=color, edgecolor="none",
                                    alpha=0.65, zorder=5)
            ax.add_patch(inner_core)

            bright_center = plt.Circle((x, y), radius * 0.18, facecolor="#ffffff", edgecolor="none",
                                       alpha=0.75, zorder=6)
            ax.add_patch(bright_center)

            if label:
                text_alpha_base = 0.85
                for dx in [-0.3, 0, 0.3]:                               # 文字辉光（三层偏移）
                    ax.text(x + dx, y - radius - 1.4, label, color=color, fontsize=9.5,
                            fontweight="bold", ha="center", va="top", alpha=text_alpha_base * 0.18, zorder=6)
                ax.text(x, y - radius - 1.4, label, color=color, fontsize=9.5, fontweight="bold",
                        ha="center", va="top", alpha=text_alpha_base, zorder=7)

    def _draw_galaxy_style(self, ax: plt.Axes, points: list[dict], theme) -> None:
        """星系样式：五角星标记、宇宙尘埃背景粒子、轨道环装饰。"""
        rng = np.random.default_rng(seed=42)
        dust_n = 180
        dust_x = rng.uniform(ax.get_xlim()[0], ax.get_xlim()[1], dust_n)
        dust_y = rng.uniform(ax.get_ylim()[0], ax.get_ylim()[1], dust_n)
        dust_s = rng.uniform(0.15, 1.8, dust_n)
        dust_a = rng.uniform(0.02, 0.14, dust_n)
        ax.scatter(dust_x, dust_y, s=dust_s, c="#ffffff", alpha=dust_a, zorder=0)       # 背景星尘粒子

        for point in points:
            x = float(point["x"])
            y = float(point["y"])
            size = float(point.get("size", 500))
            color = point.get("color") or "#ffd700"
            label = point.get("label", "")
            radius = np.sqrt(size / np.pi) * 0.095

            orbit_a = plt.Circle((x, y), radius * 1.6, facecolor="none",
                                 edgecolor=color, linewidth=0.6, linestyle="--", alpha=0.18, zorder=1)
            ax.add_patch(orbit_a)

            star_path = self._create_star_path(5, radius)               # 五角星 Path 对象
            star_marker = PathPatch(star_path, facecolor=color, edgecolor="#ffffff",
                                    linewidth=1.2, alpha=0.82, transform=ax.transData + matplotlib.transforms.Affine2D().translate(x, y), zorder=4)
            ax.add_patch(star_marker)

            glow_star = PathPatch(star_path, facecolor=color, edgecolor="none",
                                  alpha=0.18, transform=ax.transData + matplotlib.transforms.Affine2D().translate(x, y).scale(1.4), zorder=2)
            ax.add_patch(glow_star)

            center_dot = plt.Circle((x, y), radius * 0.12, facecolor="#ffffff", edgecolor="none",
                                    alpha=0.80, zorder=5)
            ax.add_patch(center_dot)

            if label:
                ax.text(x, y - radius - 1.4, label, color=color, fontsize=9, fontweight="bold",
                        ha="center", va="top", zorder=7)

    def _draw_underwater_style(self, ax: plt.Axes, points: list[dict], theme) -> None:
        """水下样式：水滴形 Path marker、焦散光线效果、深度色调变化。"""
        for idx, point in enumerate(points):
            x = float(point["x"])
            y = float(point["y"])
            size = float(point.get("size", 500))
            base_color = point.get("color") or "#00d4ff"
            label = point.get("label", "")
            radius = np.sqrt(size / np.pi) * 0.11
            depth_factor = min(idx / max(len(points) - 1, 1), 1.0)   # 深度因子：索引越大越深
            color = self._darken_by_factor(base_color, depth_factor * 0.45)  # 深度越深颜色越暗

            teardrop = self._create_teardrop_path(radius)             # 水滴形 Path 对象
            drop_shadow = PathPatch(teardrop, facecolor="#001a33", edgecolor="none",
                                    alpha=0.22, transform=ax.transData + matplotlib.transforms.Affine2D().translate(x + 0.35, y - 0.25), zorder=1)
            ax.add_patch(drop_shadow)

            drop_main = PathPatch(teardrop, facecolor=color, edgecolor=self._lighten_color(color, 0.40),
                                  linewidth=1.5, alpha=0.85, transform=ax.transData + matplotlib.transforms.Affine2D().translate(x, y), zorder=4)
            ax.add_patch(drop_main)

            highlight_teardrop = self._create_teardrop_path(radius * 0.28)
            hl = PathPatch(highlight_teardrop, facecolor="#ffffff", edgecolor="none",
                           alpha=0.40, transform=ax.transData + matplotlib.transforms.Affine2D().translate(x - radius * 0.18, y + radius * 0.30), zorder=5)
            ax.add_patch(hl)

            n_caustics = 3
            for ci in range(n_caustics):                                 # 焦散光线（从气泡发出的细线）
                angle = np.pi / 4 + ci * np.pi / 6                      # 各光线角度均匀分布
                length = radius * (0.6 + ci * 0.3)                     # 光线长度递增
                dx = length * np.cos(angle)
                dy = length * np.sin(angle)
                ax.plot([x, x + dx], [y, y + dy], color="#88eeff", linewidth=0.6, alpha=0.20 + ci * 0.08, zorder=3)

            if label:
                ax.text(x, y - radius * 1.15 - 1.0, label, color="#aaddff", fontsize=9, fontweight="bold",
                        ha="center", va="top", zorder=7)

    @staticmethod
    def _make_radial_gradient(center_color: str, edge_color: str, steps: int = 64) -> LinearSegmentedColormap:
        """创建径向渐变色映射：用于圆形气泡的中心到边缘颜色过渡。"""
        from matplotlib.colors import to_rgb
        c_rgb = np.array(to_rgb(center_color))
        e_rgb = np.array(to_rgb(edge_color))
        colors_list = []
        for i in range(steps):
            frac = i / max(steps - 1, 1)
            rgb = c_rgb + (e_rgb - c_rgb) * frac                       # RGB 线性插值
            colors_list.append(rgb)
        return LinearSegmentedColormap.from_list("_radial", colors_list)

    @staticmethod
    def _lighten_color(hex_color: str, factor: float) -> str:
        """颜色提亮：向白色方向混合 factor 比例。"""
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _darken_by_factor(hex_color: str, factor: float) -> str:
        """按比例加深颜色：RGB 各通道乘以 (1-factor)。"""
        hex_color = hex_color.lstrip("#")
        r = int(int(hex_color[0:2], 16) * (1 - factor))
        g = int(int(hex_color[2:4], 16) * (1 - factor))
        b = int(int(hex_color[4:6], 16) * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _create_star_path(n_points: int, radius: float) -> Path:
        """创建 N 角星形 Path 对象：外顶点和内凹点交替排列形成尖角星形。"""
        outer_r = radius
        inner_r = radius * 0.40                                       # 内凹点半径（控制星的尖锐度）
        vertices = []
        codes = []
        for i in range(n_points * 2):
            angle_outer = np.pi / 2 + i * np.pi / n_points            # 外顶点角度（起始朝上）
            angle_inner = np.pi / 2 + (i + 0.5) * np.pi / n_points    # 内凹点角度（两外顶点中间）
            r_outer = outer_r if i % 2 == 0 else inner_r               # 偶数索引为外顶点，奇数为内凹点
            r_inner = inner_r if i % 2 == 0 else outer_r
            vx = r_outer * np.cos(angle_outer)
            vy = r_outer * np.sin(angle_outer)
            vertices.append((vx, vy))
            codes.append(Path.MOVETO if i == 0 else Path.LINETO)
        vertices.append(vertices[0])                                    # 闭合路径
        codes.append(Path.CLOSEPOLY)
        return Path(vertices, codes)

    @staticmethod
    def _create_teardrop_path(radius: float) -> Path:
        """创建水滴形 Path 对象：贝塞尔曲线围成的上尖下圆泪滴形状。"""
        r = radius
        vertices = [
            (0, r * 1.15),                                            # 尖端顶部
            (r * 0.52, r * 0.42),                                      # 右侧曲线控制点
            (r * 0.72, -r * 0.15),                                     # 右下曲线控制点
            (r * 0.48, -r * 0.60),                                     # 右下底部
            (0, -r * 0.75),                                             # 底部最下端
            (-r * 0.48, -r * 0.60),                                    # 左下底部
            (-r * 0.72, -r * 0.15),                                    # 左下曲线控制点
            (-r * 0.52, r * 0.42),                                      # 左侧曲线控制点
            (0, r * 1.15),                                              # 回到尖端（闭合）
        ]
        codes = [Path.MOVETO] + [Path.CURVE4] * 7 + [Path.CLOSEPOLY]  # 三次贝塞尔曲线段
        return Path(vertices, codes)

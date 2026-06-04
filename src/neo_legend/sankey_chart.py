from __future__ import annotations

"""
奢华桑基图渲染器 (Luxury Sankey Diagram Renderer)
==================================================
功能：流向可视化桑基图，支持 neon_flow(霓虹流)、crystal_stream(水晶流)、sunset_ribbon(日落丝带)、ocean_current(洋流) 四种样式。
特色：9 点三次贝塞尔曲线流带、多层辉光效果、节点渐变填充、流量标注。
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
    style_cartesian_axes,  # 坐标轴样式化函数
)


class SankeyChartSkill(BaseLegendSkill):
    """奢华桑基图渲染器 — 流向关系可视化，支持 4 种奢华视觉风格的贝塞尔曲线流带。"""

    legend_type = "sankey_chart"             # 图例类型标识
    display_name = "Luxury Sankey Diagram"   # 显示名称
    default_style = "neon_streams"          # 默认样式：霓虹流光
    default_size = (1400, 1000)             # 默认输出尺寸（宽 x 高）
    style_definitions = (
        StyleDefinition(
            "neon_streams",
            "Neon glow flow bands on dark tech background with luminous nodes.",  # 霓虹流光：暗色科技背景+发光节点
        ),
        StyleDefinition(
            "energy_flow",
            "Heat-map colored energy flow with particle effects and warm nodes.",  # 能量流动：热力配色+粒子效果
        ),
        StyleDefinition(
            "crystal_rivers",
            "Alpha-gradient transparent flow bands with refraction texture lines.",  # 晶体河流：透明渐变流带+折射纹理
        ),
        StyleDefinition(
            "golden_paths",
            "Golden multi-layer glow flow bands with ornate rectangular nodes.",   # 黄金之路：金色多层辉光+华丽矩形节点
        ),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        """主渲染入口：解析数据与样式，构建报告风格桑基图。"""
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._extract_data(request.data or {})
        theme = resolve_report_theme(request.data or {}, style)

        fig = create_figure(width, height, theme.background)
        canvas = add_canvas(fig)
        draw_report_background(canvas, theme)

        report_text = resolve_report_text(
            request.data or {},
            request.title,
            request.subtitle,
            default_title="Flow Analysis",
            default_subtitle="Source → Target volume distribution",
            default_kicker="Sankey Diagram",
            default_footer="NEO LEGEND | SANKEY DIAGRAM REPORT",
        )
        draw_report_header(
            canvas,
            theme,
            report_text.title,
            report_text.subtitle,
            report_text.kicker,
            theme_label=report_text.theme_label,
        )

        total_value = sum(link["value"] for link in data["links"])
        source_count = len(data["sources"])
        target_count = len(data["targets"])

        draw_kpi_strip(
            canvas,
            theme,
            [
                ("total flow", format_metric(total_value), theme.primary),
                ("sources", str(source_count), theme.accent),
                ("targets", str(target_count), theme.secondary),
            ],
        )

        ax = add_report_axes(fig, canvas, (0.05, 0.12, 0.90, 0.68), theme)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        style_cartesian_axes(ax, theme)
        ax.set_axis_off()

        node_positions: dict[str, tuple[float, float]] = {}
        self._layout_nodes(ax, data["sources"], data["targets"], node_positions)
        self._draw_links(ax, data["links"], data["sources"], data["targets"], node_positions, style, theme)
        self._draw_nodes(ax, data["sources"], data["targets"], node_positions, style, theme)
        self._draw_link_labels(ax, data["links"], data["sources"], data["targets"], node_positions, theme)

        add_footer(canvas, theme, report_text.footer)
        return self.result(save_png(fig), style)

    @staticmethod
    def _extract_data(data: dict[str, Any]) -> dict[str, Any]:
        """提取源/目标/链接数据；缺失时返回默认演示桑基图数据。"""
        if data.get("links") and data.get("sources") and data.get("targets"):
            return {
                "sources": data["sources"],
                "targets": data["targets"],
                "links": data["links"],
            }

        sources = ["Website", "Mobile App", "Social Media", "Email", "Direct"]
        targets = ["Sign Up", "Purchase", "Upgrade"]
        links = [
            {"source": "Website", "target": "Sign Up", "value": 450},
            {"source": "Website", "target": "Purchase", "value": 280},
            {"source": "Mobile App", "target": "Sign Up", "value": 320},
            {"source": "Mobile App", "target": "Purchase", "value": 190},
            {"source": "Mobile App", "target": "Upgrade", "value": 85},
            {"source": "Social Media", "target": "Sign Up", "value": 210},
            {"source": "Social Media", "target": "Purchase", "value": 120},
            {"source": "Email", "target": "Sign Up", "value": 150},
            {"source": "Email", "target": "Purchase", "value": 95},
            {"source": "Direct", "target": "Purchase", "value": 170},
            {"source": "Direct", "target": "Upgrade", "value": 60},
        ]
        return {"sources": sources, "targets": targets, "links": links}

    @staticmethod
    def _layout_nodes(
        ax: plt.Axes,
        sources: list[str],
        targets: list[str],
        positions: dict[str, tuple[float, float]],
    ) -> None:
        """计算节点布局位置：源节点均匀分布在左侧 X=10%，目标节点在右侧 X=90%。"""
        n_sources = len(sources)
        n_targets = len(targets)
        y_spacing_source = 80 / max(n_sources - 1, 1)                    # 源节点垂直间距
        y_spacing_target = 80 / max(n_targets - 1, 1)                   # 目标节点垂直间距

        for i, src in enumerate(sources):
            y_pos = 90 - i * y_spacing_source if n_sources > 1 else 50   # 从上到下排列
            positions[src] = (10.0, y_pos)

        for i, tgt in enumerate(targets):
            y_pos = 90 - i * y_spacing_target if n_targets > 1 else 50
            positions[tgt] = (90.0, y_pos)

    def _draw_links(
        self,
        ax: plt.Axes,
        links: list[dict],
        sources: list[str],
        targets: list[str],
        positions: dict[str, tuple[float, float]],
        style: str,
        theme,
    ) -> None:
        """绘制所有流带链接：根据样式选择对应的贝塞尔曲线路径渲染方法。"""
        renderer_map = {
            "neon_streams": self._draw_neon_link,     # 霓虹流光 → 霓虹发光绘制
            "energy_flow": self._draw_crystal_link,    # 能量流动 → 晶体流线绘制
            "crystal_rivers": self._draw_sunset_link,  # 晶体河流 → 日落丝带绘制
            "golden_paths": self._draw_ocean_link,     # 黄金之路 → 洋流绘制
        }
        renderer = renderer_map.get(style, self._draw_neon_link)  # 根据样式名选择渲染方法，默认回退到霓虹流光

        all_values = [link["value"] for link in links]
        max_val = max(all_values) if all_values else 1

        for link in links:
            src_name = link["source"]
            tgt_name = link["target"]
            value = link["value"]

            if src_name not in positions or tgt_name not in positions:
                continue

            x1, y1 = positions[src_name]                                 # 源节点坐标
            x2, y2 = positions[tgt_name]                                 # 目标节点坐标
            thickness = max((value / max_val) * 8 + 1.5, 1.5)           # 流量→线宽映射

            color = link.get("color") or theme.palette[
                (sources.index(src_name) if src_name in sources else targets.index(tgt_name)) % len(theme.palette)
            ]
            renderer(ax, x1, y1, x2, y2, thickness, color, value)

    @staticmethod
    def _bezier_path(x1: float, y1: float, x2: float, y2: float, thickness: float) -> Path:
        """生成 9 点三次贝塞尔曲线路径：用于绘制平滑的流带形状。

        路径结构：
          P0: 源节点左侧边缘起点（上沿）
          P1-P3: 左侧贝塞尔控制点（形成 S 形弯曲）
          P4: 曲线中点
          P5-P7: 右侧贝塞尔控制点（反向 S 形）
          P8: 目标节点右侧边缘终点（下沿）
        """
        dx = x2 - x1
        dy = y2 - y1
        cx1 = x1 + dx * 0.30                                         # 第一段控制点（靠近源端 30% 处）
        cy1 = y1
        cx2 = x1 + dx * 0.70                                         # 第二段控制点（靠近目标端 70% 处）
        cy2 = y2
        mid_x = (x1 + x2) / 2                                        # 中点 X 坐标
        mid_y = (y1 + y2) / 2                                        # 中点 Y 坐标
        half_t = thickness / 2

        verts = [
            (x1, y1 + half_t),                                       # P0: 起点（上沿）
            (cx1, cy1 + half_t * 1.3),                                # P1: 上侧控制点1（略微加宽模拟透视）
            (mid_x, mid_y + half_t * 0.6),                            # P2: 上侧中点（收窄）
            (cx2, cy2 + half_t),                                      # P3: 上侧控制点2
            (x2, y2 + half_t),                                        # P4: 右上角转折点
            (cx2, cy2 - half_t),                                      # P5: 下侧控制点2
            (mid_x, mid_y - half_t * 0.6),                            # P6: 下侧中点
            (cx1, cy1 - half_t * 1.3),                                # P7: 下侧控制点1
            (x1, y1 - half_t),                                        # P8: 回到起点（闭合）
        ]

        codes = [
            Path.MOVETO,                                             # 移动到起点
            Path.CURVE4,                                              # 三次贝塞尔 P0→P1→P2→P3
            Path.CURVE4,                                              # 三次贝塞尔 P3→P4→P5→P6
            Path.CURVE4,                                              # 三次贝塞尔 P6→P7→P8→P0
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CLOSEPOLY,                                           # 闭合路径
        ]
        return Path(verts, codes)

    @staticmethod
    def _draw_neon_link(ax: plt.Axes, x1: float, y1: float, x2: float, y2: float, thickness: float, color: str, value: float) -> None:
        """霓虹流样式链接：多层辉光描边 + 半透明内核填充。"""
        path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness)

        for lw, alpha in [(thickness * 3.5, 0.04), (thickness * 2.0, 0.10), (thickness * 1.1, 0.25)]:
            patch = PathPatch(path, facecolor="none", edgecolor=color, linewidth=lw, alpha=alpha, zorder=2, capstyle="round", joinstyle="round")
            ax.add_patch(patch)

        fill_patch = PathPatch(path, facecolor=color, edgecolor="none", alpha=0.28, zorder=3)
        ax.add_patch(fill_patch)

        core_path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness * 0.35)
        core_patch = PathPatch(core_path, facecolor="#ffffff", edgecolor="none", alpha=0.55, zorder=4)
        ax.add_patch(core_patch)

    @staticmethod
    def _draw_crystal_link(ax: plt.Axes, x1: float, y1: float, x2: float, y2: float, thickness: float, color: str, value: float) -> None:
        """水晶流样式链接：透明玻璃质感、高光线条、柔和阴影。"""
        path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness)

        shadow_offset_x = 1.2                                          # 阴影偏移量
        shadow_verts = [(v[0] + shadow_offset_x, v[1] - 0.8) for v in path.vertices]
        shadow_codes = list(path.codes)
        shadow_path = Path(shadow_verts, shadow_codes)
        shadow_patch = PathPatch(shadow_path, facecolor="#000000", edgecolor="none", alpha=0.12, zorder=1)
        ax.add_patch(shadow_patch)

        fill_patch = PathPatch(path, facecolor=color, edgecolor="none", alpha=0.35, zorder=3)
        ax.add_patch(fill_patch)

        highlight_path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness * 0.18)
        highlight_patch = PathPatch(highlight_path, facecolor="#ffffff", edgecolor="none", alpha=0.45, zorder=4)
        ax.add_patch(highlight_patch)

        edge_patch = PathPatch(path, facecolor="none", edgecolor=color, linewidth=1.2, alpha=0.65, zorder=5)
        ax.add_patch(edge_patch)

    @staticmethod
    def _draw_sunset_link(ax: plt.Axes, x1: float, y1: float, x2: float, y2: float, thickness: float, color: str, value: float) -> None:
        """日落丝带样式链接：暖色渐变填充、环境光晕、金色高光中心。"""
        path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness)

        glow_lw = thickness * 2.5
        glow_patch = PathPatch(path, facecolor="none", edgecolor="#ffd700", linewidth=glow_lw, alpha=0.08, zorder=1, capstyle="round")
        ax.add_patch(glow_patch)

        from matplotlib.colors import to_rgb, LinearSegmentedColormap
        c_rgb = np.array(to_rgb(color))
        g_rgb = np.array(to_rgb("#ffd700"))
        blend = c_rgb * 0.70 + g_rgb * 0.30                              # 原色与金色混合
        hex_blend = f"#{int(blend[0]*255):02x}{int(blend[1]*255):02x}{int(blend[2]*255):02x}"

        fill_patch = PathPatch(path, facecolor=hex_blend, edgecolor="none", alpha=0.42, zorder=3)
        ax.add_patch(fill_patch)

        core_path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness * 0.28)
        core_patch = PathPatch(core_path, facecolor="#fffacd", edgecolor="none", alpha=0.60, zorder=4)
        ax.add_patch(core_patch)

    @staticmethod
    def _draw_ocean_link(ax: plt.Axes, x1: float, y1: float, x2: float, y2: float, thickness: float, color: str, value: float) -> None:
        """洋流样式链接：波浪形调制路径、青色辉光、深浅色调变化。"""
        base_path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness)
        n_wave = 12                                                    # 波浪分段数
        wave_amp = thickness * 0.15                                    # 波浪振幅
        verts = list(base_path.vertices)
        codes = list(base_path.codes)

        for i in range(3, min(len(verts) - 3, len(verts))):
            offset = wave_amp * np.sin(i * np.pi / 2.5)                 # 正弦波调制偏移
            verts[i] = (verts[i][0], verts[i][1] + offset)              # 仅对中间控制点施加波动

        wave_path = Path(verts, codes)

        glow_patch = PathPatch(wave_path, facecolor="none", edgecolor="#00ffff", linewidth=thickness * 2.0, alpha=0.06, zorder=1, capstyle="round")
        ax.add_patch(glow_patch)

        fill_patch = PathPatch(wave_path, facecolor=color, edgecolor="none", alpha=0.32, zorder=3)
        ax.add_patch(fill_patch)

        core_path = SankeyChartSkill._bezier_path(x1, y1, x2, y2, thickness * 0.22)
        core_patch = PathPatch(core_path, facecolor="#e0ffff", edgecolor="none", alpha=0.50, zorder=4)
        ax.add_patch(core_patch)

    @staticmethod
    def _draw_nodes(
        ax: plt.Axes,
        sources: list[str],
        targets: list[str],
        positions: dict[str, tuple[float, float]],
        style: str,
        theme,
    ) -> None:
        """绘制所有节点：圆角矩形 + 渐变填充 + 标签文字。"""
        color_map = {
            "neon_flow": ("#1a1a2e", "#ff00ff"),
            "crystal_stream": ("#f0f0ff", "#4a90d9"),
            "sunset_ribbon": ("#2d1810", "#ffa500"),
            "ocean_current": ("#001a33", "#00ced1"),
        }
        bg_color, accent_color = color_map.get(style, ("#1a1a2e", "#ff00ff"))

        for name, (x, y) in positions.items():
            is_target = name in targets
            width = 14 if is_target else 16                             # 目标节点略窄
            height = 7.0

            shadow = FancyBboxPatch(                                    # 节点阴影层
                (x - width / 2 + 0.35, y - height / 2 - 0.25),
                width, height,
                boxstyle="round,pad=0.02,rounding_size=0.8",
                facecolor="#000000",
                edgecolor="none",
                alpha=0.20,
                zorder=5,
            )
            ax.add_patch(shadow)

            node = FancyBboxPatch(                                       # 节点主体
                (x - width / 2, y - height / 2),
                width, height,
                boxstyle="round,pad=0.02,rounding_size=0.8",
                facecolor=bg_color,
                edgecolor=accent_color,
                linewidth=1.8,
                alpha=0.92,
                zorder=6,
            )
            ax.add_patch(node)

            label_color = "#ffffff"
            fontsize = 9 if is_target else 10
            ax.text(x, y, name.upper(), color=label_color, fontsize=fontsize,
                    fontweight="bold", ha="center", va="center", zorder=7)

    @staticmethod
    def _draw_link_labels(
        ax: plt.Axes,
        links: list[dict],
        sources: list[str],
        targets: list[str],
        positions: dict[str, tuple[float, float]],
        theme,
    ) -> None:
        """在每条流带的中点位置绘制流量数值标签。"""
        for link in links:
            src_name = link["source"]
            tgt_name = link["target"]
            value = link["value"]

            if src_name not in positions or tgt_name not in positions:
                continue

            x1, y1 = positions[src_name]
            x2, y2 = positions[tgt_name]
            mx = (x1 + x2) / 2                                            # 中点 X
            my = (y1 + y2) / 2                                            # 中点 Y

            bbox_props = dict(boxstyle="round,pad=0.18", facecolor=theme.panel_alt,
                              edgecolor=theme.border, alpha=0.85, linewidth=0.6)
            ax.text(mx, my, format_metric(value), color=theme.text, fontsize=8,
                    fontweight="bold", ha="center", va="center", zorder=8, bbox=bbox_props)

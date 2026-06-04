from __future__ import annotations

"""
双球场对比渲染器 (Dual Court Shot Renderer)
============================================
功能：生成上下堆叠的双半场投篮对比图，支持 year_over_year（同比）和 split_hex（分屏六边形）样式。
依赖：matplotlib, numpy
"""

"""Dual court comparison renderer skill."""


from typing import Any

import numpy as np

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._court import draw_half_court, sample_shots, BASKET_Y, THREE_PT_ARC_RADIUS, CORNER_3_X
from neo_legend._plotting import add_canvas, create_figure, make_gradient, save_png
from neo_legend.base import BaseLegendSkill, StyleDefinition


class DualCourtShotSkill(BaseLegendSkill):
    """双球场对比渲染器 — 支持上下两个半场面板的同比/六边形对比可视化。"""

    legend_type = "dual_court_shot"      # 图例类型标识符
    display_name = "Dual Court Shooting Comparison"  # 显示名称
    default_style = "year_over_year"     # 默认样式：年度同比对比
    default_size = (1179, 1471)          # 默认输出尺寸
    style_definitions = (                 # 样式定义元组
        StyleDefinition(
            "year_over_year",
            "Two stacked half-court shot maps with headline metrics.",
            ("3c1084f8f059bd51ab35a52c527d08f5.jpg",),
        ),
        StyleDefinition("split_hex", "Two stacked hex-density courts with bolder color contrast."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        """主渲染入口：绘制标题、分隔线，然后依次渲染上下两个球场面板。"""
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
        canvas.plot([0.06, 0.94], [0.872, 0.872], color="#aa9f73", lw=1, alpha=0.6)  # 标题与内容间的分隔线

        panels = self._panels(request.data)
        self._draw_panel(fig, canvas, 0.535, panels[0], style)   # 上方面板（较早赛季）
        self._draw_panel(fig, canvas, 0.09, panels[1], style)    # 下方面板（较晚赛季）

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
        """绘制单个对比面板：包含赛季信息、关键指标标签、球场热力图和区域命中率标注。"""
        season = str(panel.get("season", "2024-25"))
        attempts = str(panel.get("attempts", "79 GAMES / 808 ATTEMPTS"))
        seed = int(panel.get("seed", 12))
        canvas.text(0.05, bottom + 0.33, season, color="#f4f3ec", fontsize=28, fontweight="black")
        canvas.text(0.05, bottom + 0.305, attempts, color="#d2cec9", fontsize=10, fontweight="bold")

        metric_x = [0.66, 0.78, 0.91]                          # 三项指标的 X 坐标位置
        metric_labels = ["FG%", "3P%", "eFG%"]
        metrics = panel.get("metrics") if isinstance(panel.get("metrics"), dict) else {}
        metric_values = [str(metrics.get(label, "")) for label in metric_labels]
        if not all(metric_values):
            metric_values = ["47.6%", "33.2%", "53.7%"] if seed == 12 else ["51.8%", "42.0%", "58.4%"]  # 默认指标值
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

        court_ax = fig.add_axes([0.06, bottom - 0.03, 0.88, 0.38], facecolor="#030404")
        draw_half_court(court_ax, line_color="#f1eee5", line_width=1.0, alpha=0.74)
        x, y, value = sample_shots(seed=seed, count=500)
        if style == "split_hex":
            cmap = make_gradient(["#50a0d8", "#fff8cf", "#ef243a"], "split_hex")
            court_ax.scatter(x, y, c=value, cmap=cmap, s=32, marker="h", alpha=0.88, lw=0)
        else:
            sizes = np.interp(value, (value.min(), value.max()), (9, 48))  # 值映射到尺寸范围
            colors = np.where(value > 0.5, "#f8f7d4", np.where(value < -0.5, "#e5273f", "#77bde5"))  # 三色分段：高/低/中
            court_ax.scatter(x, y, s=sizes, c=colors, alpha=0.86, lw=0)

        for label, px, py in [
            ("31%", -CORNER_3_X + 5, int(5.0 * 10) + 5),           # 底角三分
            ("42%", int(CORNER_3_X * 0.75), BASKET_Y + THREE_PT_ARC_RADIUS * 1.35),  # 右侧弧顶外
            ("53%", int(-CORNER_3_X * 0.65), BASKET_Y + THREE_PT_ARC_RADIUS * 0.78), # 左翼中距离
            ("60%", 0, BASKET_Y + 18),                               # 篮下
        ]:
            court_ax.text(px, py, label, color="#f5f3eb", fontsize=12, fontweight="bold")

    @staticmethod
    def _panels(data: dict[str, Any]) -> list[dict[str, Any]]:
        """解析面板数据：从请求中提取两个赛季的配置，若无效则使用默认的 2024-25 / 2025-26 对比。"""
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

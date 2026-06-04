from __future__ import annotations

"""
动画球场投射图渲染器 (Animated Court Shot Renderer)
=====================================================
功能：生成 GIF 动画格式的投篮热力图，支持 arena_arc（3D 球馆弧线）、pulse（脉冲）、sweep（扫描）样式。
依赖：matplotlib, numpy, PIL
"""

"""Animated court shooting GIF renderer skill."""


from io import BytesIO

import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle
from PIL import Image

from neo_legend._court import draw_half_court, sample_shots, BASKET_Y, THREE_PT_ARC_RADIUS, COURT_HALF_WIDTH
from neo_legend._plotting import add_canvas, create_figure, make_gradient, save_png, seeded_rng
from neo_legend.base import BaseLegendSkill, StyleDefinition
from neo_legend.models import RenderRequest, RenderResult


class AnimatedCourtShotSkill(BaseLegendSkill):
    """动画球场投射渲染器 — 生成 GIF 动画，包含 3D 球馆视角的投篮弧线、脉冲波和渐进扫描效果。"""

    legend_type = "court_shot_animation"   # 图例类型标识符
    display_name = "Animated Court Shooting Terrain"
    default_style = "arena_arc"             # 默认样式：3D 球馆投篮弧线动画
    default_size = (1179, 1165)             # 默认输出尺寸
    media_type = "image/gif"                # 输出媒体类型：GIF 动画
    file_extension = "gif"                  # 文件扩展名
    style_definitions = (                   # 样式定义元组
        StyleDefinition(
            "arena_arc",
            "Black and gold 3D arena view with animated shot arcs.",
            ("0ca42dfeab11e52e7e4a3a1665b81695.jpg",),
        ),
        StyleDefinition("pulse", "Animated pulse over the shooting terrain."),
        StyleDefinition("sweep", "Animated progressive reveal over shot clusters."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        """主渲染入口：逐帧生成图片并合成为 GIF 动画。"""
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        frame_count = int(request.data.get("frame_count", 14 if style == "arena_arc" else 10))  # 总帧数
        frames = [
            self._frame(request, style, width, height, index, frame_count)
            for index in range(frame_count)
        ]
        buffer = BytesIO()
        frames[0].save(
            buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],                            # 追加后续帧
            duration=90,                                         # 每帧显示时长（毫秒）
            loop=0,                                              # 无限循环
            disposal=2,                                          # 帧间清除方式
        )
        return self.result(buffer.getvalue(), style)

    def _frame(
        self,
        request: RenderRequest,
        style: str,
        width: int,
        height: int,
        index: int,
        frame_count: int,
    ) -> Image.Image:
        """帧生成分发器：根据样式路由到对应的帧渲染方法，返回 PIL Image 对象。"""
        if style == "arena_arc":
            return self._arena_frame(request, width, height, index, frame_count)

        fig = create_figure(width, height, "#020303")
        canvas = add_canvas(fig)
        canvas.text(
            0.5,
            0.91,
            (request.title or "SHOOTING TERRAIN").upper(),
            color="#f6f4ed",
            fontsize=42,
            fontweight="black",
            ha="center",
        )
        canvas.text(
            0.5,
            0.862,
            (request.subtitle or "ANIMATED ZONE MAP").upper(),
            color="#bbb5ae",
            fontsize=15,
            fontweight="bold",
            ha="center",
        )
        ax = fig.add_axes([0.07, 0.06, 0.86, 0.68], facecolor="#020303")
        draw_half_court(ax, line_color="#e6e1d7", line_width=1.0, alpha=0.68)
        shot_count = int(request.data.get("shot_count", 430))
        seed = int(request.data.get("seed", 31))
        x, y, value = sample_shots(seed=seed, count=shot_count)
        phase = index / max(frame_count - 1, 1)                  # 当前动画相位 [0, 1]
        if style == "sweep":
            alpha = self._progressive_sweep_alpha(
                total_count=len(x),
                frame_index=index,
                frame_count=frame_count,
                settled_alpha=float(request.data.get("settled_alpha", 0.46)),
                highlight_alpha=float(request.data.get("highlight_alpha", 0.92)),
                highlight_tail=int(request.data.get("highlight_tail", 42)),
            )
        else:
            radius = np.sqrt((x / COURT_HALF_WIDTH) ** 2 + ((y - BASKET_Y) / THREE_PT_ARC_RADIUS) ** 2)  # 归一化到篮筐的距离
            alpha = np.clip(np.sin((radius + phase) * np.pi * 2) * 0.45 + 0.5, 0.1, 0.9)  # 正弦脉冲透明度
        cmap = make_gradient(["#2a2d31", "#7a3345", "#ec3456", "#ffe2d1"], "gif_terrain")
        visible = alpha > 0                                       # 过滤掉完全透明的点
        ax.scatter(
            x[visible],
            y[visible],
            c=value[visible],
            cmap=cmap,
            s=18 + alpha[visible] * 64,                           # 尺寸随透明度增大
            marker="h",
            alpha=alpha[visible],
            lw=0,
        )

        png = save_png(fig)
        return Image.open(BytesIO(png)).convert("RGB")

    @staticmethod
    def _progressive_sweep_alpha(
        total_count: int,
        frame_index: int,
        frame_count: int,
        settled_alpha: float = 0.46,
        highlight_alpha: float = 0.92,
        highlight_tail: int = 42,
    ) -> np.ndarray:
        """计算渐进扫描效果的逐点透明度数组：已显示的点保持低透明度，尾部高亮区域逐渐增强。"""
        if total_count <= 0:
            return np.array([], dtype=float)
        progress = (frame_index + 1) / max(frame_count, 1)         # 当前进度比例
        visible_count = max(1, min(total_count, int(np.ceil(total_count * progress))))  # 当前可见点数
        alpha = np.zeros(total_count, dtype=float)
        alpha[:visible_count] = np.clip(settled_alpha, 0.05, 1.0) # 已显示区域的基础透明度

        tail = max(1, min(highlight_tail, visible_count))          # 高亮尾部长度
        tail_start = visible_count - tail                         # 高亮起始位置
        tail_ramp = np.linspace(0.0, 1.0, tail)                    # 从 0 到 1 的线性渐变
        alpha[tail_start:visible_count] = np.maximum(
            alpha[tail_start:visible_count],
            np.clip(settled_alpha + (highlight_alpha - settled_alpha) * tail_ramp, 0.05, 1.0),  # 尾部叠加高亮
        )
        return alpha

    def _arena_frame(
        self,
        request: RenderRequest,
        width: int,
        height: int,
        index: int,
        frame_count: int,
    ) -> Image.Image:
        """渲染 3D 球馆视角的单帧：包含球员头像、赛季进度条、透视球场和动态投篮弧线。"""
        fig = create_figure(width, height, "#020202")
        canvas = add_canvas(fig)
        self._draw_arena_header(canvas, request, index, frame_count)
        self._draw_perspective_court(canvas)
        self._draw_animated_arcs(canvas, index, frame_count)
        png = save_png(fig)
        return Image.open(BytesIO(png)).convert("RGB")

    @staticmethod
    def _draw_arena_header(canvas, request: RenderRequest, index: int, frame_count: int) -> None:
        """绘制球馆头部信息区：球员头像（圆形组合）、姓名、副标题、赛季进度条和累计得分。"""
        yellow = "#ffd735"
        progress = (index + 1) / frame_count                      # 动画进度
        points = int(1530 + 264 * progress)                       # 随进度增长的累计得分

        canvas.add_patch(Circle((0.132, 0.86), 0.105, facecolor="#101010", edgecolor=yellow, lw=4))  # 头像外圈
        canvas.add_patch(Circle((0.132, 0.88), 0.052, facecolor="#f1c3a4", edgecolor="none"))       # 脸部底色
        canvas.add_patch(Circle((0.106, 0.89), 0.035, facecolor="#2b1a16", edgecolor="none", alpha=0.95))  # 左眼
        canvas.add_patch(Circle((0.158, 0.89), 0.035, facecolor="#2b1a16", edgecolor="none", alpha=0.95))  # 右眼
        canvas.plot([0.112, 0.152], [0.853, 0.853], color="#6b2b2b", lw=2)                        # 嘴巴

        canvas.text(
            0.29,
            0.92,
            request.title or "CAITLIN CLARK",
            color=yellow,
            fontsize=45,
            fontweight="black",
            ha="left",
            va="center",
        )
        canvas.text(
            0.29,
            0.87,
            request.subtitle or "MOST POINTS IN NCAA WOMEN'S BASKETBALL HISTORY",
            color="#f4f4f2",
            fontsize=15,
            fontweight="black",
            ha="left",
            va="center",
        )

        x0, y0, box_h = 0.29, 0.815, 0.038
        seasons = ["20-21", "21-22", "22-23", "23-24"]
        for season_index, season in enumerate(seasons):
            w = 0.10
            x = x0 + season_index * w
            fill = yellow if season_index < int(progress * len(seasons)) + 1 else "none"  # 已完成赛季填充黄色
            canvas.add_patch(Rectangle((x, y0), w - 0.004, box_h, facecolor=fill, edgecolor=yellow, lw=2))
            canvas.text(
                x + 0.045,
                y0 + box_h / 2,
                season,
                color="#111111" if fill == yellow else yellow,
                fontsize=18,
                fontweight="black",
                ha="center",
                va="center",
            )
        canvas.add_patch(Rectangle((0.69, y0), 0.08 * progress, box_h, facecolor=yellow, edgecolor="none"))  # 当前赛季进度条
        canvas.add_patch(Rectangle((0.69, y0), 0.16, box_h, facecolor="none", edgecolor=yellow, lw=2))     # 进度条边框
        canvas.text(0.965, 0.83, f"{points:,}", color=yellow, fontsize=44, fontweight="black", ha="right")  # 累计得分
        canvas.text(0.31, 0.785, "BY @VannaBushong AND @KirkGoldsberry", color="#8f8f8f", fontsize=16)

    @staticmethod
    def _draw_perspective_court(canvas) -> None:
        """绘制 3D 透视球场：梯形场地、禁区、三分线、罚球线和球队水印文字。"""
        court = np.array([[0.02, 0.02], [0.98, 0.02], [0.80, 0.62], [0.18, 0.62]])  # 梯形球场四角坐标
        canvas.add_patch(
            Polygon(court, closed=True, facecolor="#5a4728", edgecolor="#d8d4cc", lw=2, alpha=0.78)
        )
        key_polygon = [[0.38, 0.28], [0.62, 0.28], [0.58, 0.54], [0.42, 0.54]]  # 禁区（梯形）
        canvas.add_patch(
            Polygon(
                key_polygon,
                facecolor="#090909",
                edgecolor="#e6e1d7",
                lw=1.4,
                alpha=0.88,
            )
        )
        canvas.plot([0.10, 0.90], [0.26, 0.26], color="#ded9cf", lw=2, alpha=0.8)              # 底线
        canvas.add_patch(Circle((0.50, 0.31), 0.105, fill=False, edgecolor="#ded9cf", lw=1.5, alpha=0.75))  # 罚球圆
        canvas.add_patch(Circle((0.50, 0.42), 0.205, fill=False, edgecolor="#ded9cf", lw=1.5, alpha=0.75))  # 三分圆弧
        canvas.add_patch(Circle((0.50, 0.56), 0.038, fill=False, edgecolor="#ded9cf", lw=1.2, alpha=0.75))  # 篮筐标记
        canvas.plot([0.44, 0.56], [0.21, 0.21], color="#f5d033", lw=4, alpha=0.55)                 # 篮筐（金色）
        canvas.plot([0.44, 0.56], [0.47, 0.47], color="#f5f5f5", lw=3, alpha=0.85)               # 篮板
        canvas.add_patch(Rectangle((0.49, 0.47), 0.055, 0.06, facecolor="none", edgecolor="#f5f5f5", lw=2))  # 篮板外框
        canvas.add_patch(Rectangle((0.515, 0.48), 0.028, 0.025, facecolor="none", edgecolor="#f5f5f5", lw=1.5))  # 篮板内框
        canvas.text(
            0.55,
            0.58,
            "IOWA HAWKEYES",
            color="#f5d033",
            fontsize=30,
            fontweight="black",
            rotation=-7,
            ha="center",
            alpha=0.62,
        )
        canvas.text(
            0.20,
            0.08,
            "IOWA",
            color="#f5d033",
            fontsize=78,
            fontweight="black",
            rotation=9,
            ha="center",
            alpha=0.42,
        )

    @staticmethod
    def _draw_animated_arcs(canvas, index: int, frame_count: int) -> None:
        """绘制动态投篮弧线：从随机起点到篮筐的贝塞尔曲线，随帧数逐步显现并产生入网效果。"""
        rng = seeded_rng(22)
        starts = np.column_stack([rng.uniform(0.14, 0.86, 46), rng.uniform(0.16, 0.45, 46)])  # 投篮起点坐标
        hoop = np.array([0.515, 0.49])                          # 篮筐位置
        visible = min(len(starts), int((index + 1) / frame_count * len(starts)) + 3)  # 当前可见弧线数量
        yellow = "#ffe66b"
        for shot_index, start in enumerate(starts[:visible]):
            local_phase = np.clip((index + 1.6 - shot_index * 0.12) / max(frame_count * 0.55, 1), 0, 1)  # 单条弧线的局部进度
            if local_phase <= 0:
                continue
            ctrl = (start + hoop) / 2 + np.array([0, rng.uniform(0.16, 0.29)])  # 贝塞尔控制点（向上偏移模拟抛物线）
            t = np.linspace(0, local_phase, 28)                   # 曲线参数化采样
            curve = (
                (1 - t)[:, None] ** 2 * start                     # 二次贝塞尔公式：P = (1-t)²·P₀ + 2(1-t)t·P₁ + t²·P₂
                + 2 * (1 - t)[:, None] * t[:, None] * ctrl
                + t[:, None] ** 2 * hoop
            )
            canvas.plot(curve[:, 0], curve[:, 1], color=yellow, lw=1.2, alpha=0.34)  # 投篮轨迹
            canvas.scatter(curve[-1:, 0], curve[-1:, 1], color="#fff3a4", s=18, alpha=0.92, lw=0)      # 球的位置
            if local_phase > 0.92:
                canvas.plot([hoop[0], hoop[0]], [hoop[1], hoop[1] + 0.18], color=yellow, lw=2.2, alpha=0.55)  # 入网效果线

        dots = np.column_stack([rng.uniform(0.12, 0.88, 330), rng.uniform(0.12, 0.47, 330)])  # 背景装饰点
        fade = np.clip((index + 1) / frame_count, 0.25, 1.0)      # 装饰点渐显系数
        canvas.scatter(dots[:, 0], dots[:, 1], s=rng.uniform(4, 14, 330), color=yellow, alpha=0.15 * fade, lw=0)
        makes = np.column_stack([rng.normal(0.52, 0.035, 80), rng.normal(0.48, 0.035, 80)])  # 篮筐附近的命中点聚集
        canvas.scatter(makes[:, 0], makes[:, 1], s=rng.uniform(5, 20, 80), color=yellow, alpha=0.32 + 0.25 * fade, lw=0)

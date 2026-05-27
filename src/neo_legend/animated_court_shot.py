"""Animated court shooting GIF renderer skill."""

from __future__ import annotations

from io import BytesIO

from matplotlib.patches import Circle, Polygon, Rectangle
from PIL import Image
import numpy as np

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._court import draw_half_court, sample_shots
from neo_legend._plotting import add_canvas, create_figure, make_gradient, save_png, seeded_rng
from neo_legend.base import BaseLegendSkill, StyleDefinition


class AnimatedCourtShotSkill(BaseLegendSkill):
    legend_type = "court_shot_animation"
    display_name = "Animated Court Shooting Terrain"
    default_style = "arena_arc"
    default_size = (1179, 1165)
    media_type = "image/gif"
    file_extension = "gif"
    style_definitions = (
        StyleDefinition(
            "arena_arc",
            "Black and gold 3D arena view with animated shot arcs.",
            ("0ca42dfeab11e52e7e4a3a1665b81695.jpg",),
        ),
        StyleDefinition("pulse", "Animated pulse over the shooting terrain."),
        StyleDefinition("sweep", "Animated left-to-right scan over shot clusters."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        frame_count = int(request.data.get("frame_count", 14 if style == "arena_arc" else 10))
        frames = [
            self._frame(request, style, width, height, index, frame_count)
            for index in range(frame_count)
        ]
        buffer = BytesIO()
        frames[0].save(
            buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=90,
            loop=0,
            disposal=2,
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
        phase = index / max(frame_count - 1, 1)
        if style == "sweep":
            alpha = np.clip(1.0 - np.abs((x + 250) / 500 - phase) * 2.4, 0.08, 0.92)
        else:
            radius = np.sqrt((x / 250) ** 2 + ((y - 60) / 420) ** 2)
            alpha = np.clip(np.sin((radius + phase) * np.pi * 2) * 0.45 + 0.5, 0.1, 0.9)
        cmap = make_gradient(["#2a2d31", "#7a3345", "#ec3456", "#ffe2d1"], "gif_terrain")
        ax.scatter(x, y, c=value, cmap=cmap, s=18 + alpha * 64, marker="h", alpha=alpha, lw=0)

        png = save_png(fig)
        return Image.open(BytesIO(png)).convert("RGB")

    def _arena_frame(
        self,
        request: RenderRequest,
        width: int,
        height: int,
        index: int,
        frame_count: int,
    ) -> Image.Image:
        fig = create_figure(width, height, "#020202")
        canvas = add_canvas(fig)
        self._draw_arena_header(canvas, request, index, frame_count)
        self._draw_perspective_court(canvas)
        self._draw_animated_arcs(canvas, index, frame_count)
        png = save_png(fig)
        return Image.open(BytesIO(png)).convert("RGB")

    @staticmethod
    def _draw_arena_header(canvas, request: RenderRequest, index: int, frame_count: int) -> None:
        yellow = "#ffd735"
        progress = (index + 1) / frame_count
        points = int(1530 + 264 * progress)

        canvas.add_patch(Circle((0.132, 0.86), 0.105, facecolor="#101010", edgecolor=yellow, lw=4))
        canvas.add_patch(Circle((0.132, 0.88), 0.052, facecolor="#f1c3a4", edgecolor="none"))
        canvas.add_patch(Circle((0.106, 0.89), 0.035, facecolor="#2b1a16", edgecolor="none", alpha=0.95))
        canvas.add_patch(Circle((0.158, 0.89), 0.035, facecolor="#2b1a16", edgecolor="none", alpha=0.95))
        canvas.plot([0.112, 0.152], [0.853, 0.853], color="#6b2b2b", lw=2)

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
            fill = yellow if season_index < int(progress * len(seasons)) + 1 else "none"
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
        canvas.add_patch(Rectangle((0.69, y0), 0.08 * progress, box_h, facecolor=yellow, edgecolor="none"))
        canvas.add_patch(Rectangle((0.69, y0), 0.16, box_h, facecolor="none", edgecolor=yellow, lw=2))
        canvas.text(0.965, 0.83, f"{points:,}", color=yellow, fontsize=44, fontweight="black", ha="right")
        canvas.text(0.31, 0.785, "BY @VannaBushong AND @KirkGoldsberry", color="#8f8f8f", fontsize=16)

    @staticmethod
    def _draw_perspective_court(canvas) -> None:
        court = np.array([[0.02, 0.02], [0.98, 0.02], [0.80, 0.62], [0.18, 0.62]])
        canvas.add_patch(
            Polygon(court, closed=True, facecolor="#5a4728", edgecolor="#d8d4cc", lw=2, alpha=0.78)
        )
        key_polygon = [[0.38, 0.28], [0.62, 0.28], [0.58, 0.54], [0.42, 0.54]]
        canvas.add_patch(
            Polygon(
                key_polygon,
                facecolor="#090909",
                edgecolor="#e6e1d7",
                lw=1.4,
                alpha=0.88,
            )
        )
        canvas.plot([0.10, 0.90], [0.26, 0.26], color="#ded9cf", lw=2, alpha=0.8)
        canvas.add_patch(Circle((0.50, 0.31), 0.105, fill=False, edgecolor="#ded9cf", lw=1.5, alpha=0.75))
        canvas.add_patch(Circle((0.50, 0.42), 0.205, fill=False, edgecolor="#ded9cf", lw=1.5, alpha=0.75))
        canvas.add_patch(Circle((0.50, 0.56), 0.038, fill=False, edgecolor="#ded9cf", lw=1.2, alpha=0.75))
        canvas.plot([0.44, 0.56], [0.21, 0.21], color="#f5d033", lw=4, alpha=0.55)
        canvas.plot([0.44, 0.56], [0.47, 0.47], color="#f5f5f5", lw=3, alpha=0.85)
        canvas.add_patch(Rectangle((0.49, 0.47), 0.055, 0.06, facecolor="none", edgecolor="#f5f5f5", lw=2))
        canvas.add_patch(Rectangle((0.515, 0.48), 0.028, 0.025, facecolor="none", edgecolor="#f5f5f5", lw=1.5))
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
        rng = seeded_rng(22)
        starts = np.column_stack([rng.uniform(0.14, 0.86, 46), rng.uniform(0.16, 0.45, 46)])
        hoop = np.array([0.515, 0.49])
        visible = min(len(starts), int((index + 1) / frame_count * len(starts)) + 3)
        yellow = "#ffe66b"
        for shot_index, start in enumerate(starts[:visible]):
            local_phase = np.clip((index + 1.6 - shot_index * 0.12) / max(frame_count * 0.55, 1), 0, 1)
            if local_phase <= 0:
                continue
            ctrl = (start + hoop) / 2 + np.array([0, rng.uniform(0.16, 0.29)])
            t = np.linspace(0, local_phase, 28)
            curve = (
                (1 - t)[:, None] ** 2 * start
                + 2 * (1 - t)[:, None] * t[:, None] * ctrl
                + t[:, None] ** 2 * hoop
            )
            canvas.plot(curve[:, 0], curve[:, 1], color=yellow, lw=1.2, alpha=0.34)
            canvas.scatter(curve[-1:, 0], curve[-1:, 1], color="#fff3a4", s=18, alpha=0.92, lw=0)
            if local_phase > 0.92:
                canvas.plot([hoop[0], hoop[0]], [hoop[1], hoop[1] + 0.18], color=yellow, lw=2.2, alpha=0.55)

        dots = np.column_stack([rng.uniform(0.12, 0.88, 330), rng.uniform(0.12, 0.47, 330)])
        fade = np.clip((index + 1) / frame_count, 0.25, 1.0)
        canvas.scatter(dots[:, 0], dots[:, 1], s=rng.uniform(4, 14, 330), color=yellow, alpha=0.15 * fade, lw=0)
        makes = np.column_stack([rng.normal(0.52, 0.035, 80), rng.normal(0.48, 0.035, 80)])
        canvas.scatter(makes[:, 0], makes[:, 1], s=rng.uniform(5, 20, 80), color=yellow, alpha=0.32 + 0.25 * fade, lw=0)

"""Animated court shooting GIF renderer skill."""

from __future__ import annotations

from io import BytesIO

from PIL import Image
import numpy as np

from neo_legend.models import RenderRequest, RenderResult
from neo_legend.skills._court import draw_half_court, sample_shots
from neo_legend.skills._plotting import add_canvas, create_figure, make_gradient, save_png
from neo_legend.skills.base import BaseLegendSkill, StyleDefinition


class AnimatedCourtShotSkill(BaseLegendSkill):
    legend_type = "court_shot_animation"
    display_name = "Animated Court Shooting Terrain"
    default_style = "pulse"
    default_size = (1179, 1165)
    media_type = "image/gif"
    file_extension = "gif"
    style_definitions = (
        StyleDefinition(
            "pulse",
            "Animated pulse over the shooting terrain.",
            ("0ca42dfeab11e52e7e4a3a1665b81695.jpg",),
        ),
        StyleDefinition("sweep", "Animated left-to-right scan over shot clusters."),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        frame_count = int(request.data.get("frame_count", 10))
        frames = [self._frame(request, style, width, height, index, frame_count) for index in range(frame_count)]
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

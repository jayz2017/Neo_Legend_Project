"""Luxury bubble / droplet chart renderer skill with 4 artistic styles."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
from matplotlib.figure import Figure
import numpy as np

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._plotting import (
    add_canvas,
    add_reference_footer,
    create_figure,
    save_png,
    seeded_rng,
)
from neo_legend.base import BaseLegendSkill, StyleDefinition


def create_droplet_marker() -> Path:
    vertices = [
        (0.0, 0.5),
        (-0.3, 0.1),
        (-0.45, 0.35),
        (-0.35, 0.65),
        (0.0, 0.95),
        (0.35, 0.65),
        (0.45, 0.35),
        (0.3, 0.1),
        (0.0, 0.5),
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CLOSEPOLY,
    ]
    return Path(vertices, codes)


def create_star_marker(points: int = 8) -> Path:
    outer_r = 1.0
    inner_r = 0.38
    verts = []
    codes = []
    for i in range(points * 2):
        angle = np.pi / 2 + i * np.pi / points
        r = outer_r if i % 2 == 0 else inner_r
        verts.append((r * np.cos(angle), r * np.sin(angle)))
        if i == 0:
            codes.append(Path.MOVETO)
        else:
            codes.append(Path.LINETO)
    verts.append(verts[0])
    codes.append(Path.CLOSEPOLY)
    return Path(verts, codes)


DROPLET_PATH = create_droplet_marker()
STAR_8_PATH = create_star_marker(8)

WATER_COLORS = ["#0077b6", "#00b4d8", "#48cae4", "#90e0ef", "#ade8f4"]
FIREFLY_COLORS = ["#ccff00", "#adff2f", "#ffd700"]
STELLAR_COLORS = ["#ff6b6b", "#feca57", "#74b9ff", "#0984e3"]
CRYSTAL_COLORS = ["#6c5ce7", "#a29bfe", "#fd79a8", "#ffeaa7", "#81ecec"]
DISPERSION_COLORS = ["#ff0000", "#ff8800", "#ffff00", "#00ff00", "#0088ff", "#8800ff"]


class BubbleChartSkill(BaseLegendSkill):
    legend_type = "bubble_chart"
    display_name = "Luxury Bubble Chart"
    default_style = "water_drops"
    default_size = (1179, 1454)
    style_definitions = (
        StyleDefinition(
            "water_drops",
            "Deep-blue teardrop bubbles with refraction highlights and soft shadows.",
        ),
        StyleDefinition(
            "fireflies",
            "Glowing firefly particles with motion trails in a dark night.",
        ),
        StyleDefinition(
            "galaxy_stars",
            "Stellar star-shaped markers with halos and a milky-way backdrop.",
        ),
        StyleDefinition(
            "crystal_orbs",
            "3D crystal spheres with internal textures and rainbow dispersion.",
        ),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._parse_data(request.data)
        dispatch = {
            "water_drops": self._render_water_drops,
            "fireflies": self._render_fireflies,
            "galaxy_stars": self._render_galaxy_stars,
            "crystal_orbs": self._render_crystal_orbs,
        }
        fig = dispatch[style](width, height, data, request.title, request.subtitle)
        return self.result(save_png(fig), style)

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_data(data: dict[str, Any]) -> dict[str, Any]:
        points = data.get("points")
        if isinstance(points, list) and len(points) > 0:
            return data
        rng = seeded_rng(2026)
        n = rng.integers(12, 22)
        xs = rng.uniform(0.08, 0.92, size=n).tolist()
        ys = rng.uniform(0.10, 0.82, size=n).tolist()
        sizes = rng.uniform(200, 1200, size=n).tolist()
        colors_idx = rng.integers(0, 5, size=n).tolist()
        labels = [chr(65 + i % 26) for i in range(n)]
        palette = WATER_COLORS + FIREFLY_COLORS + STELLAR_COLORS + CRYSTAL_COLORS
        color_list = [palette[c % len(palette)] for c in colors_idx]
        return {
            "points": [
                {"x": x, "y": y, "size": s, "color": col, "label": lab}
                for x, y, s, col, lab in zip(xs, ys, sizes, color_list, labels)
            ],
            "x_axis": data.get("x_axis", {"label": "X Axis"}),
            "y_axis": data.get("y_axis", {"label": "Y Axis"}),
        }

    @staticmethod
    def _prevent_overlap(xs: list[float], ys: list[float], sizes: list[float], rng: np.random.Generator) -> tuple[list, list]:
        n = len(xs)
        new_xs, new_ys = list(xs), list(ys)
        for i in range(n):
            for j in range(i + 1, n):
                dx = new_xs[i] - new_xs[j]
                dy = new_ys[i] - new_ys[j]
                dist = np.hypot(dx, dy)
                min_dist = ((sizes[i] ** 0.5) + (sizes[j] ** 0.5)) * 0.00055
                if dist < min_dist and dist > 1e-9:
                    offset = (min_dist - dist) * 0.5 + rng.uniform(0.002, 0.008)
                    angle = rng.uniform(0, 2 * np.pi)
                    new_xs[i] += offset * np.cos(angle)
                    new_ys[i] += offset * np.sin(angle)
                    new_xs[j] -= offset * np.cos(angle)
                    new_ys[j] -= offset * np.sin(angle)
        return new_xs, new_ys

    # ==================================================================
    # STYLE 1 – Water Drops
    # ==================================================================

    def _render_water_drops(
        self, width: int, height: int, data: dict[str, Any], title: str | None, subtitle: str | None
    ) -> Figure:
        fig = create_figure(width, height, "#0a2647")
        canvas = add_canvas(fig)
        self._draw_header(canvas, title or "Water Drops", subtitle, "#caf0f8", "#90e0ef")
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.78], facecolor="none")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_axis_off()

        points = data["points"]
        rng = seeded_rng(42)
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        sizes = [p["size"] for p in points]
        xs, ys = self._prevent_overlap(xs, ys, sizes, rng)

        scale = 0.00105
        for idx, p in enumerate(points):
            x, y, s = xs[idx], ys[idx], p["size"]
            base_size = max(s * scale, 25)
            color = p.get("color") or WATER_COLORS[idx % len(WATER_COLORS)]

            shadow = mpatches.Ellipse(
                (x + 0.018, y - 0.02), base_size * 0.85, base_size * 0.45, angle=-15, fc="#041c33", alpha=0.22, zorder=1
            )
            ax.add_patch(shadow)

            ax.scatter(
                [x],
                [y],
                s=base_size,
                c=[color],
                marker=DROPLET_PATH,
                edgecolors="#ffffff",
                linewidths=0.4,
                alpha=0.72,
                zorder=3,
            )

            hl_w = base_size * 0.28
            hl_h = base_size * 0.18
            highlight = mpatches.Arc(
                (x - base_size * 0.08, y + base_size * 0.14),
                hl_w,
                hl_h,
                angle=25,
                theta1=15,
                theta2=145,
                fc="none",
                ec="#ffffff",
                linewidth=base_size * 0.0045,
                alpha=0.58,
                zorder=4,
                capstyle="round",
            )
            ax.add_patch(highlight)

            hl2_w = base_size * 0.14
            hl2_h = base_size * 0.09
            highlight2 = mpatches.Arc(
                (x - base_size * 0.03, y + base_size * 0.24),
                hl2_w,
                hl2_h,
                angle=20,
                theta1=30,
                theta2=130,
                fc="none",
                ec="#ffffff",
                linewidth=base_size * 0.0028,
                alpha=0.38,
                zorder=4,
                capstyle="round",
            )
            ax.add_patch(highlight2)

        self._draw_axes_decor(ax, data, "#48cae4", "#90e0ef")
        add_reference_footer(canvas, "Luxury Bubble Chart · Water Drops Style | Generated by Neo Legend", "#5a8a9e")
        return fig

    # ==================================================================
    # STYLE 2 – Fireflies
    # ==================================================================

    def _render_fireflies(
        self, width: int, height: int, data: dict[str, Any], title: str | None, subtitle: str | None
    ) -> Figure:
        fig = create_figure(width, height, "#0d0d0d")
        canvas = add_canvas(fig)
        self._draw_header(canvas, title or "Fireflies", subtitle, "#e8ff6a", "#adff2f")
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.78], facecolor="none")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_axis_off()

        rng = seeded_rng(77)
        n_stars = rng.integers(60, 100)
        star_x = rng.uniform(0, 1, size=n_stars)
        star_y = rng.uniform(0, 1, size=n_stars)
        star_s = rng.uniform(0.15, 1.2, size=n_stars)
        star_a = rng.uniform(0.06, 0.28, size=n_stars)
        star_c = rng.choice(["#ffffff", "#fffacd", "#f0e68c"], size=n_stars)
        ax.scatter(star_x, star_y, s=star_s, c=star_c, alpha=star_a, zorder=0)

        center_glow = plt.Circle((0.5, 0.46), 0.42, fc="#1a2500", alpha=0.07, zorder=0)
        ax.add_patch(center_glow)

        points = data["points"]
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        sizes = [p["size"] for p in points]
        xs, ys = self._prevent_overlap(xs, ys, sizes, rng)

        scale = 0.00085
        glow_layers = [(1.0, 0.88), (1.6, 0.38), (2.3, 0.14), (3.0, 0.04)]
        trail_len = 4

        for idx, p in enumerate(points):
            x, y, s = xs[idx], ys[idx], p["size"]
            base_r = max(s * scale, 18)
            core_color = p.get("color") or FIREFLY_COLORS[idx % len(FIREFLY_COLORS)]
            trail_angle = rng.uniform(0, 2 * np.pi)

            for t in range(trail_len, 0, -1):
                tx = x - np.cos(trail_angle) * t * base_r * 0.0022
                ty = y - np.sin(trail_angle) * t * base_r * 0.0022
                ts = base_r * (1 - t * 0.17)
                ta = 0.06 + (1 - t / trail_len) * 0.12
                ax.scatter([tx], [ty], s=ts, c=[core_color], alpha=ta, zorder=2)

            for mult, ga in glow_layers:
                ax.scatter(
                    [x],
                    [y],
                    s=base_r * mult,
                    c=[core_color],
                    alpha=ga,
                    zorder=3,
                )
            ax.scatter([x], [y], s=base_r * 0.65, c=["#ffffff"], alpha=0.92, zorder=4)

        self._draw_axes_decor(ax, data, "#ccff00", "#adff2f")
        add_reference_footer(canvas, "Luxury Bubble Chart · Fireflies Style | Generated by Neo Legend", "#667700")
        return fig

    # ==================================================================
    # STYLE 3 – Galaxy Stars
    # ==================================================================

    def _render_galaxy_stars(
        self, width: int, height: int, data: dict[str, Any], title: str | None, subtitle: str | None
    ) -> Figure:
        fig = create_figure(width, height, "#050510")
        canvas = add_canvas(fig)
        self._draw_header(canvas, title or "Galaxy Stars", subtitle, "#d4e0ff", "#74b9ff")
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.78], facecolor="none")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_axis_off()

        rng = seeded_rng(135)
        mw_n = 400
        gx_base = rng.uniform(-0.3, 1.3, size=mw_n)
        gy_base = rng.uniform(-0.3, 1.3, size=mw_n)
        dist_from_diag = np.abs(gx_base - gy_base)
        mask = dist_from_diag < 0.28 + rng.uniform(0, 0.12, size=mw_n)
        mw_alpha = np.where(mask, rng.uniform(0.01, 0.06, size=mw_n), 0)
        ax.scatter(gx_base[mask], gy_base[mask], s=rng.uniform(0.1, 1.5, size=mw_n)[mask], c=["#e8dcc8"] * mask.sum(), alpha=mw_alpha[mask], zorder=0)

        points = data["points"]
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        sizes = [p["size"] for p in points]
        xs, ys = self._prevent_overlap(xs, ys, sizes, rng)

        scale = 0.0011
        constellation_groups: dict[str, list[tuple[int, float, float]]] = {}
        for idx, p in enumerate(points):
            grp = p.get("constellation", f"g{idx % 3}")
            constellation_groups.setdefault(grp, []).append((idx, xs[idx], ys[idx]))

        for idx, p in enumerate(points):
            x, y, s = xs[idx], ys[idx], p["size"]
            base_size = max(s * scale, 30)
            color = p.get("color") or STELLAR_COLORS[idx % len(STELLAR_COLORS)]

            halo_sizes = [base_size * 3.2, base_size * 2.1, base_size * 1.4]
            halo_alphas = [0.04, 0.09, 0.18]
            for hs, ha in zip(halo_sizes, halo_alphas):
                ax.scatter([x], [y], s=hs, c=[color], alpha=ha, zorder=2)

            ax.scatter(
                [x],
                [y],
                s=base_size,
                c=[color],
                marker=STAR_8_PATH,
                edgecolors="#ffffff",
                linewidths=0.3,
                alpha=0.9,
                zorder=4,
            )
            ax.scatter([x], [y], s=base_size * 0.22, c=["#ffffff"], alpha=0.95, zorder=5)

        for group_members in constellation_groups.values():
            if len(group_members) >= 2:
                sorted_m = sorted(group_members, key=lambda m: m[0])
                line_xs = [m[1] for m in sorted_m]
                line_ys = [m[2] for m in sorted_m]
                ax.plot(line_xs, line_ys, color="#ffffff", linewidth=0.4, alpha=0.12, zorder=1)

        self._draw_axes_decor(ax, data, "#74b9ff", "#dfe6e9")
        add_reference_footer(canvas, "Luxury Bubble Chart · Galaxy Stars Style | Generated by Neo Legend", "#4a5568")
        return fig

    # ==================================================================
    # STYLE 4 – Crystal Orbs
    # ==================================================================

    def _render_crystal_orbs(
        self, width: int, height: int, data: dict[str, Any], title: str | None, subtitle: str | None
    ) -> Figure:
        fig = create_figure(width, height, "#1a0a2e")
        canvas = add_canvas(fig)
        self._draw_header(canvas, title or "Crystal Orbs", subtitle, "#e8d5ff", "#a29bfe")
        ax = fig.add_axes([0.06, 0.08, 0.88, 0.78], facecolor="none")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_axis_off()

        points = data["points"]
        rng = seeded_rng(210)
        xs = [p["x"] for p in points]
        ys = [p["y"] for p in points]
        sizes = [p["size"] for p in points]
        xs, ys = self._prevent_overlap(xs, ys, sizes, rng)

        scale = 0.0010
        sphere_layers = [
            (3.8, 0.04, 0.03),
            (2.6, 0.08, 0.05),
            (1.7, 0.13, 0.08),
            (1.25, 0.22, 0.12),
            (0.9, 0.42, 0.25),
            (0.55, 0.70, 0.50),
        ]

        for idx, p in enumerate(points):
            x, y, s = xs[idx], ys[idx], p["size"]
            base_r = max(s * scale, 30)
            color = p.get("color") or CRYSTAL_COLORS[idx % len(CRYSTAL_COLORS)]

            for mult, out_a, in_a in sphere_layers:
                layer_color = self._darken(color, 1 - (out_a * 1.8))
                ax.scatter([x], [y], s=base_r * mult, c=[layer_color], alpha=out_a, zorder=2)

            ax.scatter(
                [x],
                [y],
                s=base_r * 0.82,
                c=[color],
                edgecolors=self._lighten(color, 0.35),
                linewidths=0.8,
                alpha=0.78,
                zorder=4,
            )

            for di in range(3):
                spiral_theta = np.linspace(0, 2.2 * np.pi, 50)
                sp_r = base_r * 0.0018 * (di + 1) * 0.55
                sp_x = x + sp_r * np.cos(spiral_theta + di * 2.1) * spiral_theta / (2.2 * np.pi)
                sp_y = y + sp_r * np.sin(spiral_theta + di * 2.1) * spiral_theta / (2.2 * np.pi)
                ax.plot(sp_x, sp_y, color="#ffffff", linewidth=0.25, alpha=0.06 + di * 0.02, zorder=3)

            hex_r = base_r * 0.32
            for hi in range(6):
                angle = hi * np.pi / 3 + np.pi / 6
                hx1 = x + hex_r * 0.012 * np.cos(angle)
                hy1 = y + hex_r * 0.012 * np.sin(angle)
                hx2 = x + hex_r * 0.012 * np.cos(angle + np.pi / 3)
                hy2 = y + hex_r * 0.012 * np.sin(angle + np.pi / 3)
                ax.plot([hx1, hx2], [hy1, hy2], color="#ffffff", linewidth=0.2, alpha=0.07, zorder=3)

            disp_w = base_r * 1.18
            for ci, dc in enumerate(DISPERSION_COLORS):
                disp_ring = plt.Circle(
                    (x, y),
                    disp_w * (1 - ci * 0.025),
                    fill=False,
                    edgecolor=dc,
                    linewidth=0.4 + (ci % 2) * 0.2,
                    alpha=0.12 - ci * 0.015,
                    zorder=5,
                )
                ax.add_patch(disp_ring)

            hl_r = base_r * 0.16
            highlight = mpatches.Ellipse(
                (x - base_r * 0.11, y + base_r * 0.18),
                hl_r,
                hl_r * 0.55,
                angle=30,
                fc="#ffffff",
                alpha=0.52,
                zorder=6,
            )
            ax.add_patch(highlight)

        self._draw_axes_decor(ax, data, "#a29bfe", "#dfe6e9")
        add_reference_footer(canvas, "Luxury Bubble Chart · Crystal Orbs Style | Generated by Neo Legend", "#6c5ce7")
        return fig

    # ------------------------------------------------------------------
    # Shared UI helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _draw_header(
        canvas: plt.Axes, title: str, subtitle: str | None, title_color: str, subtitle_color: str
    ) -> None:
        canvas.text(
            0.5,
            0.94,
            title,
            color=title_color,
            fontsize=52,
            fontweight="black",
            ha="center",
        )
        if subtitle:
            canvas.text(
                0.5,
                0.898,
                subtitle,
                color=subtitle_color,
                fontsize=16,
                ha="center",
            )

    @staticmethod
    def _draw_axes_decor(ax: plt.Axes, data: dict[str, Any], label_color: str, tick_color: str) -> None:
        x_info = data.get("x_axis", {})
        y_info = data.get("y_axis", {})
        x_label = x_info.get("label", "")
        y_label = y_info.get("label", "")

        ax.spines["bottom"].set_visible(True)
        ax.spines["left"].set_visible(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(label_color)
        ax.spines["left"].set_color(label_color)
        ax.spines["bottom"].set_linewidth(0.6)
        ax.spines["left"].set_linewidth(0.6)
        ax.spines["bottom"].set_alpha(0.45)
        ax.spines["left"].set_alpha(0.45)

        ax.set_xlabel(x_label, color=label_color, fontsize=11, alpha=0.7, labelpad=6)
        ax.set_ylabel(y_label, color=label_color, fontsize=11, alpha=0.7, labelpad=6)
        ax.tick_params(colors=label_color, labelsize=8, length=3)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_alpha(0.55)

    @staticmethod
    def _darken(hex_color: str, factor: float) -> str:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _lighten(hex_color: str, amount: float) -> str:
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return f"#{r:02x}{g:02x}{b:02x}"

"""Luxury Sankey Diagram / Flow Chart renderer skill."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse as MplEllipse, FancyBboxPatch, PathPatch
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


class SankeyChartSkill(BaseLegendSkill):
    legend_type = "sankey_chart"
    display_name = "Luxury Sankey Diagram"
    default_style = "neon_streams"
    default_size = (1400, 1000)
    style_definitions = (
        StyleDefinition(
            "neon_streams",
            "Neon glow flow bands on dark tech background.",
        ),
        StyleDefinition(
            "energy_flow",
            "Heat-map colored energy flow with particle effects.",
        ),
        StyleDefinition(
            "crystal_rivers",
            "Transparent gradient ice-blue river flows.",
        ),
        StyleDefinition(
            "golden_paths",
            "Luxurious gold-toned flow paths with radiant nodes.",
        ),
    )

    _NEON_COLORS = ["#ff0055", "#00ff99", "#00ccff", "#ffcc00", "#ff00ff", "#ff6b35", "#7b68ee"]
    _ENERGY_COLORS_COLD = ["#0077b6", "#00b4d8", "#48cae4", "#90e0ef"]
    _ENERGY_COLORS_HOT = ["#ffb703", "#fb8500", "#e63946"]
    _CRYSTAL_COLORS = ["#caf0f8", "#90e0ef", "#00b4d8", "#0077b6", "#023e8a"]
    _GOLDEN_COLORS = ["#FFD700", "#FFA500", "#FF8C00", "#B8860B", "#DAA520"]

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        bg = self._bg_color(style)
        fig = create_figure(width, height, bg)
        canvas = add_canvas(fig)

        data = self._resolve_data(request.data)
        nodes, flows = self._prepare_layout(data)

        self._draw_title(canvas, request.title, request.subtitle, style)
        self._draw_decorations(canvas, style)

        renderer = {
            "neon_streams": self._render_neon,
            "energy_flow": self._render_energy,
            "crystal_rivers": self._render_crystal,
            "golden_paths": self._render_golden,
        }[style]
        renderer(canvas, nodes, flows)

        add_reference_footer(canvas, "FLOW ANALYSIS | NEO LEGEND")
        return self.result(save_png(fig), style)

    # ── data & layout ──────────────────────────────────────────────

    @staticmethod
    def _default_data() -> dict[str, Any]:
        return {
            "nodes": [
                {"id": "shots", "label": "Total Shots", "x": 0.08, "y": 0.50},
                {"id": "2pt", "label": "2-Pointers", "x": 0.36, "y": 0.72},
                {"id": "3pt", "label": "3-Pointers", "x": 0.36, "y": 0.28},
                {"id": "made", "label": "Made", "x": 0.64, "y": 0.62},
                {"id": "missed", "label": "Missed", "x": 0.64, "y": 0.38},
                {"id": "points", "label": "Points Scored", "x": 0.88, "y": 0.50},
            ],
            "flows": [
                {"source": "shots", "target": "2pt", "value": 650, "color": "#ff0055"},
                {"source": "shots", "target": "3pt", "value": 350, "color": "#00ccff"},
                {"source": "2pt", "target": "made", "value": 390, "color": "#00ff99"},
                {"source": "2pt", "target": "missed", "value": 260, "color": "#ffcc00"},
                {"source": "3pt", "target": "made", "value": 140, "color": "#ff00ff"},
                {"source": "3pt", "target": "missed", "value": 210, "color": "#ff6b35"},
                {"source": "made", "target": "points", "value": 920, "color": "#7b68ee"},
            ],
        }

    def _resolve_data(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("nodes") and data.get("flows"):
            return data
        return self._default_data()

    @staticmethod
    def _prepare_layout(data: dict[str, Any]):
        nodes_raw = data["nodes"]
        flows_raw = data["flows"]
        node_map = {n["id"]: n for n in nodes_raw}
        max_val = max((f["value"] for f in flows_raw), default=1)
        nodes = []
        for n in nodes_raw:
            x = n.get("x")
            y = n.get("y")
            if x is None or y is None:
                x, y = 0.5, 0.5
            nodes.append({"id": n["id"], "label": n.get("label", n["id"]), "x": float(x), "y": float(y)})

        flows = []
        for f in flows_raw:
            src = node_map[f["source"]]
            tgt = node_map[f["target"]]
            flows.append(
                {
                    "source_id": f["source"],
                    "target_id": f["target"],
                    "value": f["value"],
                    "color": f.get("color", "#ffffff"),
                    "sx": float(src["x"]),
                    "sy": float(src["y"]),
                    "tx": float(tgt["x"]),
                    "ty": float(tgt["y"]),
                    "norm_value": f["value"] / max_val,
                }
            )
        return nodes, flows

    # ── background / title helpers ────────────────────────────────

    @staticmethod
    def _bg_color(style: str) -> str:
        return {
            "neon_streams": "#0a0a1a",
            "energy_flow": "#1a1a2e",
            "crystal_rivers": "#0d1b2a",
            "golden_paths": "#1a1410",
        }[style]

    def _draw_title(self, canvas: plt.Axes, title: str | None, subtitle: str | None, style: str) -> None:
        title_colors = {
            "neon_streams": "#e0e0ff",
            "energy_flow": "#ffd166",
            "crystal_rivers": "#caf0f8",
            "golden_paths": "#FFD700",
        }
        sub_colors = {
            "neon_streams": "#6a6a9a",
            "energy_flow": "#8d99ae",
            "crystal_rivers": "#48cae4",
            "golden_paths": "#c9a227",
        }
        canvas.text(
            0.5,
            0.94,
            (title or "Flow Analysis").upper(),
            color=title_colors.get(style, "#ffffff"),
            fontsize=48,
            fontweight="black",
            ha="center",
            va="center",
            family="sans-serif",
        )
        canvas.text(
            0.5,
            0.89,
            subtitle or "Data Flow Visualization | Neo Legend Engine",
            color=sub_colors.get(style, "#aaaaaa"),
            fontsize=16,
            ha="center",
            va="center",
            alpha=0.8,
        )

    def _draw_decorations(self, canvas: plt.Axes, style: str) -> None:
        if style == "neon_streams":
            for i in range(21):
                canvas.axhline(i / 20, color="#ffffff", alpha=0.03, linewidth=0.4)
            for i in range(31):
                canvas.axvline(i / 30, color="#ffffff", alpha=0.025, linewidth=0.4)
        elif style == "golden_paths":
            corners = [(0.02, 0.96), (0.98, 0.96), (0.02, 0.04), (0.98, 0.04)]
            for cx, cy in corners:
                for angle in np.linspace(0, 2 * np.pi, 6, endpoint=False):
                    ex = cx + 0.025 * np.cos(angle)
                    ey = cy + 0.025 * np.sin(angle)
                    canvas.plot([cx, ex], [cy, ey], color="#FFD700", linewidth=0.5, alpha=0.18)

    # ══════════════════════════════════════════════════════════════
    #  STYLE 1 – NEON STREAMS
    # ══════════════════════════════════════════════════════════════

    def _render_neon(self, canvas: plt.Axes, nodes: list, flows: list) -> None:
        for idx, flow in enumerate(flows):
            color = flow["color"] or self._NEON_COLORS[idx % len(self._NEON_COLORS)]
            nv = flow["norm_value"]
            w_base = 0.008 + nv * 0.035
            self._draw_glow_band(canvas, flow["sx"], flow["sy"], flow["tx"], flow["ty"],
                                 w_base, color)
            mx = (flow["sx"] + flow["tx"]) / 2
            my = (flow["sy"] + flow["ty"]) / 2
            canvas.text(mx, my + 0.015, f"{int(flow['value'])}",
                        color="#ffffff", fontsize=8, ha="center", va="center", alpha=0.85,
                        family="monospace")

        for idx, node in enumerate(nodes):
            color = self._NEON_COLORS[idx % len(self._NEON_COLORS)]
            self._draw_neon_node(canvas, node["x"], node["y"], node["label"], color)

    @staticmethod
    def _draw_glow_band(canvas: plt.Axes, sx: float, sy: float, tx: float, ty: float,
                        width: float, color: str) -> None:
        layers = [
            (width * 3.2, 0.06, 0),
            (width * 2.2, 0.13, 0),
            (width * 1.5, 0.30, 0),
            (width * 1.0, 0.78, 0.5),
        ]
        for w, a, lw in layers:
            verts = _band_vertices(sx, sy, tx, ty, w)
            codes = [Path.MOVETO] + [Path.CURVE4] * 7 + [Path.CLOSEPOLY]
            patch = PathPatch(Path(verts, codes), facecolor=color, edgecolor=color,
                              alpha=a, linewidth=lw, capstyle="round", joinstyle="round")
            canvas.add_patch(patch)

    @staticmethod
    def _draw_neon_node(canvas: plt.Axes, x: float, y: float, label: str, color: str) -> None:
        for r, a, lw in [(0.055, 0.06, 0), (0.045, 0.12, 0), (0.036, 0.28, 0), (0.028, 0.75, 1.0)]:
            circle = plt.Circle((x, y), r, facecolor=color if a > 0.5 else "none",
                                edgecolor=color, alpha=a, linewidth=lw)
            canvas.add_patch(circle)
        inner = plt.Circle((x, y), 0.020, facecolor=_lighten(color, 0.3),
                           edgecolor="none", alpha=0.55)
        canvas.add_patch(inner)
        canvas.text(x, y - 0.072, label, color="#dddddd", fontsize=10, ha="center",
                    va="top", family="monospace", fontweight="bold")

    # ══════════════════════════════════════════════════════════════
    #  STYLE 2 – ENERGY FLOW
    # ══════════════════════════════════════════════════════════════

    def _render_energy(self, canvas: plt.Axes, nodes: list, flows: list) -> None:
        all_values = [f["value"] for f in flows]
        vmin, vmax = min(all_values), max(all_values)
        for flow in flows:
            t = (flow["value"] - vmin) / (vmax - vmin) if vmax > vmin else 0.5
            if t < 0.5:
                color = cmap_color(self._ENERGY_COLORS_COLD, t * 2)
            else:
                color = cmap_color(self._ENERGY_COLORS_HOT, (t - 0.5) * 2)
            w = 0.006 + flow["norm_value"] * 0.038
            self._draw_solid_band(canvas, flow["sx"], flow["sy"], flow["tx"], flow["ty"], w, color, 0.65)
            pct = flow["value"] / sum(all_values) * 100
            mx = (flow["sx"] + flow["tx"]) / 2
            my = (flow["sy"] + flow["ty"]) / 2
            canvas.text(mx, my + 0.014, f"{pct:.0f}%", color="#ffffff", fontsize=9,
                        ha="center", va="center", fontweight="bold", alpha=0.92)
            self._scatter_particles(canvas, flow["sx"], flow["sy"], flow["tx"], flow["ty"], color, int(flow["value"] / 80))

        node_totals = {n["id"]: 0 for n in nodes}
        for f in flows:
            node_totals[f["source_id"]] += f["value"]
            node_totals[f["target_id"]] += f["value"]
        nt_max = max(node_totals.values()) if node_totals else 1
        for node in nodes:
            total = node_totals[node["id"]]
            intensity = total / nt_max if nt_max else 0.5
            heat_color = cmap_color(self._ENERGY_COLORS_COLD + self._ENERGY_COLORS_HOT, intensity)
            self._draw_heat_node(canvas, node["x"], node["y"], node["label"], heat_color, intensity)

    @staticmethod
    def _draw_solid_band(canvas: plt.Axes, sx: float, sy: float, tx: float, ty: float,
                         width: float, color: str, alpha: float) -> None:
        verts = _band_vertices(sx, sy, tx, ty, width)
        codes = [Path.MOVETO] + [Path.CURVE4] * 7 + [Path.CLOSEPOLY]
        canvas.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none",
                                   alpha=alpha, capstyle="round", joinstyle="round"))

    @staticmethod
    def _scatter_particles(canvas: plt.Axes, sx: float, sy: float, tx: float, ty: float,
                           color: str, count: int) -> None:
        rng = np.random.default_rng(hash((sx, sy, tx, ty)) % (2**32))
        for _ in range(min(count, 18)):
            t = rng.uniform(0.15, 0.85)
            px = sx + (tx - sx) * t + rng.normal(0, 0.008)
            py = sy + (ty - sy) * t + rng.normal(0, 0.012)
            sz = rng.uniform(0.003, 0.010)
            canvas.add_patch(plt.Circle((px, py), sz, facecolor=color, alpha=0.55, edgecolor="none"))

    @staticmethod
    def _draw_heat_node(canvas: plt.Axes, x: float, y: float, label: str,
                        color: str, intensity: float) -> None:
        for r_mult, a in [(2.0, 0.06), (1.55, 0.12), (1.2, 0.22)]:
            canvas.add_patch(plt.Circle((x, y), 0.032 * r_mult, facecolor="none",
                                        edgecolor=color, linewidth=1.2, alpha=a))
        canvas.add_patch(plt.Circle((x, y), 0.030, facecolor=color, edgecolor="white",
                                    alpha=0.82, linewidth=1.0))
        canvas.text(x, y - 0.055, label, color="#eeeeee", fontsize=10, ha="center",
                    va="top", fontweight="bold")

    # ══════════════════════════════════════════════════════════════
    #  STYLE 3 – CRYSTAL RIVERS
    # ══════════════════════════════════════════════════════════════

    def _render_crystal(self, canvas: plt.Axes, nodes: list, flows: list) -> None:
        target_flows: dict[str, list] = {}
        for f in flows:
            target_flows.setdefault(f["target_id"], []).append(f)

        for idx, flow in enumerate(flows):
            color = flow["color"] or self._CRYSTAL_COLORS[idx % len(self._CRYSTAL_COLORS)]
            w = 0.006 + flow["norm_value"] * 0.034
            self._draw_gradient_band(canvas, flow["sx"], flow["sy"], flow["tx"], flow["ty"],
                                     w, color, 0.70, 0.10)
            self._draw_refraction_lines(canvas, flow["sx"], flow["sy"], flow["tx"], flow["ty"],
                                        w, color)

        for idx, node in enumerate(nodes):
            color = self._CRYSTAL_COLORS[idx % len(self._CRYSTAL_COLORS)]
            self._draw_crystal_node(canvas, node["x"], node["y"], node["label"], color)

    @staticmethod
    def _draw_gradient_band(canvas: plt.Axes, sx: float, sy: float, tx: float, ty: float,
                            width: float, color: str, alpha_start: float, alpha_end: float) -> None:
        segments = 14
        for i in range(segments):
            t0 = i / segments
            t1 = (i + 1) / segments
            frac = (t0 + t1) / 2
            ax_ = sx + (tx - sx) * t0
            ay_ = sy + (ty - sy) * t0
            bx_ = sx + (tx - sx) * t1
            by_ = sy + (ty - sy) * t1
            alpha = alpha_start + (alpha_end - alpha_start) * frac
            w_seg = width * (1.0 - frac * 0.25)
            verts = _band_vertices(ax_, ay_, bx_, by_, w_seg)
            codes = [Path.MOVETO] + [Path.CURVE4] * 7 + [Path.CLOSEPOLY]
            canvas.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none",
                                       alpha=max(alpha, 0.04), capstyle="butt", joinstyle="round"))

    @staticmethod
    def _draw_refraction_lines(canvas: plt.Axes, sx: float, sy: float, tx: float, ty: float,
                               width: float, base_color: str) -> None:
        steps = 20
        for i in range(steps):
            t = i / steps
            cx = sx + (tx - sx) * t
            cy = sy + (ty - sy) * t
            hw = width * 0.45 * (1.0 - t * 0.2)
            dx = (ty - sy)
            dy = -(tx - sx)
            dlen = np.hypot(dx, dy) or 1.0
            dx /= dlen
            dy /= dlen
            canvas.plot([cx - dx * hw, cx + dx * hw], [cy - dy * hw, cy + dy * hw],
                        color="#ffffff", alpha=0.06, linewidth=0.35)

    @staticmethod
    def _draw_crystal_node(canvas: plt.Axes, x: float, y: float, label: str, color: str) -> None:
        ellipse = MplEllipse((x, y), 0.070, 0.044, angle=0,
                              facecolor=_lighten(color, 0.25), edgecolor="#ffffff",
                              alpha=0.85, linewidth=1.4)
        canvas.add_patch(ellipse)
        inner = MplEllipse((x, y), 0.042, 0.026, angle=0,
                            facecolor=_lighten(color, 0.55), edgecolor="none", alpha=0.40)
        canvas.add_patch(inner)
        canvas.text(x, y - 0.04, label, color="#d0e8ef", fontsize=10, ha="center",
                    va="top", fontweight="bold", alpha=0.92)

    # ══════════════════════════════════════════════════════════════
    #  STYLE 4 – GOLDEN PATHS
    # ══════════════════════════════════════════════════════════════

    def _render_golden(self, canvas: plt.Axes, nodes: list, flows: list) -> None:
        source_ids = {f["source_id"] for f in flows}
        sink_ids = {f["target_id"] for f in flows}
        for idx, flow in enumerate(flows):
            color = flow["color"] or self._GOLDEN_COLORS[idx % len(self._GOLDEN_COLORS)]
            w = 0.007 + flow["norm_value"] * 0.036
            self._draw_gold_band(canvas, flow["sx"], flow["sy"], flow["tx"], flow["ty"], w, color)
            mx = (flow["sx"] + flow["tx"]) / 2
            my = (flow["sy"] + flow["ty"]) / 2
            is_important = flow["norm_value"] > 0.65
            txt = f"{'* ' if is_important else ''}{int(flow['value'])}"
            canvas.text(mx, my + 0.016, txt, color="#fff8e0", fontsize=9 if is_important else 8,
                        ha="center", va="center", family="serif", alpha=0.92)

        for idx, node in enumerate(nodes):
            color = self._GOLDEN_COLORS[idx % len(self._GOLDEN_COLORS)]
            is_source_or_sink = node["id"] in source_ids or node["id"] in sink_ids
            self._draw_golden_node(canvas, node["x"], node["y"], node["label"], color,
                                   is_source_or_sink, node["id"])

    @staticmethod
    def _draw_gold_band(canvas: plt.Axes, sx: float, sy: float, tx: float, ty: float,
                        width: float, color: str) -> None:
        glow_layers = [
            (width * 2.6, 0.07, 0),
            (width * 1.8, 0.15, 0),
            (width * 1.25, 0.38, 0),
            (width * 1.0, 0.80, 0.6),
        ]
        for w, a, lw in glow_layers:
            verts = _band_vertices(sx, sy, tx, ty, w)
            codes = [Path.MOVETO] + [Path.CURVE4] * 7 + [Path.CLOSEPOLY]
            canvas.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor=color,
                                       alpha=a, linewidth=lw, capstyle="round", joinstyle="round"))

    @staticmethod
    def _draw_golden_node(canvas: plt.Axes, x: float, y: float, label: str, color: str,
                          radiant: bool, node_id: str) -> None:
        shadow = FancyBboxPatch((x - 0.032 + 0.005, y - 0.020 + 0.005), 0.064, 0.040,
                                boxstyle="round,pad=0.008,rounding_size=0.01",
                                facecolor="#000000", edgecolor="none", alpha=0.30)
        canvas.add_patch(shadow)
        box = FancyBboxPatch((x - 0.032, y - 0.020), 0.064, 0.040,
                             boxstyle="round,pad=0.008,rounding_size=0.01",
                             facecolor=_darken(color, 0.35), edgecolor=color,
                             linewidth=2.6, alpha=0.92)
        canvas.add_patch(box)
        inner_box = FancyBboxPatch((x - 0.022, y - 0.013), 0.044, 0.026,
                                   boxstyle="round,pad=0.004,rounding_size=0.006",
                                   facecolor=_lighten(color, 0.2), edgecolor="none",
                                   alpha=0.30)
        canvas.add_patch(inner_box)
        canvas.text(x, y, label, color="#fff8e0", fontsize=9, ha="center", va="center",
                    family="serif", fontweight="bold", alpha=0.95)
        if radiant:
            num_rays = 12
            for i in range(num_rays):
                angle = 2 * np.pi * i / num_rays + np.pi / num_rays
                ray_len = 0.035 + 0.018 * ((i % 3) / 2)
                rx = x + ray_len * np.cos(angle)
                ry = y + ray_len * np.sin(angle)
                canvas.plot([x, rx], [y, ry], color="#FFD700", linewidth=0.6,
                            alpha=0.12 + 0.08 * (1 - abs(np.sin(angle))), solid_capstyle="round")


def _band_vertices(sx: float, sy: float, tx: float, ty: float, half_w: float) -> list:
    dx = tx - sx
    dy = ty - sy
    dist = np.hypot(dx, dy)
    if dist < 1e-8:
        nx, ny = 1.0, 0.0
    else:
        nx, ny = -dy / dist, dx / dist
    perp_x = nx * half_w
    perp_y = ny * half_w
    cx = sx + dx * 0.5
    cy = sy + dy * 0.5
    offset = dist * 0.12
    ctrl_x = cx - ny * offset
    ctrl_y = cy + nx * offset
    return [
        (sx - perp_x, sy - perp_y),
        (ctrl_x - perp_x * 0.6, ctrl_y - perp_y * 0.6),
        (tx - perp_x * 0.85, ty - perp_y * 0.85),
        (tx - perp_x * 0.3, ty - perp_y * 0.3),
        (tx + perp_x * 0.3, ty + perp_y * 0.3),
        (tx + perp_x * 0.85, ty + perp_y * 0.85),
        (ctrl_x + perp_x * 0.6, ctrl_y + perp_y * 0.6),
        (sx + perp_x, sy + perp_y),
        (sx - perp_x, sy - perp_y),
    ]


def _lighten(hex_color: str, amount: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = min(255, int(hex_color[0:2], 16) + int(amount * 255))
    g = min(255, int(hex_color[2:4], 16) + int(amount * 255))
    b = min(255, int(hex_color[4:6], 16) + int(amount * 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def _darken(hex_color: str, amount: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = max(0, int(hex_color[0:2], 16) - int(amount * 255))
    g = max(0, int(hex_color[2:4], 16) - int(amount * 255))
    b = max(0, int(hex_color[4:6], 16) - int(amount * 255))
    return f"#{r:02x}{g:02x}{b:02x}"

"""Dual radar comparison renderer skill."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Polygon

from neo_legend.models import RenderRequest, RenderResult
from neo_legend._plotting import (
    add_canvas,
    create_figure,
    make_gradient,
    save_png,
    seeded_rng,
)
from neo_legend.base import BaseLegendSkill, StyleDefinition


class DualRadarChartSkill(BaseLegendSkill):
    legend_type = "dual_radar_chart"
    display_name = "Dual Radar Comparison"
    default_style = "versus_battle"
    default_size = (1400, 900)
    style_definitions = (
        StyleDefinition(
            "versus_battle",
            "Dark arena-style dual radar with VS branding and performance arrows.",
        ),
        StyleDefinition(
            "mirror_compare",
            "Light textured dual radar with connecting lines and stats panel.",
        ),
        StyleDefinition(
            "evolution_track",
            "Dark blue evolution timeline radar with improvement highlights.",
        ),
    )

    def render(self, request: RenderRequest) -> RenderResult:
        style = self.resolve_style(request.style)
        width, height = self.output_size(request)
        data = self._parse_data(request.data)

        dispatch = {
            "versus_battle": self._render_versus_battle,
            "mirror_compare": self._render_mirror_compare,
            "evolution_track": self._render_evolution_track,
        }
        fig = dispatch[style](width, height, data, request.title, request.subtitle)
        return self.result(save_png(fig), style)

    @staticmethod
    def _parse_data(data: dict[str, Any]) -> dict[str, Any]:
        raw_left = data.get("left", {})
        raw_right = data.get("right", {})
        default_categories = ["PTS", "REB", "AST", "STL", "BLK"]
        left = {
            "label": raw_left.get("label", "Player A / 2024"),
            "categories": list(raw_left.get("categories", default_categories)),
            "values": list(raw_left.get("values", [28.0, 7.5, 8.2, 1.2, 0.9])),
        }
        right = {
            "label": raw_right.get("label", "Player B / 2025"),
            "categories": list(raw_right.get("categories", default_categories)),
            "values": list(raw_right.get("values", [32.0, 8.8, 9.5, 1.5, 1.2])),
        }
        return {"left": left, "right": right}

    def _render_versus_battle(
        self,
        width: int,
        height: int,
        data: dict[str, Any],
        title: str | None,
        subtitle: str | None,
    ) -> plt.Figure:
        bg = "#0d0d1a"
        fig = create_figure(width, height, bg)
        canvas = add_canvas(fig)

        title_text = (title or "DUAL RADAR COMPARISON").upper()
        canvas.text(0.5, 0.95, title_text, color="#ffffff", fontsize=36, fontweight="black", ha="center")
        sub_text = (subtitle or "HEAD-TO-HEAD PERFORMANCE ANALYSIS").upper()
        canvas.text(0.5, 0.905, sub_text, color="#888899", fontsize=14, fontweight="bold", ha="center")
        canvas.plot([0.08, 0.92], [0.885, 0.885], color="#ff4757", lw=2, alpha=0.6)

        for dx in np.arange(-4, 5) * 0.003:
            canvas.text(0.5 + dx, 0.52, "VS", color="#ff4757", fontsize=60, fontweight="black",
                        ha="center", va="center", alpha=0.12)
        canvas.text(0.5, 0.52, "VS", color="#ff4757", fontsize=60, fontweight="black",
                    ha="center", va="center")

        left_data = data["left"]
        right_data = data["right"]
        categories = left_data["categories"]
        lv = np.array(left_data["values"], dtype=float)
        rv = np.array(right_data["values"], dtype=float)
        diffs_pct = np.where(lv > 0, (rv - lv) / np.maximum(lv, 1e-9) * 100, 0)

        warm_colors = ["#ff6b6b", "#ff8e53", "#feca57", "#ff9ff3", "#ff6348"]
        cool_colors = ["#54a0ff", "#5f27cd", "#00d2d3", "#48dbfb", "#a29bfe"]

        ax_l = fig.add_axes([0.05, 0.12, 0.42, 0.75], polar=True, facecolor=bg)
        ax_r = fig.add_axes([0.53, 0.12, 0.42, 0.75], polar=True, facecolor=bg)

        self._draw_radar_core(ax_l, categories, lv, warm_colors, bg, title=left_data["label"])
        self._draw_radar_core(ax_r, categories, rv, cool_colors, bg, title=right_data["label"])

        max_diff_idx = int(np.argmax(np.abs(diffs_pct)))
        highlight_idx = -1
        for i, cat in enumerate(categories):
            if abs(diffs_pct[i]) > 10:
                highlight_idx = i
                break
        for ax in (ax_l, ax_r):
            labels = [(f"\u25CF {c}" if j == highlight_idx else c) for j, c in enumerate(categories)]
            ax.set_xticklabels(labels, color="#ccccdd", fontsize=10)
            if highlight_idx >= 0:
                for j, tick_label in enumerate(ax.get_xticklabels()):
                    if j == highlight_idx:
                        tick_label.set_color("#ffd32a")
                        tick_label.set_fontsize(13)
                        tick_label.set_fontweight("bold")

        l_avg = float(np.mean(lv))
        r_avg = float(np.mean(rv))
        l_total = float(np.sum(lv))
        r_total = float(np.sum(rv))

        arrow_l = "\u2191" if l_avg > r_avg else "\u2193"
        arrow_r = "\u2191" if r_avg > l_avg else "\u2193"
        arrow_color_l = "#2ed573" if l_avg >= r_avg else "#ff4757"
        arrow_color_r = "#2ed573" if r_avg >= l_avg else "#ff4757"

        canvas.text(0.26, 0.065, f"{arrow_l} AVG:{l_avg:.1f}  SUM:{l_total:.1f}",
                    color=arrow_color_l, fontsize=13, fontweight="bold", ha="center",
                    bbox={"boxstyle": "round,pad=0.4", "facecolor": "#1a1a2e", "edgecolor": arrow_color_l, "lw": 1.5})
        canvas.text(0.74, 0.065, f"{arrow_r} AVG:{r_avg:.1f}  SUM:{r_total:.1f}",
                    color=arrow_color_r, fontsize=13, fontweight="bold", ha="center",
                    bbox={"boxstyle": "round,pad=0.4", "facecolor": "#1a1a2e", "edgecolor": arrow_color_r, "lw": 1.5})

        diff_val = diffs_pct[max_diff_idx]
        diff_dir = "+" if diff_val > 0 else ""
        canvas.text(0.5, 0.03,
                    f"MAX DIFF: {categories[max_diff_idx]}  {diff_dir}{diff_val:.1f}%",
                    color="#ffd32a", fontsize=13, fontweight="bold", ha="center")

        return fig

    def _render_mirror_compare(
        self,
        width: int,
        height: int,
        data: dict[str, Any],
        title: str | None,
        subtitle: str | None,
    ) -> plt.Figure:
        bg = "#f5f3ee"
        fig = create_figure(width, height, bg)
        canvas = add_canvas(fig)

        title_text = (title or "MIRROR COMPARISON").upper()
        canvas.text(0.5, 0.95, title_text, color="#2d3436", fontsize=36, fontweight="black", ha="center")
        sub_text = (subtitle or "SYMMETRIC ANALYSIS DASHBOARD").upper()
        canvas.text(0.5, 0.905, sub_text, color="#636e72", fontsize=14, fontweight="bold", ha="center")
        canvas.plot([0.08, 0.92], [0.885, 0.885], color="#b2bec3", lw=1.5, alpha=0.6)

        left_data = data["left"]
        right_data = data["right"]
        categories = left_data["categories"]
        lv = np.array(left_data["values"], dtype=float)
        rv = np.array(right_data["values"], dtype=float)
        n = len(categories)

        left_colors = ["#ff6b6b", "#ee5a24", "#f9ca24", "#eb4d4b", "#e17055"]
        right_colors = ["#4ecdc4", "#6c5ce7", "#00cec9", "#81ecec", "#74b9ff"]

        ax_l = fig.add_axes([0.04, 0.15, 0.40, 0.68], polar=True, facecolor=bg)
        ax_r = fig.add_axes([0.56, 0.15, 0.40, 0.68], polar=True, facecolor=bg)

        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]
        lv_closed = list(lv) + [lv[0]]
        rv_closed = list(rv) + [rv[0]]

        self._draw_radar_light(ax_l, categories, lv, left_colors, bg, title=left_data["label"])
        self._draw_radar_light(ax_r, categories, rv, right_colors, bg, title=right_data["label"])

        ax_l_pos = ax_l.get_position()
        ax_r_pos = ax_r.get_position()
        center_ax = fig.add_axes([0.44, 0.30, 0.12, 0.38], facecolor="none")
        center_ax.set_axis_off()

        for i in range(n):
            a1 = angles[i]
            a2 = angles[i]
            r1 = lv[i] / max(lv.max(), 1e-9) * 0.95
            r2 = rv[i] / max(rv.max(), 1e-9) * 0.95
            x1 = r1 * np.cos(a1) * 0.42 + 0.26
            y1 = r1 * np.sin(a1) * 0.28 + 0.49
            x2 = (1 - r2 * np.cos(a2) * 0.42) - 0.26
            y2 = r2 * np.sin(a2) * 0.28 + 0.49
            diff_color = "#27ae60" if rv[i] >= lv[i] else "#e74c3c"
            canvas.plot([x1, x2], [y1, y2], color=diff_color, ls="--", lw=1.2, alpha=0.3)

        diffs = rv - lv
        max_diff_idx = int(np.argmax(np.abs(diffs)))
        l_avg = float(np.mean(lv))
        r_avg = float(np.mean(rv))

        panel_x, panel_y = 0.5, 0.48
        panel_w, panel_h = 0.18, 0.30
        box = FancyBboxPatch(
            (panel_x - panel_w / 2, panel_y - panel_h / 2),
            panel_w, panel_h,
            boxstyle="round,pad=0.02,rounding_size=0.01",
            facecolor="#ffffff", edgecolor="#dfe6e9", lw=1.5, alpha=0.92,
        )
        canvas.add_patch(box)

        canvas.text(panel_x, panel_y + 0.12, "DIFF SUMMARY", color="#2d3436",
                    fontsize=10, fontweight="black", ha="center")
        canvas.text(panel_x, panel_y + 0.07, "─" * 14, color="#b2bec3", fontsize=8, ha="center")
        canvas.text(panel_x, panel_y + 0.02, f"MAX GAP:", color="#636e72", fontsize=9, ha="center")
        canvas.text(panel_x, panel_y - 0.02, categories[max_diff_idx], color="#0984e3",
                    fontsize=12, fontweight="bold", ha="center")
        diff_val = diffs[max_diff_idx]
        diff_sign = "+" if diff_val > 0 else ""
        canvas.text(panel_x, panel_y - 0.065, f"{diff_sign}{diff_val:.1f}",
                    color="#e74c3c" if diff_val < 0 else "#27ae60",
                    fontsize=18, fontweight="black", ha="center")
        canvas.text(panel_x, panel_y - 0.105, "─" * 14, color="#b2bec3", fontsize=8, ha="center")
        canvas.text(panel_x, panel_y - 0.13, f"L-AVG: {l_avg:.1f}", color="#ff6b6b",
                    fontsize=10, fontweight="bold", ha="center")
        canvas.text(panel_x, panel_y - 0.155, f"R-AVG: {r_avg:.1f}", color="#4ecdc4",
                    fontsize=10, fontweight="bold", ha="center")
        winner = "RIGHT" if r_avg >= l_avg else "LEFT"
        win_color = "#4ecdc4" if r_avg >= l_avg else "#ff6b6b"
        canvas.text(panel_x, panel_y - 0.195, f"\u25B6 {winner}", color=win_color,
                    fontsize=11, fontweight="black", ha="center")

        return fig

    def _render_evolution_track(
        self,
        width: int,
        height: int,
        data: dict[str, Any],
        title: str | None,
        subtitle: str | None,
    ) -> plt.Figure:
        bg = "#0a192f"
        fig = create_figure(width, height, bg)
        canvas = add_canvas(fig)

        title_text = (title or "EVOLUTION TRACK").upper()
        canvas.text(0.5, 0.96, title_text, color="#ccd6f6", fontsize=36, fontweight="black", ha="center")
        sub_text = (subtitle or "PERFORMANCE PROGRESSION TIMELINE").upper()
        canvas.text(0.5, 0.92, sub_text, color="#64ffda", fontsize=13, fontweight="bold", ha="center", alpha=0.8)
        canvas.plot([0.08, 0.92], [0.90, 0.90], color="#64ffda", lw=1.5, alpha=0.35)

        early_data = data["left"]
        late_data = data["right"]
        categories = early_data["categories"]
        ev = np.array(early_data["values"], dtype=float)
        lv = np.array(late_data["values"], dtype=float)
        n = len(categories)
        changes = lv - ev

        e_colors = ["#233554", "#2a4365", "#2c5282", "#2b6cb0", "#3182ce"]
        l_colors = ["#00ff88", "#00e676", "#00cc66", "#00b359", "#00994d"]

        ax_e = fig.add_axes([0.08, 0.50, 0.58, 0.37], polar=True, facecolor=bg)
        ax_l = fig.add_axes([0.08, 0.07, 0.58, 0.37], polar=True, facecolor=bg)

        time_label_e = early_data["label"].split("/")[-1].strip() if "/" in early_data["label"] else "EARLY PHASE"
        time_label_l = late_data["label"].split("/")[-1].strip() if "/" in late_data["label"] else "LATE PHASE"

        self._draw_radar_dark(ax_e, categories, ev, e_colors, bg, title=f"\u25C0  {time_label_e}")
        self._draw_radar_dark(ax_l, categories, lv, l_colors, bg, title=f"\u25B6  {time_label_l}")

        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        for i in range(n):
            if changes[i] > 0:
                theta_range = np.linspace(angles[i], angles[(i + 1) % n], 20)
                r_vals_e = np.linspace(ev[i] / max(ev.max(), 1e-9), ev[(i + 1) % n] / max(ev.max(), 1e-9), 20)
                r_vals_l = np.linspace(lv[i] / max(lv.max(), 1e-9), lv[(i + 1) % n] / max(lv.max(), 1e-9), 20)
                verts_e = list(zip(theta_range, r_vals_e))
                verts_l = list(zip(theta_range, r_vals_l))
                poly_e = Polygon(verts_e, closed=False, transform=ax_l.transData + ax_l.transAxes.inverted(),
                                 facecolor="#00ff88", alpha=0.15, edgecolor="none", zorder=1)
                ax_l.add_patch(poly_e)
            elif changes[i] < 0:
                theta_range = np.linspace(angles[i], angles[(i + 1) % n], 20)
                r_vals_l = np.linspace(lv[i] / max(lv.max(), 1e-9), lv[(i + 1) % n] / max(lv.max(), 1e-9), 20)
                verts_l = list(zip(theta_range, r_vals_l))
                poly_l = Polygon(verts_l, closed=False, transform=ax_l.transData + ax_l.transAxes.inverted(),
                                 facecolor="#ff4444", alpha=0.15, edgecolor="none", zorder=1)
                ax_l.add_patch(poly_l)

        mid_x = 0.78
        canvas.annotate("", xy=(mid_x, 0.51), xytext=(mid_x, 0.43),
                        arrowprops=dict(arrowstyle="-|>", color="#64ffda", lw=3, mutation_scale=20))
        canvas.text(mid_x, 0.47, "EVOLVE", color="#64ffda", fontsize=12, fontweight="bold",
                    ha="center", va="center", rotation=90)

        e_avg = float(np.mean(ev))
        l_avg = float(np.mean(lv))
        delta = l_avg - e_avg
        delta_sign = "+" if delta > 0 else ""
        delta_color = "#00ff88" if delta >= 0 else "#ff4444"

        stat_box_x = 0.72
        canvas.text(stat_box_x, 0.85, "PROGRESSION STATS", color="#ccd6f6", fontsize=13,
                    fontweight="bold", ha="center")
        canvas.text(stat_box_x, 0.80, "\u2500" * 16, color="#64ffda", fontsize=8, ha="center", alpha=0.4)
        canvas.text(stat_box_x, 0.74, f"EARLY  AVG: {e_avg:.1f}", color="#8892b0", fontsize=12,
                    fontweight="bold", ha="center")
        canvas.text(stat_box_x, 0.68, f"LATE   AVG: {l_avg:.1f}", color="#ccd6f6", fontsize=12,
                    fontweight="bold", ha="center")
        canvas.text(stat_box_x, 0.61, "\u2500" * 16, color="#64ffda", fontsize=8, ha="center", alpha=0.4)
        canvas.text(stat_box_x, 0.54, f"{delta_sign}{delta:.1f}", color=delta_color, fontsize=32,
                    fontweight="black", ha="center")
        label_text = "IMPROVEMENT" if delta >= 0 else "DECLINE"
        canvas.text(stat_box_x, 0.47, label_text, color=delta_color, fontsize=11,
                    fontweight="bold", ha="center", alpha=0.85)

        improved = sum(1 for c in changes if c > 0)
        declined = sum(1 for c in changes if c < 0)
        canvas.text(stat_box_x, 0.37, f"\u2191 {improved} UP  \u2193 {declined} DOWN",
                    color="#64ffda", fontsize=11, fontweight="bold", ha="center", alpha=0.7)

        improved_cats = [categories[i] for i in range(n) if changes[i] > 0]
        declined_cats = [categories[i] for i in range(n) if changes[i] < 0]
        if improved_cats:
            canvas.text(stat_box_x, 0.29, "UP: " + ", ".join(improved_cats),
                        color="#00ff88", fontsize=9, ha="center", alpha=0.8)
        if declined_cats:
            canvas.text(stat_box_x, 0.23, "DOWN: " + ", ".join(declined_cats),
                        color="#ff4444", fontsize=9, ha="center", alpha=0.8)

        return fig

    @staticmethod
    def _draw_radar_core(
        ax: plt.Axes,
        categories: list[str],
        values: np.ndarray,
        colors: list[str],
        bg: str,
        title: str = "",
    ) -> None:
        n = len(categories)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        vals = np.array(values, dtype=float)
        vmax = max(vals.max() * 1.15, 1e-9)
        vals_norm = vals / vmax
        vals_closed = list(vals_norm) + [vals_norm[0]]

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), categories, color="#aaaacc", fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["", "", "", ""], color="#555566", fontsize=7)
        ax.grid(color="#333344", lw=0.8, alpha=0.5)
        ax.spines["polar"].set_color("#333344")
        ax.spines["polar"].set_linewidth(1.0)
        ax.set_facecolor(bg)

        cmap = make_gradient(colors, "radar_cmap")
        fill_alphas = np.linspace(0.45, 0.15, n)
        for i in range(n):
            seg_angles = [angles[i], angles[(i + 1) % n], angles[(i + 1) % n], angles[i]]
            seg_radii = [vals_norm[i], vals_norm[(i + 1) % n], 0, 0]
            ax.fill(seg_angles, seg_radii, color=cmap(float(i) / max(n - 1, 1)), alpha=fill_alphas[i], zorder=2)

        ax.plot(angles, vals_closed, color=colors[0], lw=2.8, solid_capstyle="round", zorder=4)
        ax.scatter(angles[:-1], vals_norm, color=colors[:n], s=55, zorder=5, edgecolors="#ffffff", linewidths=1.2)

        if title:
            ax.set_title(title.upper(), color="#ffffff", fontsize=14, fontweight="bold",
                         pad=16, va="bottom")

        total_score = float(np.sum(vals))
        score_text = f"SCORE: {total_score:.1f}"
        ax.text(0.5, -0.12, score_text, transform=ax.transAxes, ha="center",
                color="#ffd32a", fontsize=12, fontweight="bold")

    @staticmethod
    def _draw_radar_light(
        ax: plt.Axes,
        categories: list[str],
        values: np.ndarray,
        colors: list[str],
        bg: str,
        title: str = "",
    ) -> None:
        n = len(categories)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        vals = np.array(values, dtype=float)
        vmax = max(vals.max() * 1.15, 1e-9)
        vals_norm = vals / vmax
        vals_closed = list(vals_norm) + [vals_norm[0]]

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), categories, color="#636e72", fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["25%", "50%", "75%", "100%"], color="#b2bec3", fontsize=8)
        ax.grid(color="#dfe6e9", lw=1.0, alpha=0.65)
        ax.spines["polar"].set_color("#b2bec3")
        ax.spines["polar"].set_linewidth(1.2)
        ax.set_facecolor(bg)

        cmap = make_gradient(colors, "light_radar_cmap")
        ax.fill(angles, vals_closed, color=cmap(0.4), alpha=0.22, zorder=2)
        ax.plot(angles, vals_closed, color=colors[0], lw=3.0, solid_capstyle="round", zorder=4)
        ax.scatter(angles[:-1], vals_norm, color=colors[:n], s=60, zorder=5,
                   edgecolors="#ffffff", linewidths=1.5)

        if title:
            ax.set_title(title.upper(), color="#2d3436", fontsize=14, fontweight="bold",
                         pad=16, va="bottom")

    @staticmethod
    def _draw_radar_dark(
        ax: plt.Axes,
        categories: list[str],
        values: np.ndarray,
        colors: list[str],
        bg: str,
        title: str = "",
    ) -> None:
        n = len(categories)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]

        vals = np.array(values, dtype=float)
        vmax = max(vals.max() * 1.15, 1e-9)
        vals_norm = vals / vmax
        vals_closed = list(vals_norm) + [vals_norm[0]]

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), categories, color="#8892b0", fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["", "", "", ""], color="#233554", fontsize=7)
        ax.grid(color="#1d3461", lw=0.8, alpha=0.5)
        ax.spines["polar"].set_color("#1d3461")
        ax.spines["polar"].set_linewidth(1.0)
        ax.set_facecolor(bg)

        cmap = make_gradient(colors, "dark_radar_cmap")
        ax.fill(angles, vals_closed, color=cmap(0.5), alpha=0.2, zorder=2)
        ax.plot(angles, vals_closed, color=colors[0], lw=2.8, solid_capstyle="round", zorder=4)
        ax.scatter(angles[:-1], vals_norm, color=colors[:n], s=55, zorder=5,
                   edgecolors="#ccd6f6", linewidths=1.2)

        if title:
            ax.set_title(title.upper(), color="#ccd6f6", fontsize=14, fontweight="bold",
                         pad=14, va="bottom")

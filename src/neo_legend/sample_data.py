"""Synthetic data builders for every built-in legend type."""

from __future__ import annotations

from typing import Any

from neo_legend.models import RenderRequest
from neo_legend.base import BaseLegendSkill


def build_sample_request(skill: BaseLegendSkill, style: str) -> RenderRequest:
    """Create a deterministic render request for a legend skill/style pair."""

    width, height = skill.default_size
    return RenderRequest(
        legend_type=skill.legend_type,
        style=style,
        title=_sample_title(skill.legend_type, style),
        subtitle=_sample_subtitle(skill.legend_type, style),
        data=sample_data_for(skill.legend_type, style),
        width=width,
        height=height,
    )


def sample_data_for(legend_type: str, style: str) -> dict[str, Any]:
    """Return deterministic sample data that exercises the renderer."""

    normalized = legend_type.strip().lower().replace("-", "_")
    if normalized == "coordinate":
        return {"points": _coordinate_points(style)}
    if normalized == "plus_minus_coordinate":
        return {"points": _quadrant_points()}
    if normalized == "rose":
        return {
            "current_values": [14, 14, 14, 11.5, 11.5, 9, 6.8, 6.7, 4.5, 3, 2, 1.5, 1, 0.5],
            "proposed_values": [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
        }
    if normalized == "table":
        return {"rows": _table_rows()}
    if normalized == "dual_court_shot":
        return {
            "panels": [
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
        }
    if normalized == "court_shot_animation":
        frame_count = 14 if style == "arena_arc" else 10
        return {"shot_count": 430, "seed": 31, "frame_count": frame_count}
    if normalized == "court_shot":
        if style == "points_location":
            return {
                "seed": 2021,
                "max_points": 800,
                "scoring_zones": [
                    {
                        "name": "rim",
                        "center": [0, 58],
                        "spread": [36, 28],
                        "count": 900,
                        "points_per_event": 8.8,
                    },
                    {
                        "name": "paint",
                        "center": [0, 142],
                        "spread": [24, 56],
                        "count": 430,
                        "points_per_event": 6.2,
                    },
                    {
                        "name": "above_break_three",
                        "shape": "arc",
                        "angle_range": [25, 155],
                        "radius": 235,
                        "radius_sd": 12,
                        "count": 760,
                        "points_per_event": 3.7,
                    },
                    {
                        "name": "left_corner",
                        "center": [-222, 96],
                        "spread": [8, 42],
                        "count": 170,
                        "points_per_event": 3.2,
                    },
                    {
                        "name": "right_corner",
                        "center": [222, 96],
                        "spread": [8, 42],
                        "count": 170,
                        "points_per_event": 3.2,
                    },
                    {
                        "name": "short_midrange",
                        "center": [0, 215],
                        "spread": [52, 28],
                        "count": 130,
                        "points_per_event": 2.4,
                    },
                ],
            }
        return {"shot_count": 620, "seed": 11}
    return {}


def summarize_sample_data(data: dict[str, Any]) -> dict[str, Any]:
    """Create a compact log-friendly summary of sample data."""

    summary: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, list):
            summary[key] = {"type": "list", "count": len(value)}
        elif isinstance(value, dict):
            summary[key] = {"type": "dict", "keys": sorted(value)}
        else:
            summary[key] = value
    return summary


def _sample_title(legend_type: str, style: str) -> str:
    style_titles = {
        ("court_shot_animation", "arena_arc"): "CAITLIN CLARK",
        ("court_shot", "points_location"): "Total Points By Location",
        ("court_shot", "kobe_shots"): "Kobe Bryant",
    }
    if (legend_type, style) in style_titles:
        return style_titles[(legend_type, style)]

    titles = {
        "court_shot": "Scottie Pippen",
        "dual_court_shot": "Jaden McDaniels",
        "court_shot_animation": "Shooting Terrain",
        "coordinate": "NBA Scorers",
        "plus_minus_coordinate": "The Efficiency Landscape",
        "rose": "Lottery Reform",
        "table": "Leaders In Points Created",
    }
    if style != "default":
        return titles.get(legend_type, legend_type).title()
    return titles.get(legend_type, legend_type)


def _sample_subtitle(legend_type: str, style: str) -> str:
    style_subtitles = {
        ("court_shot_animation", "arena_arc"): "MOST POINTS IN NCAA WOMEN'S BASKETBALL HISTORY",
        ("court_shot", "points_location"): "2020-21 Season | By @KirkGoldsberry",
        ("court_shot", "kobe_shots"): "January 22, 2006 | 81 Points Scored | 5 Points Assisted",
    }
    if (legend_type, style) in style_subtitles:
        return style_subtitles[(legend_type, style)]

    subtitles = {
        "court_shot": "1997-98 Shooting Terrain",
        "dual_court_shot": "Minnesota Timberwolves / Year Over Year",
        "court_shot_animation": "Animated Zone Map",
        "coordinate": "Volume And Efficiency | Simulated Sample",
        "plus_minus_coordinate": "Round 1 Only | Simulated Sample",
        "rose": 'Current System Versus "Proposal 1"',
        "table": "Playoffs",
    }
    return subtitles.get(legend_type, "Simulated Sample")


def _coordinate_points(style: str) -> list[dict[str, Any]]:
    names = [
        ("Nikola\nJokic", 20.9, 65.6, 200),
        ("Markkanen", 23.5, 59.8, 640),
        ("Luka\nDoncic", 30.4, 56.3, 1900),
        ("Giannis", 29.7, 55.2, 1700),
        ("LeBron", 29.6, 54.6, 1600),
        ("Tatum", 27.7, 53.3, 1450),
        ("SGA", 26.8, 52.9, 1550),
        ("Trae\nYoung", 26.1, 47.8, 1350),
        ("Ja\nMorant", 30.2, 49.8, 1500),
        ("Kyrie\nIrving", 27.0, 56.8, 1300),
        ("Mitchell", 28.4, 56.4, 1200),
        ("Bam", 22.2, 53.8, 260),
        ("Mikal\nBridges", 19.3, 53.8, 140),
        ("Banchero", 22.5, 46.2, 320),
        ("Brunson", 24.5, 52.1, 620),
        ("Fox", 25.4, 55.6, 980),
        ("Embiid", 29.2, 55.8, 1600),
        ("Klay", 25.9, 54.8, 920),
    ]
    size_multiplier = 1.12 if style == "gold_scorers" else 1.0
    return [
        {"label": name, "x": x, "y": y, "size": size * size_multiplier}
        for name, x, y, size in names
    ]


def _quadrant_points() -> list[dict[str, Any]]:
    return [
        {"label": "ORL", "x": -6.3, "y": 7.1, "color": "#284c8f", "note": "TWINNING"},
        {"label": "DET", "x": -5.2, "y": 7.0, "color": "#c0323c", "note": "TWINNING"},
        {"label": "LAL", "x": -3.4, "y": 2.7, "color": "#552583", "note": ""},
        {"label": "HOU", "x": -1.7, "y": 4.8, "color": "#c8102e", "note": ""},
        {"label": "MIN", "x": 1.6, "y": 3.8, "color": "#236192", "note": ""},
        {"label": "BOS", "x": 3.1, "y": 2.0, "color": "#008348", "note": ""},
        {"label": "OKC", "x": 11.2, "y": 3.8, "color": "#007ac1", "note": "#2 Net"},
        {"label": "NYK", "x": 8.6, "y": 7.3, "color": "#f58426", "note": "#1 Net"},
        {"label": "DEN", "x": -2.7, "y": -1.8, "color": "#4d4d4d", "note": "#11 Offense"},
        {"label": "POR", "x": -8.6, "y": -5.7, "color": "#e03a3e", "note": ""},
        {"label": "ATL", "x": -4.2, "y": -10.3, "color": "#c1d32f", "note": ""},
        {"label": "PHI", "x": -0.8, "y": -3.7, "color": "#006bb6", "note": ""},
        {"label": "CLE", "x": 2.4, "y": -2.7, "color": "#6f263d", "note": "TWINNING"},
    ]


def _table_rows() -> list[dict[str, Any]]:
    return [
        _table_row("OKC", "#007ac1", "SGA", 55.3, 68, 3.6, 35.7),
        _table_row("DET", "#c8102e", "Cunningham", 51.1, 60, 1.2, 40.4),
        _table_row("DEN", "#0e2240", "Jokic", 50.0, 55, 2.5, 39.5),
        _table_row("TOR", "#ce1141", "Barnes", 44.4, 61, 2.5, 39.0),
        _table_row("LAL", "#552583", "James", 43.4, 53, 1.9, 38.7),
        _table_row("ORL", "#0077c0", "Banchero", 42.7, 52, 1.8, 39.0),
        _table_row("NYK", "#f58426", "Brunson", 41.6, 60, 2.5, 34.3),
        _table_row("BOS", "#008348", "Tatum", 41.3, 61, 2.4, 36.3),
        _table_row("PHI", "#006bb6", "Maxey", 40.6, 58, 3.7, 39.1),
        _table_row("PHI", "#ed174c", "Embiid", 40.2, 53, 3.2, 34.2),
        _table_row("DEN", "#fec524", "Murray", 38.4, 48, 2.6, 39.7),
        _table_row("LAC", "#1d428a", "Harden", 37.2, 62, 1.2, 37.0),
        _table_row("SAC", "#5a2d81", "Fox", 36.5, 55, 2.5, 35.0),
        _table_row("BOS", "#008348", "Brown", 35.6, 55, 0.9, 35.6),
        _table_row("SAS", "#000000", "Castle", 34.9, 58, 1.9, 32.0),
    ]


def _table_row(
    team: str,
    team_color: str,
    name: str,
    pts_created: float,
    ts: float,
    ast_tov: float,
    mpg: float,
) -> dict[str, Any]:
    return {
        "team": team,
        "team_color": team_color,
        "name": name,
        "pts_created": pts_created,
        "ts": ts,
        "ast_tov": ast_tov,
        "mpg": mpg,
    }

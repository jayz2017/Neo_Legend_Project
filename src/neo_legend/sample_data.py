from __future__ import annotations

"""Synthetic data builders for every built-in legend type."""


from typing import Any

from neo_legend.base import BaseLegendSkill
from neo_legend.models import RenderRequest


def build_sample_request(skill: BaseLegendSkill, style: str) -> RenderRequest:
    """Create a deterministic render request for a legend skill/style pair."""

    width, height = _sample_size(skill, style)
    data = sample_data_for(skill.legend_type, style)
    data.setdefault("luxury_theme", "random")
    return RenderRequest(
        legend_type=skill.legend_type,
        style=style,
        title=_sample_title(skill.legend_type, style),
        subtitle=_sample_subtitle(skill.legend_type, style),
        data=data,
        width=width,
        height=height,
    )


def _sample_size(skill: BaseLegendSkill, style: str) -> tuple[int, int]:
    if skill.legend_type == "table" and style == "league_standings_gradient":
        return 1245, 680
    return skill.default_size


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
        if style == "league_standings_gradient":
            return _league_standings_table_data()
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
    if normalized == "line_chart":
        return {
            "categories": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"],
            "series": [
                {"label": "Revenue", "values": [42, 51, 48, 64, 72, 84]},
                {"label": "Margin", "values": [31, 36, 39, 45, 49, 57]},
            ],
            "benchmark": 50,
            "x_label": "Quarter",
            "y_label": "Index",
        }
    if normalized == "calendar_chart":
        return {
            "month_label": "May 2026",
            "start_weekday": 4,
            "days": 31,
            "events": [
                {"day": 2, "type": "RATE", "impact": 0.80},
                {"day": 3, "type": "M&A", "impact": 0.88},
                {"day": 4, "type": "IPO", "impact": 0.70},
                {"day": 7, "type": "EPS", "impact": 0.62},
                {"day": 9, "type": "RATE", "impact": 0.74},
                {"day": 12, "type": "EPS", "impact": 0.88},
                {"day": 15, "type": "M&A", "impact": 0.70},
                {"day": 18, "type": "EPS", "impact": 0.95},
                {"day": 23, "type": "IPO", "impact": 0.65},
                {"day": 25, "type": "M&A", "impact": 0.92},
                {"day": 31, "type": "EPS", "impact": 0.85},
            ],
        }
    if normalized == "matrix_bubble_chart":
        return {}
    if normalized == "chord_chart":
        return {}
    if normalized == "scatter_matrix_chart":
        return {}
    if normalized == "stacked_bar_chart":
        return {}
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
        ("table", "league_standings_gradient"): "League Standings",
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
        "radar_chart": "Player Radar Profile",
        "dual_radar_chart": "Dual Radar Comparison",
        "bar_chart": "Performance Analytics",
        "line_chart": "Trend Performance",
        "combo_chart": "Performance Overview",
        "bubble_chart": "Bubble Distribution",
        "sankey_chart": "Flow Analysis",
        "calendar_chart": "Catalyst Calendar",
        "matrix_bubble_chart": "Cross-Asset Correlation Matrix",
        "chord_chart": "Capital Flow Chord",
        "scatter_matrix_chart": "Macro Pair Matrix",
        "stacked_bar_chart": "Segment Contribution",
    }
    if style != "default":
        return titles.get(legend_type, legend_type).title()
    return titles.get(legend_type, legend_type)


def _sample_subtitle(legend_type: str, style: str) -> str:
    style_subtitles = {
        ("court_shot_animation", "arena_arc"): "MOST POINTS IN NCAA WOMEN'S BASKETBALL HISTORY",
        ("court_shot", "points_location"): "2020-21 Season | By @KirkGoldsberry",
        ("court_shot", "kobe_shots"): "January 22, 2006 | 81 Points Scored | 5 Points Assisted",
        ("table", "league_standings_gradient"): "Average-centered gradient columns",
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
        "radar_chart": "Multidimensional Analysis",
        "dual_radar_chart": "Head-to-head performance analysis",
        "bar_chart": "Ranked value comparison with benchmark context",
        "line_chart": "Time-series movement with benchmark context",
        "combo_chart": "Primary volume with secondary trend signal",
        "bubble_chart": "Position, scale and category intensity in one view",
        "sankey_chart": "Weighted transition paths with node totals",
        "calendar_chart": "Catalyst calendar for commercial reporting",
        "matrix_bubble_chart": "Bubble size encodes magnitude, color encodes direction",
        "chord_chart": "Inter-segment allocation intensity and direction",
        "scatter_matrix_chart": "Small multiples for cross-metric inspection",
        "stacked_bar_chart": "Stacked category composition with total ranking",
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


def _league_standings_table_data() -> dict[str, Any]:
    return {
        "color_theme": "random",
        "header_height": 0.11,
        "columns": [
            {"key": "rank", "label": "排名", "width": 0.055, "format": "int"},
            {"key": "team", "label": "球队", "width": 0.140, "align": "center", "bold": True},
            {"key": "wins", "label": "胜场", "width": 0.045, "format": "int", "average_format": ".1f"},
            {"key": "losses", "label": "负场", "width": 0.045, "format": "int", "average_format": ".1f"},
            {"key": "net_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "net_rating", "label": "", "width": 0.055, "format": ".1f"},
            {"key": "off_rating_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "off_rating", "label": "", "width": 0.055, "format": ".1f"},
            {"key": "efg_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "efg", "label": "", "width": 0.060, "format": "{value:.1f}%"},
            {"key": "turnover_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "turnover_rate", "label": "", "width": 0.055, "format": "{value:.1f}%"},
            {"key": "orb_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "orb_rate", "label": "", "width": 0.060, "format": "{value:.1f}%"},
            {"key": "ft_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "ft_rate", "label": "", "width": 0.055, "format": "{value:.1f}%"},
            {"key": "def_rating_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "def_rating", "label": "", "width": 0.055, "format": ".1f"},
            {"key": "opp_efg_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "opp_efg", "label": "", "width": 0.060, "format": "{value:.1f}%"},
            {"key": "def_turnover_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "def_turnover_rate", "label": "", "width": 0.055, "format": "{value:.1f}%"},
            {"key": "opp_orb_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "opp_orb_rate", "label": "", "width": 0.060, "format": "{value:.1f}%"},
            {"key": "foul_rank", "label": "", "width": 0.040, "format": "int"},
            {"key": "foul_rate", "label": "", "width": 0.055, "format": "{value:.1f}%"},
        ],
        "header_groups": [
            {"label": "百回合净胜分", "columns": ["net_rank", "net_rating"], "show_children": False},
            {
                "label": "进攻",
                "columns": [
                    "off_rating_rank",
                    "off_rating",
                    "efg_rank",
                    "efg",
                    "turnover_rank",
                    "turnover_rate",
                    "orb_rank",
                    "orb_rate",
                    "ft_rank",
                    "ft_rate",
                ],
                "children": [
                    {"label": "百回合得分", "columns": ["off_rating_rank", "off_rating"]},
                    {"label": "有效命中率", "columns": ["efg_rank", "efg"]},
                    {"label": "失误率", "columns": ["turnover_rank", "turnover_rate"]},
                    {"label": "进攻篮板率", "columns": ["orb_rank", "orb_rate"]},
                    {"label": "罚球率", "columns": ["ft_rank", "ft_rate"]},
                ],
            },
            {
                "label": "防守",
                "columns": [
                    "def_rating_rank",
                    "def_rating",
                    "opp_efg_rank",
                    "opp_efg",
                    "def_turnover_rank",
                    "def_turnover_rate",
                    "opp_orb_rank",
                    "opp_orb_rate",
                    "foul_rank",
                    "foul_rate",
                ],
                "children": [
                    {"label": "百回合失分", "columns": ["def_rating_rank", "def_rating"]},
                    {"label": "有效命中率", "columns": ["opp_efg_rank", "opp_efg"]},
                    {"label": "失误率", "columns": ["def_turnover_rank", "def_turnover_rate"]},
                    {"label": "进攻篮板率", "columns": ["opp_orb_rank", "opp_orb_rate"]},
                    {"label": "罚球率", "columns": ["foul_rank", "foul_rate"]},
                ],
            },
        ],
        "average_row": {
            "team": "联盟平均",
            "wins": 21.0,
            "losses": 21.0,
            "net_rating": 0.0,
            "off_rating": 116.2,
            "efg": 53.7,
            "turnover_rate": 16.1,
            "orb_rate": 31.0,
            "ft_rate": 25.2,
            "def_rating": 116.2,
            "opp_efg": 53.7,
            "def_turnover_rate": 16.1,
            "opp_orb_rate": 31.0,
            "foul_rate": 25.2,
        },
        "gradient_columns": {
            "net_rank": {"midpoint": "mean", "higher_is_better": False},
            "off_rating_rank": {"midpoint": "mean", "higher_is_better": False},
            "efg_rank": {"midpoint": "mean", "higher_is_better": False},
            "turnover_rank": {"midpoint": "mean", "higher_is_better": False},
            "orb_rank": {"midpoint": "mean", "higher_is_better": False},
            "ft_rank": {"midpoint": "mean", "higher_is_better": False},
            "def_rating_rank": {"midpoint": "mean", "higher_is_better": False},
            "opp_efg_rank": {"midpoint": "mean", "higher_is_better": False},
            "def_turnover_rank": {"midpoint": "mean", "higher_is_better": False},
            "opp_orb_rank": {"midpoint": "mean", "higher_is_better": False},
            "foul_rank": {"midpoint": "mean", "higher_is_better": False},
        },
        "rows": [
            _league_standing_row(1, "上海久事", 38, 4, net_rank=1, net_rating=21.0, off_rating_rank=1, off_rating=126.4, efg_rank=1, efg=60.1, turnover_rank=10, turnover_rate=15.9, orb_rank=4, orb_rate=34.5, ft_rank=17, ft_rate=22.9, def_rating_rank=1, def_rating=105.4, opp_efg_rank=1, opp_efg=49.1, def_turnover_rank=13, def_turnover_rate=15.8, opp_orb_rank=1, opp_orb_rate=26.1, foul_rank=4, foul_rate=20.7),
            _league_standing_row(2, "浙江浙商证券", 33, 9, net_rank=2, net_rating=12.3, off_rating_rank=5, off_rating=120.1, efg_rank=9, efg=53.7, turnover_rank=6, turnover_rate=15.3, orb_rank=6, orb_rate=33.8, ft_rank=6, ft_rate=27.5, def_rating_rank=2, def_rating=107.9, opp_efg_rank=4, opp_efg=50.8, def_turnover_rank=3, def_turnover_rate=18.0, opp_orb_rank=9, opp_orb_rate=30.1, foul_rank=5, foul_rate=20.8),
            _league_standing_row(3, "北京北汽", 29, 13, net_rank=3, net_rating=11.0, off_rating_rank=2, off_rating=122.8, efg_rank=3, efg=56.3, turnover_rank=2, turnover_rate=14.8, orb_rank=5, orb_rate=33.9, ft_rank=16, ft_rate=23.0, def_rating_rank=5, def_rating=111.8, opp_efg_rank=6, opp_efg=51.8, def_turnover_rank=16, def_turnover_rate=14.6, opp_orb_rank=2, opp_orb_rate=28.2, foul_rank=2, foul_rate=19.8),
            _league_standing_row(4, "浙江稠州金租", 27, 15, net_rank=4, net_rating=8.2, off_rating_rank=7, off_rating=118.6, efg_rank=7, efg=53.8, turnover_rank=17, turnover_rate=17.7, orb_rank=3, orb_rate=35.6, ft_rank=13, ft_rate=24.4, def_rating_rank=3, def_rating=110.5, opp_efg_rank=7, opp_efg=52.2, def_turnover_rank=2, def_turnover_rate=18.0, opp_orb_rank=4, opp_orb_rate=29.2, foul_rank=14, foul_rate=27.4),
            _league_standing_row(5, "广东东阳光", 27, 15, net_rank=5, net_rating=6.5, off_rating_rank=6, off_rating=119.0, efg_rank=10, efg=53.7, turnover_rank=5, turnover_rate=15.1, orb_rank=8, orb_rate=33.1, ft_rank=14, ft_rate=24.4, def_rating_rank=6, def_rating=112.5, opp_efg_rank=8, opp_efg=52.4, def_turnover_rank=4, def_turnover_rate=17.9, opp_orb_rank=13, opp_orb_rate=31.8, foul_rank=15, foul_rate=27.6),
            _league_standing_row(6, "深圳马可波罗", 30, 12, net_rank=6, net_rating=6.3, off_rating_rank=3, off_rating=121.8, efg_rank=4, efg=56.1, turnover_rank=1, turnover_rate=13.6, orb_rank=14, orb_rate=29.7, ft_rank=15, ft_rate=23.0, def_rating_rank=12, def_rating=115.5, opp_efg_rank=14, opp_efg=54.5, def_turnover_rank=6, def_turnover_rate=17.2, opp_orb_rank=10, opp_orb_rate=30.7, foul_rank=8, foul_rate=24.9),
            _league_standing_row(7, "青岛崂山啤酒", 25, 17, net_rank=7, net_rating=4.4, off_rating_rank=13, off_rating=115.5, efg_rank=12, efg=53.5, turnover_rank=7, turnover_rate=15.5, orb_rank=17, orb_rate=28.0, ft_rank=8, ft_rate=26.2, def_rating_rank=4, def_rating=111.2, opp_efg_rank=2, opp_efg=50.4, def_turnover_rank=12, def_turnover_rate=15.9, opp_orb_rank=11, opp_orb_rate=31.5, foul_rank=9, foul_rate=25.0),
            _league_standing_row(8, "山东高速", 24, 18, net_rank=8, net_rating=4.0, off_rating_rank=8, off_rating=118.3, efg_rank=19, efg=51.4, turnover_rank=11, turnover_rate=16.1, orb_rank=1, orb_rate=36.2, ft_rank=2, ft_rate=28.7, def_rating_rank=9, def_rating=114.4, opp_efg_rank=12, opp_efg=54.1, def_turnover_rank=1, def_turnover_rate=18.7, opp_orb_rank=6, opp_orb_rate=29.7, foul_rank=20, foul_rate=32.0),
            _league_standing_row(9, "山西汾酒", 22, 20, net_rank=9, net_rating=3.1, off_rating_rank=9, off_rating=117.9, efg_rank=6, efg=54.2, turnover_rank=8, turnover_rate=15.6, orb_rank=10, orb_rate=31.8, ft_rank=3, ft_rate=28.2, def_rating_rank=11, def_rating=114.9, opp_efg_rank=11, opp_efg=53.9, def_turnover_rank=5, def_turnover_rate=17.5, opp_orb_rank=12, opp_orb_rate=31.7, foul_rank=12, foul_rate=27.2),
            _league_standing_row(10, "辽宁本钢", 23, 19, net_rank=10, net_rating=2.3, off_rating_rank=11, off_rating=116.0, efg_rank=15, efg=53.0, turnover_rank=14, turnover_rate=17.2, orb_rank=2, orb_rate=36.1, ft_rank=19, ft_rate=20.9, def_rating_rank=8, def_rating=113.7, opp_efg_rank=10, opp_efg=53.3, def_turnover_rank=9, def_turnover_rate=16.9, opp_orb_rank=3, opp_orb_rate=28.9, foul_rank=13, foul_rate=27.2),
            _league_standing_row(11, "宁波町渥", 21, 21, net_rank=11, net_rating=2.0, off_rating_rank=15, off_rating=114.8, efg_rank=11, efg=53.5, turnover_rank=19, turnover_rate=17.8, orb_rank=7, orb_rate=33.2, ft_rank=1, ft_rate=28.7, def_rating_rank=7, def_rating=112.8, opp_efg_rank=3, opp_efg=50.7, def_turnover_rank=8, def_turnover_rate=16.9, opp_orb_rank=14, opp_orb_rate=32.1, foul_rank=19, foul_rate=30.3),
            _league_standing_row(12, "广州朗肽海本", 18, 24, net_rank=12, net_rating=-1.2, off_rating_rank=14, off_rating=115.4, efg_rank=13, efg=53.1, turnover_rank=15, turnover_rate=17.3, orb_rank=9, orb_rate=32.4, ft_rank=9, ft_rate=25.7, def_rating_rank=13, def_rating=116.5, opp_efg_rank=5, opp_efg=51.7, def_turnover_rank=20, def_turnover_rate=13.5, opp_orb_rank=16, opp_orb_rate=32.7, foul_rank=3, foul_rate=20.2),
            _league_standing_row(13, "新疆伊力特", 14, 28, net_rank=13, net_rating=-1.9, off_rating_rank=17, off_rating=112.9, efg_rank=5, efg=54.6, turnover_rank=20, turnover_rate=18.0, orb_rank=11, orb_rate=31.5, ft_rank=20, ft_rate=20.2, def_rating_rank=10, def_rating=114.8, opp_efg_rank=9, opp_efg=53.3, def_turnover_rank=10, def_turnover_rate=16.4, opp_orb_rank=8, opp_orb_rate=30.0, foul_rank=10, foul_rate=25.7),
            _league_standing_row(14, "福建晋江文旅", 17, 25, net_rank=14, net_rating=-3.0, off_rating_rank=10, off_rating=116.3, efg_rank=14, efg=53.0, turnover_rank=3, turnover_rate=14.8, orb_rank=15, orb_rate=28.7, ft_rank=5, ft_rate=27.7, def_rating_rank=15, def_rating=119.3, opp_efg_rank=13, opp_efg=54.5, def_turnover_rank=7, def_turnover_rate=17.1, opp_orb_rank=19, opp_orb_rate=34.4, foul_rank=17, foul_rate=28.7),
        ],
    }


def _league_standing_row(
    rank: int,
    team: str,
    wins: int,
    losses: int,
    **metrics: Any,
) -> dict[str, Any]:
    row = {
        "rank": rank,
        "team": team,
        "wins": wins,
        "losses": losses,
    }
    row.update(metrics)
    return row

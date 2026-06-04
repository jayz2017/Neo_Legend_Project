from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image, ImageColor

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry
from neo_legend.table import TableSkill


@pytest.fixture
def registry():
    return build_default_registry()


# ==================== RoseSkill Tests ====================

def test_proposal_comparison_style_renders_valid_png(registry):
    """测试 RoseSkill proposal_comparison 样式双环对比图"""
    request = RenderRequest(legend_type="rose", style="proposal_comparison", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert result.media_type == "image/png"
    assert image.size == (720, 900)


def test_lottery_black_style_renders_valid_png(registry):
    """测试 RoseSkill lottery_black 样式单环图"""
    request = RenderRequest(legend_type="rose", style="lottery_black", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_rose_styles_produce_different_outputs(registry):
    """测试双环 vs 单环模式输出不同"""
    proposal = registry.render(RenderRequest(legend_type="rose", style="proposal_comparison", width=720, height=900))
    lottery = registry.render(RenderRequest(legend_type="rose", style="lottery_black", width=720, height=900))

    assert proposal.content != lottery.content


def test_rose_custom_values(registry):
    """测试自定义 current_values 和 proposed_values 数据"""
    custom_data = {
        "current_values": [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 1, 0.5, 0.3, 0.1],
        "proposed_values": [10, 10, 10, 10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5]
    }
    request = RenderRequest(
        legend_type="rose",
        style="proposal_comparison",
        width=720,
        height=900,
        data=custom_data
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


# ==================== TableSkill Tests ====================

def test_heatmap_light_style_renders_valid_png(registry):
    """测试 TableSkill heatmap_light 样式表格渲染成功"""
    request = RenderRequest(legend_type="table", style="heatmap_light", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert result.media_type == "image/png"
    assert image.size == (720, 900)


def test_scoreboard_dark_style_renders_valid_png(registry):
    """测试 TableSkill scoreboard_dark 样式暗色主题"""
    request = RenderRequest(legend_type="table", style="scoreboard_dark", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_scoreboard_dark_cell_text_uses_contrast_color():
    assert TableSkill._cell_text_color("#a6efb7") == "#050505"
    assert TableSkill._cell_text_color("#fff1b8") == "#050505"
    assert TableSkill._cell_text_color("#4d3300") == "#ffffff"


def test_table_styles_have_different_themes(registry):
    """测试亮色主题 vs 暗色主题输出不同"""
    light = registry.render(RenderRequest(legend_type="table", style="heatmap_light", width=720, height=900))
    dark = registry.render(RenderRequest(legend_type="table", style="scoreboard_dark", width=720, height=900))

    assert light.content != dark.content


def test_table_custom_rows_data(registry):
    """测试自定义 rows 数据替换默认数据"""
    custom_data = {
        "rows": [
            {
                "team": "NEO",
                "team_color": "#29b98f",
                "name": "Test Player",
                "pts_created": 45.5,
                "ts": 62,
                "ast_tov": 3.0,
                "mpg": 36.5
            },
            {
                "team": "LEG",
                "team_color": "#ff5733",
                "name": "Another Player",
                "pts_created": 38.2,
                "ts": 58,
                "ast_tov": 2.1,
                "mpg": 34.0
            }
        ]
    }
    request = RenderRequest(
        legend_type="table",
        style="heatmap_light",
        width=720,
        height=900,
        data=custom_data,
        title="Custom Table Test"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_table_custom_title(registry):
    """测试自定义标题生效"""
    request = RenderRequest(
        legend_type="table",
        style="heatmap_light",
        width=720,
        height=900,
        title="LEADERS IN ASSISTS",
        subtitle="REGULAR SEASON"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_league_standings_gradient_style_renders_valid_png(registry):
    request = RenderRequest(
        legend_type="table",
        style="league_standings_gradient",
        width=900,
        height=720,
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert result.media_type == "image/png"
    assert image.size == (900, 720)


def test_league_standings_gradient_columns_are_independently_configurable(registry):
    request = RenderRequest(
        legend_type="table",
        style="league_standings_gradient",
        width=640,
        height=640,
        data=_small_gradient_table({"score": {"midpoint": "average"}}),
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content)).convert("RGB")
    score_cell = image.getpixel((int(0.45 * image.width), int(0.545 * image.height)))
    neutral_cell = image.getpixel((int(0.74 * image.width), int(0.545 * image.height)))

    assert score_cell[2] > score_cell[0] + 30
    assert all(channel > 238 for channel in neutral_cell)


def test_league_standings_gradient_uses_average_as_midpoint():
    columns = [
        {"key": "team", "label": "Team"},
        {"key": "score", "label": "Score"},
    ]
    rows = [
        {"team": "High", "score": 120},
        {"team": "Low", "score": 80},
    ]
    average_row = {"team": "Average", "score": 100}
    gradients = TableSkill._gradient_configs(
        {"gradient_columns": {"score": {"midpoint": "average"}}},
        columns,
        rows,
        average_row,
    )

    high = ImageColor.getrgb(TableSkill._diverging_cell_color(120, **gradients["score"]))
    low = ImageColor.getrgb(TableSkill._diverging_cell_color(80, **gradients["score"]))

    assert gradients["score"]["midpoint"] == 100
    assert high[0] > high[2]
    assert low[2] > low[0]


def test_league_standings_gradient_themes_are_configurable():
    default_theme = TableSkill._league_theme({"color_theme": "clean_contrast"})
    emerald_theme = TableSkill._league_theme({"color_theme": "emerald_coral"})
    random_theme = TableSkill._league_theme({"color_theme": "random", "theme_seed": "stable"})
    random_data = {"color_theme": "random", "theme_seed": "stable"}
    TableSkill._league_theme(random_data)

    assert len(default_theme) >= 10
    assert default_theme["mid"] == "#ffffff"
    assert default_theme["header"] != emerald_theme["header"]
    assert random_theme in TableSkill._available_league_themes()
    assert random_data["_resolved_color_theme"] in {"clean_contrast", "emerald_coral", "royal_gold", "ink_ruby"}


def test_league_standings_gradient_supports_merged_header_groups(registry):
    data = _small_grouped_table()
    columns = TableSkill._league_columns(data)
    groups = TableSkill._header_groups(data, columns)

    assert groups[0]["label"] == "Offense"
    assert groups[0]["children"][0]["columns"] == ["off_rank", "off_value"]

    request = RenderRequest(
        legend_type="table",
        style="league_standings_gradient",
        width=900,
        height=640,
        data=data,
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.size == (900, 640)
    assert image.format == "PNG"


def test_league_standings_gradient_can_compose_left_image(registry, tmp_path):
    side_path = tmp_path / "side.png"
    Image.new("RGB", (80, 240), "#f0442f").save(side_path)
    data = _small_gradient_table({"score": {"midpoint": "average"}})
    data["left_image"] = {
        "path": str(side_path),
        "width_ratio": 0.25,
        "padding": 0,
        "fit": "cover",
    }
    request = RenderRequest(
        legend_type="table",
        style="league_standings_gradient",
        width=800,
        height=640,
        data=data,
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content)).convert("RGB")
    left_pixel = image.getpixel((40, image.height // 2))
    chart_pixel = image.getpixel((240, image.height // 2))

    assert image.size == (800, 640)
    assert left_pixel[0] > 210 and left_pixel[1] < 90 and left_pixel[2] < 90
    assert chart_pixel != left_pixel


def test_rose_invalid_style_raises_error(registry):
    """测试 RoseSkill 无效 style 抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="rose", style="invalid"))


def test_table_invalid_style_raises_error(registry):
    """测试 TableSkill 无效 style 抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="table", style="invalid"))


def _small_gradient_table(gradient_columns):
    return {
        "color_theme": "clean_contrast",
        "left": 0.003,
        "right": 0.997,
        "top": 0.996,
        "bottom": 0.018,
        "header_height": 0.14,
        "row_height": 0.16,
        "columns": [
            {"key": "rank", "label": "Rank", "width": 0.12, "format": "int"},
            {"key": "team", "label": "Team", "width": 0.28},
            {"key": "score", "label": "Score", "width": 0.30, "format": "int"},
            {"key": "pace", "label": "Pace", "width": 0.30, "format": "int"},
        ],
        "average_row": {"team": "Average", "score": 100, "pace": 100},
        "gradient_columns": gradient_columns,
        "rows": [
            {"rank": 1, "team": "High", "score": 120, "pace": 120},
            {"rank": 2, "team": "Low", "score": 80, "pace": 80},
        ],
    }


def _small_grouped_table():
    return {
        "color_theme": "clean_contrast",
        "columns": [
            {"key": "rank", "label": "Rank", "width": 0.12, "format": "int"},
            {"key": "team", "label": "Team", "width": 0.28},
            {"key": "off_rank", "label": "", "width": 0.15, "format": "int"},
            {"key": "off_value", "label": "", "width": 0.15, "format": "int"},
            {"key": "def_rank", "label": "", "width": 0.15, "format": "int"},
            {"key": "def_value", "label": "", "width": 0.15, "format": "int"},
        ],
        "header_groups": [
            {
                "label": "Offense",
                "columns": ["off_rank", "off_value"],
                "children": [{"label": "Rating", "columns": ["off_rank", "off_value"]}],
            },
            {
                "label": "Defense",
                "columns": ["def_rank", "def_value"],
                "children": [{"label": "Rating", "columns": ["def_rank", "def_value"]}],
            },
        ],
        "average_row": {"team": "Average", "off_value": 100, "def_value": 100},
        "gradient_columns": {
            "off_rank": {"midpoint": "mean", "higher_is_better": False},
            "def_rank": {"midpoint": "mean", "higher_is_better": False},
        },
        "rows": [
            {"rank": 1, "team": "A", "off_rank": 1, "off_value": 120, "def_rank": 2, "def_value": 90},
            {"rank": 2, "team": "B", "off_rank": 2, "off_value": 80, "def_rank": 1, "def_value": 110},
        ],
    }

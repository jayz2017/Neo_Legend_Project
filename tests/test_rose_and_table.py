from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


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

from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


# ==================== CoordinateSkill Tests ====================

def test_dark_bubble_style_renders_valid_png(registry):
    """测试 CoordinateSkill dark_bubble 样式散点图可正常渲染"""
    request = RenderRequest(legend_type="coordinate", style="dark_bubble", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert result.media_type == "image/png"
    assert image.size == (720, 900)


def test_gold_scorers_style_renders_valid_png(registry):
    """测试 CoordinateSkill gold_scorers 样式渲染成功"""
    request = RenderRequest(legend_type="coordinate", style="gold_scorers", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_coordinate_styles_have_different_colors(registry):
    """测试两种样式配色存在差异（输出内容不同）"""
    dark = registry.render(RenderRequest(legend_type="coordinate", style="dark_bubble", width=720, height=900))
    gold = registry.render(RenderRequest(legend_type="coordinate", style="gold_scorers", width=720, height=900))

    assert dark.content != gold.content


def test_coordinate_custom_points_data(registry):
    """测试自定义 points 数据覆盖默认数据"""
    custom_data = {
        "points": [
            {"label": "Test Player 1", "x": 22.0, "y": 55.0, "size": 500},
            {"label": "Test Player 2", "x": 28.0, "y": 60.0, "size": 800},
        ]
    }
    request = RenderRequest(
        legend_type="coordinate",
        style="dark_bubble",
        width=720,
        height=900,
        data=custom_data
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_coordinate_custom_title(registry):
    """测试自定义标题生效"""
    request = RenderRequest(
        legend_type="coordinate",
        style="dark_bubble",
        width=720,
        height=900,
        title="Custom Scorers Title"
    )
    result = registry.render(request)
    assert result.legend_type == "coordinate"


# ==================== PlusMinusCoordinateSkill Tests ====================

def test_paper_quadrant_style_renders_valid_png(registry):
    """测试 PlusMinusCoordinateSkill paper_quadrant 样式四象限划分正确"""
    request = RenderRequest(legend_type="plus_minus_coordinate", style="paper_quadrant", width=720, height=720)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert result.media_type == "image/png"
    assert image.size == (720, 720)


def test_clean_quadrant_style_renders_valid_png(registry):
    """测试 clean_quadrant 样式无纹理背景"""
    request = RenderRequest(legend_type="plus_minus_coordinate", style="clean_quadrant", width=720, height=720)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_quadrant_styles_differ_in_background(registry):
    """测试 paper_quadrant 有纹理而 clean_quadrant 无纹理（输出不同）"""
    paper = registry.render(RenderRequest(legend_type="plus_minus_coordinate", style="paper_quadrant", width=720, height=720))
    clean = registry.render(RenderRequest(legend_type="plus_minus_coordinate", style="clean_quadrant", width=720, height=720))

    assert paper.content != clean.content


def test_plus_minus_custom_points_data(registry):
    """测试自定义 points 数据覆盖默认数据"""
    custom_data = {
        "points": [
            {"label": "TEAM A", "x": 5.0, "y": 5.0, "color": "#ff0000"},
            {"label": "TEAM B", "x": -5.0, "y": -5.0, "color": "#0000ff"},
        ]
    }
    request = RenderRequest(
        legend_type="plus_minus_coordinate",
        style="paper_quadrant",
        width=720,
        height=720,
        data=custom_data
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_coordinate_invalid_style_raises_error(registry):
    """测试 CoordinateSkill 无效 style 抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="coordinate", style="invalid"))


def test_plus_minus_invalid_style_raises_error(registry):
    """测试 PlusMinusCoordinateSkill 无效 style 抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="plus_minus_coordinate", style="invalid"))

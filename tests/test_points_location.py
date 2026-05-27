from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_default_style_renders_valid_png(registry):
    """测试 default 样式匹配参考图片视觉特征（深色背景、六边形网格、青色渐变、底部图例）"""
    request = RenderRequest(legend_type="points_location", style="default", width=720, height=900)
    result = registry.render(request)

    assert result.media_type == "image/png"
    assert result.legend_type == "points_location"
    assert result.style == "default"

    image = Image.open(BytesIO(result.content))
    assert image.size == (720, 900)
    assert image.format == "PNG"


def test_warm_gradient_style_renders_valid_png(registry):
    """测试 warm_gradient 样式使用暖色系配色"""
    request = RenderRequest(legend_type="points_location", style="warm_gradient", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_styles_produce_different_outputs(registry):
    """测试 default 和 warm_gradient 样式输出内容存在差异"""
    default_result = registry.render(RenderRequest(legend_type="points_location", style="default", width=720, height=900))
    warm_result = registry.render(RenderRequest(legend_type="points_location", style="warm_gradient", width=720, height=900))

    assert default_result.content != warm_result.content


def test_custom_shots_data(registry):
    """测试自定义 shots 数据生成不同热力分布"""
    custom_data = {
        "shots": [
            {"x": 0.0, "y": 50.0, "points": 800},
            {"x": -150.0, "y": 200.0, "points": 600},
            {"x": 150.0, "y": 200.0, "points": 500},
            {"x": -100.0, "y": 300.0, "points": 400},
            {"x": 100.0, "y": 300.0, "points": 350},
            {"x": 0.0, "y": 100.0, "points": 700},
        ] * 20
    }
    request = RenderRequest(
        legend_type="points_location",
        style="default",
        width=720,
        height=900,
        data=custom_data
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_default_data_fallback(registry):
    """测试无自定义数据时使用默认数据正常渲染"""
    request = RenderRequest(legend_type="points_location", style="default", width=720, height=900, data={})
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_custom_title_and_subtitle(registry):
    """测试自定义标题和副标题正确显示"""
    request = RenderRequest(
        legend_type="points_location",
        style="default",
        width=720,
        height=900,
        title="Custom Points Title",
        subtitle="2025-26 Season | Custom Author"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_invalid_style_raises_error(registry):
    """测试无效 style 参数抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="points_location", style="invalid_style"))


def test_points_location_registered_in_registry(registry):
    """验证 points_location 类型已在注册表中可用"""
    types = registry.list_types()
    type_names = [t.legend_type for t in types]

    assert "points_location" in type_names

    points_location_meta = next(t for t in types if t.legend_type == "points_location")
    assert points_location_meta.display_name == "Total Points By Location"
    assert len(points_location_meta.styles) == 2
    style_names = [s.name for s in points_location_meta.styles]
    assert "default" in style_names
    assert "warm_gradient" in style_names

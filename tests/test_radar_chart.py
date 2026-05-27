from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_neon_glow_style_renders_valid_png(registry):
    """测试 neon_glow 样式渲染成功"""
    request = RenderRequest(legend_type="radar_chart", style="neon_glow", width=800, height=1000)
    result = registry.render(request)

    assert result.media_type == "image/png"
    assert result.legend_type == "radar_chart"
    assert result.style == "neon_glow"

    image = Image.open(BytesIO(result.content))
    assert image.size == (800, 1000)
    assert image.format == "PNG"


def test_crystal_metal_style_renders_valid_png(registry):
    """测试 crystal_metal 样式渲染成功"""
    request = RenderRequest(legend_type="radar_chart", style="crystal_metal", width=800, height=1000)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_gradient_rainbow_style_renders_valid_png(registry):
    """测试 gradient_rainbow 样式渲染成功"""
    request = RenderRequest(legend_type="radar_chart", style="gradient_rainbow", width=800, height=1000)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_all_styles_produce_different_outputs(registry):
    """测试三种样式输出内容存在差异"""
    styles = ["neon_glow", "crystal_metal", "gradient_rainbow"]
    results = []
    for style in styles:
        req = RenderRequest(legend_type="radar_chart", style=style, width=800, height=1000)
        results.append(registry.render(req).content)

    # 确保至少有两两不同
    assert results[0] != results[1] or results[1] != results[2]


def test_custom_categories_and_datasets(registry):
    """测试自定义 categories 和 datasets 数据"""
    custom_data = {
        "categories": ["Speed", "Power", "Defense", "Magic", "Luck"],
        "datasets": [
            {"label": "Warrior", "values": [90, 85, 78, 60, 88], "color": "#ff4444"},
            {"label": "Mage", "values": [65, 55, 70, 95, 75], "color": "#4444ff"},
            {"label": "Rogue", "values": [88, 72, 82, 68, 92], "color": "#44ff44"},
        ]
    }
    request = RenderRequest(
        legend_type="radar_chart",
        style="neon_glow",
        width=800,
        height=1000,
        data=custom_data,
        title="RPG Character Stats",
        subtitle="Multi-class Comparison"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_single_dataset_fallback(registry):
    """测试单个 dataset 正常渲染"""
    custom_data = {
        "categories": ["A", "B", "C"],
        "datasets": [
            {"label": "Only One", "values": [80, 90, 75], "color": "#ff6b6b"}
        ]
    }
    request = RenderRequest(legend_type="radar_chart", style="crystal_metal", width=800, height=1000, data=custom_data)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_custom_title_and_subtitle(registry):
    """测试自定义标题和副标题"""
    request = RenderRequest(
        legend_type="radar_chart",
        style="gradient_rainbow",
        width=800,
        height=1000,
        title="Custom Radar Title",
        subtitle="Custom Subtitle Here"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_invalid_style_raises_error(registry):
    """测试无效 style 参数抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="radar_chart", style="invalid_style"))


def test_radar_registered_in_registry(registry):
    """验证 radar_chart 类型已在注册表中"""
    types = {t.legend_type for t in registry.list_types()}
    assert "radar_chart" in types

    radar_meta = next(t for t in registry.list_types() if t.legend_type == "radar_chart")
    assert radar_meta.display_name == "Luxury Radar Chart"
    assert len(radar_meta.styles) == 3  # neon_glow, crystal_metal, gradient_rainbow

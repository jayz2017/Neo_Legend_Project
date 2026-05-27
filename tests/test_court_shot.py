from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_terrain_style_renders_valid_png(registry):
    """测试 terrain 样式默认数据渲染成功且图片有效"""
    request = RenderRequest(legend_type="court_shot", style="terrain", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert result.media_type == "image/png"
    assert image.size == (720, 900)
    assert image.format == "PNG"


def test_hex_style_renders_valid_png(registry):
    """测试 hex 样式渲染成功"""
    request = RenderRequest(legend_type="court_shot", style="hex", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_zone_style_renders_valid_png(registry):
    """测试 zone 样式渲染成功"""
    request = RenderRequest(legend_type="court_shot", style="zone", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_points_location_brightens_high_accumulation_regions(registry):
    request = RenderRequest(
        legend_type="court_shot",
        style="points_location",
        width=720,
        height=900,
        data={
            "shots": (
                [{"x": 0.0, "y": 55.0, "points": 8.0}] * 700
                + [{"x": -220.0, "y": 95.0, "points": 2.0}] * 50
                + [{"x": 0.0, "y": 330.0, "points": 1.0}] * 20
            ),
            "max_points": 800,
        },
    )

    result = registry.render(request)
    image = Image.open(BytesIO(result.content)).convert("RGB")

    rim_luma = _mean_luma(image, (340, 640, 380, 700))
    sparse_luma = _mean_luma(image, (340, 360, 380, 410))

    assert rim_luma > sparse_luma + 20


def test_different_styles_produce_different_outputs(registry):
    """测试不同样式输出内容存在差异"""
    terrain = registry.render(RenderRequest(legend_type="court_shot", style="terrain", width=720, height=900))
    zone = registry.render(RenderRequest(legend_type="court_shot", style="zone", width=720, height=900))

    assert terrain.content != zone.content


def test_custom_shot_count_affects_output(registry):
    """测试自定义 shot_count 参数影响输出"""
    small = registry.render(RenderRequest(
        legend_type="court_shot",
        style="terrain",
        width=720,
        height=900,
        data={"shot_count": 100}
    ))
    large = registry.render(RenderRequest(
        legend_type="court_shot",
        style="terrain",
        width=720,
        height=900,
        data={"shot_count": 1000}
    ))

    assert small.content != large.content


def test_custom_seed_affects_output(registry):
    """测试自定义 seed 参数影响输出"""
    seed1 = registry.render(RenderRequest(
        legend_type="court_shot",
        style="terrain",
        width=720,
        height=900,
        data={"seed": 1}
    ))
    seed2 = registry.render(RenderRequest(
        legend_type="court_shot",
        style="terrain",
        width=720,
        height=900,
        data={"seed": 99}
    ))

    assert seed1.content != seed2.content


def test_custom_title_and_subtitle(registry):
    """测试自定义 title 和 subtitle 正确显示（验证不报错即可）"""
    request = RenderRequest(
        legend_type="court_shot",
        style="terrain",
        width=720,
        height=900,
        title="CUSTOM PLAYER",
        subtitle="CUSTOM SEASON 2025-26"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_invalid_style_raises_error(registry):
    """测试无效 style 参数抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="court_shot", style="invalid_style"))


def test_default_style_when_none_provided(registry):
    """测试不提供 style 时使用默认值"""
    request = RenderRequest(legend_type="court_shot", width=720, height=900)
    result = registry.render(request)

    assert result.style == "terrain"


def _mean_luma(image: Image.Image, box: tuple[int, int, int, int]) -> float:
    crop = image.crop(box)
    pixels = list(crop.getdata())
    return sum(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in pixels) / len(pixels)

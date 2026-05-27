from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_empty_dict_data_fallback(registry):
    """测试空字典 data 参数的降级处理"""
    request = RenderRequest(legend_type="court_shot", style="terrain", width=640, height=640, data={})
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_none_data_fallback(registry):
    """测试不传 data 参数时使用默认空字典"""
    request = RenderRequest(legend_type="table", style="heatmap_light", width=640, height=640)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_unicode_title_and_subtitle(registry):
    """测试 Unicode 字符标题/副标题正常处理"""
    request = RenderRequest(
        legend_type="court_shot",
        style="terrain",
        width=640,
        height=640,
        title="🏀 球员统计 📊",
        subtitle="赛季 2025-26 | 作者 @测试用户"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_very_long_title(registry):
    """测试长文本标题不导致错误"""
    long_title = "A" * 200
    request = RenderRequest(
        legend_type="coordinate",
        style="dark_bubble",
        width=640,
        height=640,
        title=long_title
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_square_aspect_ratio(registry):
    """测试正方形比例图片生成"""
    request = RenderRequest(legend_type="rose", style="lottery_black", width=800, height=800)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.size == (800, 800)


def test_portrait_orientation(registry):
    """测试竖向比例图片生成"""
    request = RenderRequest(legend_type="table", style="heatmap_light", width=640, height=1280)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.size == (640, 1280)

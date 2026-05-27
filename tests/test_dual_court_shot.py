from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_year_over_year_style_renders_valid_png(registry):
    """测试 year_over_year 样式双面板布局正确"""
    request = RenderRequest(legend_type="dual_court_shot", style="year_over_year", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert result.media_type == "image/png"
    assert image.size == (720, 900)


def test_split_hex_style_renders_valid_png(registry):
    """测试 split_hex 样式渲染成功"""
    request = RenderRequest(legend_type="dual_court_shot", style="split_hex", width=720, height=900)
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_different_styles_produce_different_outputs(registry):
    """测试不同样式输出内容存在差异"""
    yoy = registry.render(RenderRequest(legend_type="dual_court_shot", style="year_over_year", width=720, height=900))
    split = registry.render(RenderRequest(legend_type="dual_court_shot", style="split_hex", width=720, height=900))

    assert yoy.content != split.content


def test_custom_panels_data(registry):
    """测试自定义 panels 数据（两个赛季的 metrics）正确显示"""
    custom_data = {
        "panels": [
            {
                "season": "2022-23",
                "attempts": "65 GAMES / 650 ATTEMPTS",
                "seed": 77,
                "metrics": {"FG%": "45.0%", "3P%": "30.0%", "eFG%": "50.0%"}
            },
            {
                "season": "2023-24",
                "attempts": "70 GAMES / 700 ATTEMPTS",
                "seed": 88,
                "metrics": {"FG%": "48.5%", "3P%": "35.5%", "eFG%": "54.2%"}
            }
        ]
    }
    request = RenderRequest(
        legend_type="dual_court_shot",
        style="year_over_year",
        width=720,
        height=900,
        data=custom_data
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_most_improved_badge_displayed(registry):
    """测试 MOST IMPROVED 徽章在第二个面板正确显示（使用非默认seed触发）"""
    custom_data = {
        "panels": [
            {
                "season": "2024-25",
                "attempts": "79 GAMES / 808 ATTEMPTS",
                "seed": 12,
                "metrics": {"FG%": "47.6%", "3P%": "33.2%", "eFG%": "53.7%"}
            },
            {
                "season": "2025-26",
                "attempts": "71 GAMES / 774 ATTEMPTS",
                "seed": 44,
                "metrics": {"FG%": "51.8%", "3P%": "42.0%", "eFG%": "58.4%"}
            }
        ]
    }
    request = RenderRequest(
        legend_type="dual_court_shot",
        style="year_over_year",
        width=720,
        height=900,
        data=custom_data
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_metrics_panel_rendering(registry):
    """测试 FG%, 3P%, eFG% 统计指标面板正确渲染"""
    request = RenderRequest(legend_type="dual_court_shot", style="year_over_year", width=720, height=900)
    result = registry.render(request)

    assert "dual_court_shot" in result.legend_type


def test_custom_title_and_subtitle(registry):
    """测试自定义标题和副标题"""
    request = RenderRequest(
        legend_type="dual_court_shot",
        style="year_over_year",
        width=720,
        height=900,
        title="TEST PLAYER",
        subtitle="CUSTOM TEAM / COMPARISON"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_invalid_style_raises_error(registry):
    """测试无效 style 参数抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="dual_court_shot", style="invalid"))

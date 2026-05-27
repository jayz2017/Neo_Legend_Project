from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_water_drops_style(registry):
    req = RenderRequest(legend_type="bubble_chart", style="water_drops", width=1000, height=800)
    result = registry.render(req)
    assert result.media_type == "image/png"
    img = Image.open(BytesIO(result.content))
    assert img.size == (1000, 800)


def test_fireflies_style(registry):
    req = RenderRequest(legend_type="bubble_chart", style="fireflies", width=1000, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_galaxy_stars_style(registry):
    req = RenderRequest(legend_type="bubble_chart", style="galaxy_stars", width=1000, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_crystal_orbs_style(registry):
    req = RenderRequest(legend_type="bubble_chart", style="crystal_orbs", width=1000, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_all_bubble_styles_differ(registry):
    styles = ["water_drops", "fireflies", "galaxy_stars", "crystal_orbs"]
    contents = [registry.render(RenderRequest(legend_type="bubble_chart", style=s, width=800, height=800)).content for s in styles]
    assert len(set(contents)) == 4


def test_custom_bubble_data(registry):
    data = {
        "points": [
            {"x": 1.2, "y": 3.4, "size": 500, "color": "#ff6b6b", "label": "A"},
            {"x": 2.5, "y": 2.1, "size": 800, "color": "#4ecdc4", "label": "B"},
            {"x": 1.8, "y": 4.2, "size": 300, "color": "#ffeaa7", "label": "C"},
            {"x": 3.5, "y": 1.5, "size": 600, "color": "#74b9ff", "label": "D"},
        ]
    }
    req = RenderRequest(legend_type="bubble_chart", style="water_drops", width=1000, height=800, data=data, title="Custom Bubbles")
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_size_mapping(registry):
    """测试大小映射到第三维数据"""
    small_data = {
        "points": [{"x": i, "y": i, "size": 100 * (i+1), "color": "#ff6b6b", "label": f"P{i}"} for i in range(5)]
    }
    req = RenderRequest(legend_type="bubble_chart", style="fireflies", width=900, height=700, data=small_data)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_invalid_style(registry):
    from neo_legend.errors import UnknownStyleError
    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="bubble_chart", style="invalid"))


def test_bubble_registered(registry):
    assert "bubble_chart" in {t.legend_type for t in registry.list_types()}
    meta = next(t for t in registry.list_types() if t.legend_type == "bubble_chart")
    assert len(meta.styles) == 4

from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_glass_3d_style(registry):
    req = RenderRequest(legend_type="bar_chart", style="glass_3d", width=1000, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_neon_tubes_style(registry):
    req = RenderRequest(legend_type="bar_chart", style="neon_tubes", width=1000, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_gradient_sky_style(registry):
    req = RenderRequest(legend_type="bar_chart", style="gradient_sky", width=1000, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_crystal_pillars_style(registry):
    req = RenderRequest(legend_type="bar_chart", style="crystal_pillars", width=1000, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_all_bar_styles_differ(registry):
    styles = ["glass_3d", "neon_tubes", "gradient_sky", "crystal_pillars"]
    contents = [registry.render(RenderRequest(legend_type="bar_chart", style=s, width=800, height=800)).content for s in styles]
    assert len(set(contents)) == 4


def test_grouped_mode(registry):
    data = {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "grouped": [
            {"label": "2024", "values": [80, 90, 70, 85], "color": "#ff006e"},
            {"label": "2025", "values": [88, 78, 95, 92], "color": "#3a86ff"}
        ]
    }
    req = RenderRequest(legend_type="bar_chart", style="neon_tubes", width=1000, height=800, data=data, title="Grouped Test")
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_custom_labels_values(registry):
    data = {"labels": ["A", "B", "C", "D", "E"], "values": [10, 25, 18, 30, 22]}
    req = RenderRequest(legend_type="bar_chart", style="glass_3d", width=900, height=700, data=data)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_invalid_style(registry):
    from neo_legend.errors import UnknownStyleError
    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="bar_chart", style="invalid"))


def test_bar_registered(registry):
    assert "bar_chart" in {t.legend_type for t in registry.list_types()}

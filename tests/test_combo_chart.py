from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_crystal_stream_style(registry):
    req = RenderRequest(legend_type="combo_chart", style="crystal_stream", width=1200, height=800)
    result = registry.render(req)
    assert result.media_type == "image/png"
    img = Image.open(BytesIO(result.content))
    assert img.size == (1200, 800)


def test_neon_pulse_style(registry):
    req = RenderRequest(legend_type="combo_chart", style="neon_pulse", width=1200, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_sunset_gradient_style(registry):
    req = RenderRequest(legend_type="combo_chart", style="sunset_gradient", width=1200, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_ocean_depths_style(registry):
    req = RenderRequest(legend_type="combo_chart", style="ocean_depths", width=1200, height=800)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_all_combo_styles_differ(registry):
    styles = ["crystal_stream", "neon_pulse", "sunset_gradient", "ocean_depths"]
    contents = []
    for s in styles:
        req = RenderRequest(legend_type="combo_chart", style=s, width=1000, height=700)
        contents.append(registry.render(req).content)
    assert len(set(contents)) == 4


def test_custom_data(registry):
    data = {
        "categories": ["Jan", "Feb", "Mar", "Apr", "May"],
        "bar_values": [120, 145, 132, 168, 155],
        "line_values": [45, 52, 48, 62, 58],
        "bar_label": "Revenue",
        "line_label": "Growth %"
    }
    req = RenderRequest(
        legend_type="combo_chart",
        style="sunset_gradient",
        width=1200,
        height=800,
        data=data,
        title="Revenue & Growth Analysis"
    )
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_empty_data_fallback(registry):
    req = RenderRequest(legend_type="combo_chart", style="crystal_stream", width=1000, height=700, data={})
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_invalid_style(registry):
    from neo_legend.errors import UnknownStyleError
    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="combo_chart", style="bad"))


def test_combo_registered(registry):
    types = {t.legend_type for t in registry.list_types()}
    assert "combo_chart" in types
    meta = next(t for t in registry.list_types() if t.legend_type == "combo_chart")
    assert len(meta.styles) == 4

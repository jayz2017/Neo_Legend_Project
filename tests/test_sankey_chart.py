from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_neon_streams_style(registry):
    req = RenderRequest(legend_type="sankey_chart", style="neon_streams", width=1200, height=900)
    result = registry.render(req)
    assert result.media_type == "image/png"
    img = Image.open(BytesIO(result.content))
    assert img.size == (1200, 900)


def test_energy_flow_style(registry):
    req = RenderRequest(legend_type="sankey_chart", style="energy_flow", width=1200, height=900)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_crystal_rivers_style(registry):
    req = RenderRequest(legend_type="sankey_chart", style="crystal_rivers", width=1200, height=900)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_golden_paths_style(registry):
    req = RenderRequest(legend_type="sankey_chart", style="golden_paths", width=1200, height=900)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_all_sankey_styles_differ(registry):
    styles = ["neon_streams", "energy_flow", "crystal_rivers", "golden_paths"]
    contents = [registry.render(RenderRequest(legend_type="sankey_chart", style=s, width=1000, height=800)).content for s in styles]
    assert len(set(contents)) == 4


def test_custom_sankey_data(registry):
    data = {
        "nodes": [
            {"id": "source", "label": "Source", "x": 0.1, "y": 0.5},
            {"id": "a", "label": "Page A", "x": 0.4, "y": 0.3},
            {"id": "b", "label": "Page B", "x": 0.4, "y": 0.7},
            {"id": "conv", "label": "Convert", "x": 0.7, "y": 0.5},
            {"id": "exit", "label": "Exit", "x": 0.9, "y": 0.5}
        ],
        "flows": [
            {"source": "source", "target": "a", "value": 1000, "color": "#ff6b6b"},
            {"source": "source", "target": "b", "value": 800, "color": "#4ecdc4"},
            {"source": "a", "target": "conv", "value": 600, "color": "#45b7d1"},
            {"source": "b", "target": "conv", "value": 450, "color": "#96ceb4"},
            {"source": "conv", "target": "exit", "value": 850, "color": "#ffeaa7"}
        ]
    }
    req = RenderRequest(legend_type="sankey_chart", style="golden_paths", width=1200, height=900, data=data, title="Traffic Flow")
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_default_data_fallback(registry):
    """测试无自定义数据时使用默认数据正常渲染"""
    req = RenderRequest(legend_type="sankey_chart", style="neon_streams", width=1000, height=800, data={})
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_invalid_style(registry):
    from neo_legend.errors import UnknownStyleError
    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="sankey_chart", style="bad_style"))


def test_sankey_registered(registry):
    assert "sankey_chart" in {t.legend_type for t in registry.list_types()}
    meta = next(t for t in registry.list_types() if t.legend_type == "sankey_chart")
    assert meta.display_name == "Luxury Sankey Diagram"
    assert len(meta.styles) == 4

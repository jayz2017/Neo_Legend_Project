from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_versus_battle_style(registry):
    request = RenderRequest(legend_type="dual_radar_chart", style="versus_battle", width=1000, height=800)
    result = registry.render(request)
    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_mirror_compare_style(registry):
    request = RenderRequest(legend_type="dual_radar_chart", style="mirror_compare", width=1000, height=800)
    result = registry.render(request)
    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_evolution_track_style(registry):
    request = RenderRequest(legend_type="dual_radar_chart", style="evolution_track", width=1000, height=900)
    result = registry.render(request)
    image = Image.open(BytesIO(result.content))
    assert image.format == "PNG"


def test_styles_differ(registry):
    styles = ["versus_battle", "mirror_compare", "evolution_track"]
    results = [registry.render(RenderRequest(legend_type="dual_radar_chart", style=s, width=800, height=800)).content for s in styles]
    assert len(set(results)) == 3  # 所有不同


def test_custom_dual_data(registry):
    data = {
        "left": {"label": "2024 Player", "categories": ["PTS", "REB", "AST"], "values": [25, 8, 6]},
        "right": {"label": "2025 Player", "categories": ["PTS", "REB", "AST"], "values": [30, 10, 8]}
    }
    req = RenderRequest(legend_type="dual_radar_chart", style="versus_battle", width=1000, height=800, data=data)
    result = registry.render(req)
    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_invalid_style(registry):
    from neo_legend.errors import UnknownStyleError
    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="dual_radar_chart", style="bad"))


def test_registered(registry):
    assert "dual_radar_chart" in {t.legend_type for t in registry.list_types()}

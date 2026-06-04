from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_line_chart_styles_render(registry):
    for style in ["executive_trend", "champagne_forecast", "aurora_stream"]:
        result = registry.render(RenderRequest(legend_type="line_chart", style=style, width=1000, height=800))
        image = Image.open(BytesIO(result.content))

        assert result.media_type == "image/png"
        assert image.format == "PNG"
        assert image.size == (1000, 800)


def test_line_chart_custom_series(registry):
    data = {
        "categories": ["Jan", "Feb", "Mar", "Apr"],
        "series": [
            {"label": "Actual", "values": [22, 28, 31, 38], "color": "#36d5ff"},
            {"label": "Target", "values": [24, 27, 33, 40], "color": "#f6d365"},
        ],
        "benchmark": 30,
    }

    result = registry.render(
        RenderRequest(
            legend_type="line_chart",
            style="executive_trend",
            width=1000,
            height=800,
            data=data,
        )
    )

    assert Image.open(BytesIO(result.content)).format == "PNG"


def test_line_chart_registered(registry):
    metadata = next(item for item in registry.list_types() if item.legend_type == "line_chart")

    assert metadata.display_name == "Luxury Line Chart"
    assert len(metadata.styles) == 3

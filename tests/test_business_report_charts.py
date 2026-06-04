from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


@pytest.mark.parametrize(
    ("legend_type", "styles"),
    [
        ("calendar_chart", ["executive_month", "earnings_calendar"]),
        ("matrix_bubble_chart", ["correlation_board", "risk_heat_matrix"]),
        ("chord_chart", ["capital_flows", "sector_rotation"]),
        ("scatter_matrix_chart", ["macro_quadrants", "portfolio_pairs"]),
        ("stacked_bar_chart", ["wall_street_stack", "portfolio_stack"]),
    ],
)
def test_business_report_chart_styles_render(registry, legend_type, styles):
    contents = []
    for style in styles:
        result = registry.render(RenderRequest(legend_type=legend_type, style=style, width=1000, height=800))
        image = Image.open(BytesIO(result.content))

        assert result.media_type == "image/png"
        assert image.format == "PNG"
        assert image.size == (1000, 800)
        contents.append(result.content)

    assert len(set(contents)) == len(styles)


def test_matrix_bubble_accepts_custom_values(registry):
    data = {
        "rows": ["Credit", "Rates"],
        "columns": ["Growth", "Inflation", "FX"],
        "values": [[0.82, -0.42, 0.15], [-0.71, 0.34, -0.22]],
    }
    result = registry.render(
        RenderRequest(
            legend_type="matrix_bubble_chart",
            style="correlation_board",
            width=900,
            height=700,
            data=data,
        )
    )

    assert Image.open(BytesIO(result.content)).format == "PNG"

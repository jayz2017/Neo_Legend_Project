from __future__ import annotations

import importlib
from io import BytesIO
from typing import Any

import pytest
from PIL import Image

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry

REPORT_HEADER_RENDERERS = [
    ("bar_chart", "glass_3d", "neo_legend.bar_chart"),
    ("line_chart", "executive_trend", "neo_legend.line_chart"),
    ("combo_chart", "crystal_stream", "neo_legend.combo_chart"),
    ("radar_chart", "neon_glow", "neo_legend.radar_chart"),
    ("dual_radar_chart", "versus_battle", "neo_legend.dual_radar_chart"),
    ("bubble_chart", "water_drops", "neo_legend.bubble_chart"),
    ("sankey_chart", "neon_streams", "neo_legend.sankey_chart"),
    ("calendar_chart", "executive_month", "neo_legend.business_report_charts"),
    ("matrix_bubble_chart", "risk_heat_matrix", "neo_legend.business_report_charts"),
    ("chord_chart", "capital_flows", "neo_legend.business_report_charts"),
    ("scatter_matrix_chart", "macro_quadrants", "neo_legend.business_report_charts"),
    ("stacked_bar_chart", "wall_street_stack", "neo_legend.business_report_charts"),
]


@pytest.fixture
def registry():
    return build_default_registry()


@pytest.mark.parametrize(("legend_type", "style", "module_name"), REPORT_HEADER_RENDERERS)
def test_report_style_header_text_can_be_filled_from_request_fields(
    monkeypatch,
    registry,
    legend_type: str,
    style: str,
    module_name: str,
) -> None:
    captured: dict[str, str | None] = {}
    module = importlib.import_module(module_name)

    def capture_header(
        _canvas: Any,
        _theme: Any,
        title: str,
        subtitle: str | None,
        kicker: str,
        *,
        theme_label: str | None = None,
    ) -> None:
        captured["title"] = title
        captured["subtitle"] = subtitle
        captured["kicker"] = kicker
        captured["theme_label"] = theme_label

    def capture_footer(_canvas: Any, _theme: Any, text: str) -> None:
        captured["footer"] = text

    monkeypatch.setattr(module, "draw_report_header", capture_header)
    monkeypatch.setattr(module, "add_footer", capture_footer)

    result = registry.render(
        RenderRequest(
            legend_type=legend_type,
            style=style,
            width=700,
            height=700,
            title="Client Revenue Risk Review",
            subtitle="Q4 board package custom subtitle",
            kicker="Custom Top Label",
            theme_label="Client Executive Pack",
            footer="ACME CAPITAL | INTERNAL REPORT",
        )
    )

    assert Image.open(BytesIO(result.content)).format == "PNG"
    assert captured == {
        "title": "Client Revenue Risk Review",
        "subtitle": "Q4 board package custom subtitle",
        "kicker": "Custom Top Label",
        "theme_label": "Client Executive Pack",
        "footer": "ACME CAPITAL | INTERNAL REPORT",
    }


def test_report_header_text_can_be_filled_from_nested_data(monkeypatch, registry) -> None:
    captured: dict[str, str | None] = {}
    module = importlib.import_module("neo_legend.business_report_charts")

    def capture_header(
        _canvas: Any,
        _theme: Any,
        title: str,
        subtitle: str | None,
        kicker: str,
        *,
        theme_label: str | None = None,
    ) -> None:
        captured["title"] = title
        captured["subtitle"] = subtitle
        captured["kicker"] = kicker
        captured["theme_label"] = theme_label

    monkeypatch.setattr(module, "draw_report_header", capture_header)
    monkeypatch.setattr(module, "add_footer", lambda _canvas, _theme, text: captured.update({"footer": text}))

    result = registry.render(
        RenderRequest(
            legend_type="matrix_bubble_chart",
            style="risk_heat_matrix",
            width=700,
            height=700,
            data={
                "report_header": {
                    "title": "Nested Correlation Audit",
                    "subtitle": "Filled from data.report_header",
                    "kicker": "Nested Kicker",
                    "theme_label": "Nested Theme Label",
                    "footer": "NESTED FOOTER",
                }
            },
        )
    )

    assert Image.open(BytesIO(result.content)).format == "PNG"
    assert captured == {
        "title": "Nested Correlation Audit",
        "subtitle": "Filled from data.report_header",
        "kicker": "Nested Kicker",
        "theme_label": "Nested Theme Label",
        "footer": "NESTED FOOTER",
    }


def test_get_render_accepts_report_header_text_query(client) -> None:
    response = client.get(
        "/render",
        params={
            "legend_type": "matrix_bubble_chart",
            "style": "risk_heat_matrix",
            "width": 700,
            "height": 700,
            "title": "API Header Title",
            "subtitle": "API Header Subtitle",
            "kicker": "API Kicker",
            "theme_label": "API Pack",
            "footer": "API FOOTER",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_direct_skill_render_uses_request_header_fields(monkeypatch) -> None:
    captured: dict[str, str | None] = {}
    module = importlib.import_module("neo_legend.business_report_charts")
    skill = module.MatrixBubbleChartSkill()

    def capture_header(
        _canvas: Any,
        _theme: Any,
        title: str,
        subtitle: str | None,
        kicker: str,
        *,
        theme_label: str | None = None,
    ) -> None:
        captured["title"] = title
        captured["subtitle"] = subtitle
        captured["kicker"] = kicker
        captured["theme_label"] = theme_label

    monkeypatch.setattr(module, "draw_report_header", capture_header)
    monkeypatch.setattr(module, "add_footer", lambda _canvas, _theme, text: captured.update({"footer": text}))

    result = skill.render(
        RenderRequest(
            legend_type="matrix_bubble_chart",
            style="risk_heat_matrix",
            width=700,
            height=700,
            title="Direct Skill Title",
            subtitle="Direct Skill Subtitle",
            kicker="Direct Skill Kicker",
            theme_label="Direct Skill Pack",
            footer="DIRECT SKILL FOOTER",
        )
    )

    assert Image.open(BytesIO(result.content)).format == "PNG"
    assert captured == {
        "title": "Direct Skill Title",
        "subtitle": "Direct Skill Subtitle",
        "kicker": "Direct Skill Kicker",
        "theme_label": "Direct Skill Pack",
        "footer": "DIRECT SKILL FOOTER",
    }


def test_all_registered_renderers_accept_report_header_text_fields(registry) -> None:
    for metadata in registry.list_types():
        result = registry.render(
            RenderRequest(
                legend_type=metadata.legend_type,
                style=metadata.default_style,
                width=700,
                height=700,
                title="Universal Title Audit",
                subtitle="Universal Subtitle Audit",
                kicker="Universal Kicker Audit",
                theme_label="Universal Pack Audit",
                footer="UNIVERSAL FOOTER AUDIT",
            )
        )

        assert result.content

from __future__ import annotations

import pytest

from neo_legend.errors import UnknownLegendTypeError
from neo_legend.models import RenderRequest


def test_registry_lists_all_readme_legend_types(registry) -> None:
    legend_types = {item.legend_type for item in registry.list_types()}

    assert legend_types == {
        "court_shot",
        "dual_court_shot",
        "court_shot_animation",
        "coordinate",
        "plus_minus_coordinate",
        "rose",
        "table",
    }


def test_registry_auto_selects_component_by_type(registry) -> None:
    request = RenderRequest(legend_type="court-shot", style="default", width=720, height=900)

    result = registry.render(request)

    assert result.legend_type == "court_shot"
    assert result.style == "terrain"
    assert result.media_type == "image/png"
    assert result.content.startswith(b"\x89PNG")


def test_registry_rejects_unknown_type(registry) -> None:
    with pytest.raises(UnknownLegendTypeError):
        registry.render(RenderRequest(legend_type="unknown", style="default"))

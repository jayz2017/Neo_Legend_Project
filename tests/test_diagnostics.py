from __future__ import annotations

from pathlib import Path

from neo_legend.diagnostics import (
    compare_to_references,
    image_metrics_from_bytes,
    reference_paths_for_style,
    tune_content_to_reference,
)
from neo_legend.models import RenderRequest


def test_metrics_comparison_and_tuning_pipeline(registry, tmp_path) -> None:
    result = registry.render(
        RenderRequest(legend_type="court_shot", style="terrain", width=720, height=900)
    )
    generated_path = tmp_path / "generated.png"
    generated_path.write_bytes(result.content)

    comparison = compare_to_references(
        generated_path,
        [Path.cwd() / "6f95be795cc16e2d3b0e0f6425e12353.jpg"],
    )
    tuned_content, tuning = tune_content_to_reference(
        result.content,
        result.media_type,
        comparison.generated_metrics,
        comparison.reference_metrics,
    )
    tuned_metrics = image_metrics_from_bytes(tuned_content)

    assert comparison.best_reference is not None
    assert tuned_metrics.width == 720
    assert tuned_metrics.height == 900
    assert "applied" in tuning


def test_reference_paths_do_not_fallback_for_known_style_without_refs() -> None:
    refs = reference_paths_for_style(
        project_root=Path.cwd(),
        styles=[
            {"name": "with_refs", "reference_images": ["a.png"]},
            {"name": "no_refs", "reference_images": []},
        ],
        style_name="no_refs",
    )

    assert refs == []

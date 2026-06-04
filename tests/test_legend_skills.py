from __future__ import annotations

from pathlib import Path

from neo_legend.registry import build_default_registry

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEGEND_SKILL_ROOT = PROJECT_ROOT / "legend_skills"


def test_every_registered_legend_has_project_skill() -> None:
    registry = build_default_registry()
    expected = {
        f"neo-legend-{metadata.legend_type.replace('_', '-')}"
        for metadata in registry.list_types()
    }
    actual = {path.name for path in LEGEND_SKILL_ROOT.iterdir() if path.is_dir()}

    assert actual == expected


def test_legend_skill_content_matches_renderer_metadata() -> None:
    registry = build_default_registry()
    index = (LEGEND_SKILL_ROOT / "INDEX.md").read_text(encoding="utf-8")

    for metadata in registry.list_types():
        skill_name = f"neo-legend-{metadata.legend_type.replace('_', '-')}"
        skill_path = LEGEND_SKILL_ROOT / skill_name / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")

        assert f"name: {skill_name}" in content
        assert f"`{metadata.legend_type}`" in content
        assert f"`{metadata.default_style}`" in content
        assert metadata.display_name in content
        assert skill_name in index
        for style in metadata.styles:
            assert f"`{style.name}`" in content

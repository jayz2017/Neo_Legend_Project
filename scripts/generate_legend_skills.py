"""Generate project-local Codex skills for every Neo Legend renderer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from neo_legend.registry import build_default_registry
from neo_legend.sample_data import sample_data_for

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "legend_skills"
SAMPLE_OUTPUT_ROOT = "G:/echaet"

SPECIAL_NOTES: dict[str, list[str]] = {
    "table": [
        "`header_groups` controls merged parent headers and child headers.",
        "`gradient_columns` or `gradients` controls average-centered cell color scaling.",
        "`left_image` or `left_image_path` composes an external image on the left side.",
    ],
    "court_shot": [
        "`points_location` expects scoring zones; higher accumulated points must render brighter.",
        "Use court geometry helpers in `src/neo_legend/_court.py` for shot placement changes.",
    ],
    "court_shot_animation": [
        "`sweep` must reveal shots cumulatively by data order, not by left-to-right masking.",
        "Keep GIF frame count, duration, and data progression readable before changing effects.",
    ],
    "points_location": [
        "Brightness must encode regional point density; dense areas should be visibly brighter.",
    ],
    "matrix_bubble_chart": [
        "Bubble size encodes absolute magnitude; color encodes direction.",
        "The report header supports `title`, `subtitle`, `kicker`, `theme_label`, and `footer`.",
    ],
}


@dataclass(frozen=True)
class RendererSpec:
    legend_type: str
    skill_name: str
    display_name: str
    default_style: str
    default_size: tuple[int, int]
    media_type: str
    extension: str
    module_path: Path
    class_name: str
    styles: list[tuple[str, str]]
    tests: list[Path]
    has_report_header: bool


def main() -> None:
    registry = build_default_registry()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    specs: list[RendererSpec] = []
    for metadata in registry.list_types():
        skill = registry.get(metadata.legend_type)
        spec = _build_spec(skill, metadata)
        specs.append(spec)
        _write_skill(spec)

    _write_index(specs)
    print(f"generated {len(specs)} legend skills in {OUTPUT_ROOT}")


def _build_spec(skill: Any, metadata: Any) -> RendererSpec:
    module_path = PROJECT_ROOT / "src" / Path(skill.__class__.__module__.replace(".", "/")).with_suffix(".py")
    source = module_path.read_text(encoding="utf-8")
    tests = _find_tests(metadata.legend_type)
    return RendererSpec(
        legend_type=metadata.legend_type,
        skill_name=f"neo-legend-{metadata.legend_type.replace('_', '-')}",
        display_name=metadata.display_name,
        default_style=metadata.default_style,
        default_size=skill.default_size,
        media_type=metadata.media_type,
        extension=skill.file_extension,
        module_path=module_path.relative_to(PROJECT_ROOT),
        class_name=skill.__class__.__name__,
        styles=[(style.name, style.description) for style in metadata.styles],
        tests=tests,
        has_report_header="draw_report_header(" in source,
    )


def _find_tests(legend_type: str) -> list[Path]:
    tests_dir = PROJECT_ROOT / "tests"
    matches: list[Path] = []
    if not tests_dir.exists():
        return matches
    for path in sorted(tests_dir.glob("test_*.py")):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(errors="ignore")
        if legend_type in text:
            matches.append(path.relative_to(PROJECT_ROOT))
    return matches


def _write_skill(spec: RendererSpec) -> None:
    skill_dir = OUTPUT_ROOT / spec.skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "agents").mkdir(exist_ok=True)
    (skill_dir / "SKILL.md").write_text(_skill_markdown(spec), encoding="utf-8")
    (skill_dir / "agents" / "openai.yaml").write_text(_openai_yaml(spec), encoding="utf-8")


def _skill_markdown(spec: RendererSpec) -> str:
    style_rows = "\n".join(
        f"| `{name}` | {description} | `{SAMPLE_OUTPUT_ROOT}/{spec.legend_type}__{name}.{spec.extension}` |"
        for name, description in spec.styles
    )
    data_sections = "\n\n".join(_data_contract_sections(spec))
    tests = "\n".join(f"- `{path.as_posix()}`" for path in spec.tests) or "- No direct test file found; add one before risky changes."
    notes = "\n".join(f"- {note}" for note in SPECIAL_NOTES.get(spec.legend_type, [])) or "- Keep visual changes scoped to this renderer unless shared helpers are required."
    header_fields = (
        "- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`.\n"
        if spec.has_report_header
        else "- Header fields: `title` and `subtitle` are the primary text overrides for this renderer.\n"
    )
    return f"""---
name: {spec.skill_name}
description: >-
  Maintain and tune the Neo Legend `{spec.legend_type}` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
---

# {spec.display_name}

## Renderer Contract

- Legend type: `{spec.legend_type}`
- Renderer class: `{spec.class_name}`
- Source file: `{spec.module_path.as_posix()}`
- Default style: `{spec.default_style}`
- Default size: `{spec.default_size[0]}x{spec.default_size[1]}`
- Media type: `{spec.media_type}`
{header_fields}
## Supported Styles

| Style | Intent | Current sample output |
| --- | --- | --- |
{style_rows}

## Data Contract

{data_sections}

## Modification Workflow

1. Treat this Skill as the product-level spec for `{spec.legend_type}`.
2. Read `{spec.module_path.as_posix()}` only after this Skill does not answer the change.
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`.
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values.
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference.
6. Update this Skill when a new input field, theme, style, or layout rule is added.

## Tuning Notes

{notes}

## Validation

- Run focused render tests for this renderer first.
- Run `python -m pytest tests/test_report_header_text.py -q` when changing report headers.
- Run `python -m pytest -q` before considering the change complete.
- Regenerate all outputs with:

```powershell
$env:PYTHONPATH='src'; python -m neo_legend.batch_generate --output-dir G:\\echaet --project-root E:\\haochenkeji\\Neo_Legend_Project
```

## Related Tests

{tests}
"""


def _data_contract_sections(spec: RendererSpec) -> list[str]:
    sections: list[str] = []
    for style, _description in spec.styles:
        data = sample_data_for(spec.legend_type, style)
        lines = _summarize_data(data)
        if not lines:
            lines = ["- No required custom data; renderer can synthesize defaults."]
        sections.append(f"### `{style}`\n" + "\n".join(lines))
    return sections


def _summarize_data(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key, value in sorted(data.items()):
        lines.append(f"- `{key}`: {_describe_value(value)}")
    return lines


def _describe_value(value: Any) -> str:
    if isinstance(value, list):
        if not value:
            return "empty list"
        first = value[0]
        if isinstance(first, dict):
            keys = ", ".join(sorted(str(key) for key in first))
            return f"list[{len(value)}] of objects with keys: {keys}"
        return f"list[{len(value)}]"
    if isinstance(value, dict):
        keys = ", ".join(sorted(str(key) for key in value))
        return f"object with keys: {keys}" if keys else "object"
    return f"{type(value).__name__} value `{value}`"


def _openai_yaml(spec: RendererSpec) -> str:
    display_name = f"Neo Legend {spec.display_name}"
    short_description = f"Tune `{spec.legend_type}` chart styling and data rules."
    default_prompt = f"Use ${spec.skill_name} to tune the Neo Legend `{spec.legend_type}` renderer."
    return f"""interface:
  display_name: "{_yaml_quote(display_name)}"
  short_description: "{_yaml_quote(short_description)}"
  default_prompt: "{_yaml_quote(default_prompt)}"
policy:
  allow_implicit_invocation: true
"""


def _write_index(specs: list[RendererSpec]) -> None:
    rows = "\n".join(
        f"| `{spec.legend_type}` | `{spec.skill_name}` | `{spec.default_style}` | `{spec.module_path.as_posix()}` |"
        for spec in specs
    )
    content = f"""# Neo Legend Skill Index

Generated on {date.today().isoformat()} from the current renderer registry.

| Legend type | Skill | Default style | Source |
| --- | --- | --- | --- |
{rows}

Use the matching Skill first when changing a chart. Update both the Skill and renderer code when a visual rule, input field, theme, or data contract changes.
"""
    (OUTPUT_ROOT / "INDEX.md").write_text(content, encoding="utf-8")


def _yaml_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    main()

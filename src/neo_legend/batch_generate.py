"""Batch generation, logging, and visual comparison workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from neo_legend.diagnostics import (
    compare_to_references,
    image_metrics_from_path,
    reference_paths_for_style,
    tune_content_to_reference,
)
from neo_legend.registry import LegendRegistry, build_default_registry
from neo_legend.sample_data import build_sample_request, summarize_sample_data

DEFAULT_OUTPUT_DIR = Path(r"G:\echaet")


def generate_all(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    project_root: Path | None = None,
    registry: LegendRegistry | None = None,
) -> dict[str, Any]:
    """Generate every style, write images/logs, and return a summary report."""

    project_root = project_root or Path.cwd()
    registry = registry or build_default_registry()
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    logs_dir = output_dir / "logs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    events: list[dict[str, Any]] = []
    jsonl_path = logs_dir / "render_events.jsonl"
    if jsonl_path.exists():
        jsonl_path.unlink()

    for metadata in registry.list_types():
        skill = registry.get(metadata.legend_type)
        styles = [style.model_dump() for style in metadata.styles]
        for style in metadata.styles:
            request = build_sample_request(skill, style.name)
            result = registry.render(request)
            base_name = f"{metadata.legend_type}__{style.name}.{result.file_extension}"
            raw_path = raw_dir / base_name
            final_path = output_dir / base_name
            raw_path.write_bytes(result.content)

            reference_paths = reference_paths_for_style(
                project_root=project_root,
                styles=styles,
                style_name=style.name,
            )
            initial_comparison = compare_to_references(raw_path, reference_paths)
            if request.data.get("_resolved_luxury_theme"):
                tuned_content = result.content
                tuning = {
                    "applied": False,
                    "reason": "luxury_theme_preserved",
                    "theme": request.data["_resolved_luxury_theme"],
                }
            else:
                tuned_content, tuning = tune_content_to_reference(
                    result.content,
                    result.media_type,
                    initial_comparison.generated_metrics,
                    initial_comparison.reference_metrics,
                )
            final_path.write_bytes(tuned_content)
            final_metrics = image_metrics_from_path(final_path)
            final_comparison = compare_to_references(final_path, reference_paths)
            if _score_worse(final_comparison.to_dict(), initial_comparison.to_dict()):
                final_path.write_bytes(result.content)
                final_metrics = image_metrics_from_path(final_path)
                final_comparison = initial_comparison
                tuning = {
                    "applied": False,
                    "reason": "score_not_improved",
                    "candidate": tuning,
                }

            event = {
                "legend_type": metadata.legend_type,
                "display_name": metadata.display_name,
                "style": style.name,
                "media_type": result.media_type,
                "request": request.model_dump(),
                "data_summary": summarize_sample_data(request.data),
                "paths": {
                    "raw": str(raw_path),
                    "final": str(final_path),
                    "references": [str(path) for path in reference_paths if path.exists()],
                },
                "initial_comparison": initial_comparison.to_dict(),
                "final_metrics": final_metrics.to_dict(),
                "final_comparison": final_comparison.to_dict(),
                "tuning": tuning,
            }
            events.append(event)
            _append_jsonl(jsonl_path, event)

    report = _build_report(events, output_dir)
    (logs_dir / "comparison_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (logs_dir / "tuning_report.md").write_text(_render_markdown_report(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Neo Legend sample images and logs.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--project-root", default=str(Path.cwd()))
    args = parser.parse_args()

    report = generate_all(output_dir=Path(args.output_dir), project_root=Path(args.project_root))
    print(
        json.dumps(
            {
                "output_dir": report["output_dir"],
                "image_count": report["image_count"],
                "log_dir": report["log_dir"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def _append_jsonl(path: Path, event: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def _build_report(events: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    scores = [
        event["final_comparison"]["score"]
        for event in events
        if event["final_comparison"]["score"] is not None
    ]
    return {
        "output_dir": str(output_dir),
        "log_dir": str(output_dir / "logs"),
        "image_count": len(events),
        "raw_image_dir": str(output_dir / "raw"),
        "average_score": round(sum(scores) / len(scores), 5) if scores else None,
        "events": events,
    }


def _score_worse(final_comparison: dict[str, Any], initial_comparison: dict[str, Any]) -> bool:
    final_score = final_comparison.get("score")
    initial_score = initial_comparison.get("score")
    if final_score is None or initial_score is None:
        return False
    return float(final_score) > float(initial_score)


def _render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Neo Legend 图像生成与调参报告",
        "",
        f"- 输出目录: `{report['output_dir']}`",
        f"- 原始图目录: `{report['raw_image_dir']}`",
        f"- 日志目录: `{report['log_dir']}`",
        f"- 生成图片数量: {report['image_count']}",
        f"- 平均比对分数: {report['average_score']}",
        "",
        "| 图例类型 | 样式 | 参考图 | 分数 | 自动调整 | 建议 |",
        "|---|---|---|---:|---|---|",
    ]
    for event in report["events"]:
        comparison = event["final_comparison"]
        tuning = event["tuning"]
        recommendations = "<br>".join(comparison["recommendations"])
        lines.append(
            "| {legend_type} | {style} | {reference} | {score} | {tuning} | {recommendations} |".format(
                legend_type=event["legend_type"],
                style=event["style"],
                reference=comparison["best_reference"] or "无",
                score=comparison["score"] if comparison["score"] is not None else "N/A",
                tuning="已应用" if tuning.get("applied") else "未应用",
                recommendations=recommendations,
            )
        )
    lines.append("")
    lines.append("## 日志字段说明")
    lines.append("")
    lines.append("- `render_events.jsonl`: 每行对应一次图例生成，包含请求参数、模拟数据摘要、路径、初始比对、最终比对和自动调参因子。")
    lines.append("- `comparison_report.json`: 汇总全部样式的结构化报告，适合后续程序读取。")
    lines.append("- `tuning_report.md`: 面向人工微调的报告，列出每种图例的参考图、分数和调整建议。")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()

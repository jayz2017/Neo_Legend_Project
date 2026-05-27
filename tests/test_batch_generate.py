from __future__ import annotations

import json
from pathlib import Path

from neo_legend.batch_generate import generate_all
from neo_legend.registry import build_default_registry


def test_generate_all_writes_images_logs_and_reports(tmp_path) -> None:
    report = generate_all(output_dir=tmp_path, project_root=Path.cwd())
    expected_count = sum(len(item.styles) for item in build_default_registry().list_types())

    assert report["image_count"] == expected_count
    assert (tmp_path / "court_shot__terrain.png").exists()
    assert (tmp_path / "court_shot__points_location.png").exists()
    assert (tmp_path / "court_shot__kobe_shots.png").exists()
    assert (tmp_path / "court_shot_animation__arena_arc.gif").exists()
    assert (tmp_path / "raw" / "court_shot__terrain.png").exists()
    assert (tmp_path / "logs" / "render_events.jsonl").exists()
    assert (tmp_path / "logs" / "comparison_report.json").exists()
    assert (tmp_path / "logs" / "tuning_report.md").exists()

    lines = (tmp_path / "logs" / "render_events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == report["image_count"]
    first_event = json.loads(lines[0])
    assert {"request", "data_summary", "initial_comparison", "final_comparison", "tuning"} <= set(
        first_event
    )

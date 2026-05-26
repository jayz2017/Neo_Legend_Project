"""FastAPI application for rendering legend graphics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from neo_legend.batch_generate import generate_all
from neo_legend.errors import UnknownLegendTypeError, UnknownStyleError
from neo_legend.models import (
    BatchGenerateRequest,
    BatchGenerateSummary,
    LegendTypeInfo,
    RenderRequest,
    RenderResult,
)
from neo_legend.registry import build_default_registry

app = FastAPI(
    title="Neo Legend Renderer",
    version="0.1.0",
    description="Render NBA-style legend graphics from type and style parameters.",
)
registry = build_default_registry()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/legend-types", response_model=list[LegendTypeInfo])
def legend_types() -> list[LegendTypeInfo]:
    return registry.list_types()


@app.get("/render")
def render_preview(
    legend_type: str = Query(..., description="Legend type, for example court_shot."),
    style: str = Query("default", description="Style variant, for example terrain."),
    title: str | None = Query(None),
    subtitle: str | None = Query(None),
    width: int = Query(1179, ge=640, le=2400),
    height: int | None = Query(None, ge=640, le=3200),
) -> Response:
    request = RenderRequest(
        legend_type=legend_type,
        style=style,
        title=title,
        subtitle=subtitle,
        width=width,
        height=height,
    )
    return _render_response(request)


@app.post("/render")
def render_from_body(request: RenderRequest) -> Response:
    return _render_response(request)


@app.post("/batch-generate", response_model=BatchGenerateSummary)
def batch_generate(request: BatchGenerateRequest) -> BatchGenerateSummary:
    project_root = Path(request.project_root) if request.project_root else Path.cwd()
    report = generate_all(output_dir=Path(request.output_dir), project_root=project_root)
    return BatchGenerateSummary(
        output_dir=report["output_dir"],
        log_dir=report["log_dir"],
        raw_image_dir=report["raw_image_dir"],
        image_count=report["image_count"],
        average_score=report["average_score"],
    )


def _render_response(request: RenderRequest) -> Response:
    result = _render_or_http_error(request)
    filename = f"{result.legend_type}-{result.style}.{result.file_extension}"
    headers = {
        "Content-Disposition": f'inline; filename="{filename}"',
        "X-Legend-Type": result.legend_type,
        "X-Legend-Style": result.style,
    }
    return Response(content=result.content, media_type=result.media_type, headers=headers)


def _render_or_http_error(request: RenderRequest) -> RenderResult:
    try:
        return registry.render(request)
    except UnknownLegendTypeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnknownStyleError as exc:
        detail: dict[str, Any] = {
            "message": str(exc),
            "legend_type": exc.legend_type,
            "style": exc.style,
            "allowed_styles": exc.allowed_styles,
        }
        raise HTTPException(status_code=400, detail=detail) from exc

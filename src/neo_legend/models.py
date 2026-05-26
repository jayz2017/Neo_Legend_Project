"""Pydantic models and render result contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field, field_validator


class RenderRequest(BaseModel):
    """Input contract for rendering any legend graphic."""

    legend_type: str = Field(..., min_length=1, description="Legend type to render.")
    style: str = Field("default", min_length=1, description="Style variant for the legend type.")
    title: str | None = Field(None, description="Optional title override.")
    subtitle: str | None = Field(None, description="Optional subtitle override.")
    data: dict[str, Any] = Field(default_factory=dict, description="Renderer-specific data.")
    width: int = Field(1179, ge=640, le=2400, description="Output width in pixels.")
    height: int | None = Field(None, ge=640, le=3200, description="Output height in pixels.")

    @field_validator("legend_type", "style")
    @classmethod
    def normalize_token(cls, value: str) -> str:
        return value.strip().lower().replace("-", "_")


class LegendStyleInfo(BaseModel):
    """Public style metadata for a renderer skill."""

    name: str
    description: str
    reference_images: list[str] = Field(default_factory=list)


class LegendTypeInfo(BaseModel):
    """Public metadata for a registered legend renderer."""

    legend_type: str
    display_name: str
    default_style: str
    styles: list[LegendStyleInfo]
    media_type: str


class BatchGenerateRequest(BaseModel):
    """Input contract for generating every built-in sample image."""

    output_dir: str = Field(r"G:\echaet", min_length=1, description="Directory for generated images.")
    project_root: str | None = Field(
        None,
        description="Project root containing README reference images. Defaults to current working directory.",
    )


class BatchGenerateSummary(BaseModel):
    """Small response model for batch generation."""

    output_dir: str
    log_dir: str
    raw_image_dir: str
    image_count: int
    average_score: float | None


@dataclass(frozen=True)
class RenderResult:
    """Bytes and response metadata produced by a renderer."""

    content: bytes
    media_type: str
    file_extension: str
    legend_type: str
    style: str

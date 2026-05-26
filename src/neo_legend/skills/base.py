"""Base classes for independent renderer skills."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from neo_legend.errors import UnknownStyleError
from neo_legend.models import LegendStyleInfo, LegendTypeInfo, RenderRequest, RenderResult


@dataclass(frozen=True)
class StyleDefinition:
    """Supported style metadata for a renderer skill."""

    name: str
    description: str
    reference_images: tuple[str, ...] = ()


class BaseLegendSkill(ABC):
    """Common contract for all renderer skills."""

    legend_type: ClassVar[str]
    display_name: ClassVar[str]
    default_style: ClassVar[str]
    default_size: ClassVar[tuple[int, int]] = (1179, 1454)
    media_type: ClassVar[str] = "image/png"
    file_extension: ClassVar[str] = "png"
    style_definitions: ClassVar[tuple[StyleDefinition, ...]]

    def metadata(self) -> LegendTypeInfo:
        return LegendTypeInfo(
            legend_type=self.legend_type,
            display_name=self.display_name,
            default_style=self.default_style,
            styles=[
                LegendStyleInfo(
                    name=style.name,
                    description=style.description,
                    reference_images=list(style.reference_images),
                )
                for style in self.style_definitions
            ],
            media_type=self.media_type,
        )

    def resolve_style(self, style: str | None) -> str:
        normalized = (style or self.default_style).strip().lower().replace("-", "_")
        if normalized == "default":
            normalized = self.default_style

        allowed_styles = [style_definition.name for style_definition in self.style_definitions]
        if normalized not in allowed_styles:
            raise UnknownStyleError(self.legend_type, normalized, allowed_styles)
        return normalized

    def output_size(self, request: RenderRequest) -> tuple[int, int]:
        return request.width, request.height or self.default_size[1]

    def result(self, content: bytes, style: str) -> RenderResult:
        return RenderResult(
            content=content,
            media_type=self.media_type,
            file_extension=self.file_extension,
            legend_type=self.legend_type,
            style=style,
        )

    @abstractmethod
    def render(self, request: RenderRequest) -> RenderResult:
        """Render an image for the request."""

"""Shared luxury visual themes applied across renderer outputs."""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass
from io import BytesIO
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageSequence

from neo_legend.models import RenderResult


@dataclass(frozen=True)
class LuxuryTheme:
    name: str
    display_name: str
    description: str
    brightness: float
    contrast: float
    saturation: float
    sharpness: float
    shadow_tint: str
    highlight_tint: str
    shadow_strength: float
    highlight_strength: float
    vignette_strength: float
    border_color: str
    border_width_ratio: float


LUXURY_THEMES: dict[str, LuxuryTheme] = {
    "obsidian_gold": LuxuryTheme(
        name="obsidian_gold",
        display_name="Obsidian Gold",
        description="Deep contrast with restrained warm-gold highlights.",
        brightness=1.01,
        contrast=1.12,
        saturation=1.08,
        sharpness=1.10,
        shadow_tint="#07090d",
        highlight_tint="#ffd27a",
        shadow_strength=0.040,
        highlight_strength=0.035,
        vignette_strength=0.045,
        border_color="#c9a85d",
        border_width_ratio=0.004,
    ),
    "champagne_ivory": LuxuryTheme(
        name="champagne_ivory",
        display_name="Champagne Ivory",
        description="Clean bright surface with subtle champagne warmth.",
        brightness=1.03,
        contrast=1.08,
        saturation=1.04,
        sharpness=1.08,
        shadow_tint="#352716",
        highlight_tint="#fff1cf",
        shadow_strength=0.018,
        highlight_strength=0.020,
        vignette_strength=0.018,
        border_color="#d8bd7a",
        border_width_ratio=0.003,
    ),
    "sapphire_platinum": LuxuryTheme(
        name="sapphire_platinum",
        display_name="Sapphire Platinum",
        description="Crisp cool shadows with polished platinum highlights.",
        brightness=1.02,
        contrast=1.10,
        saturation=1.06,
        sharpness=1.12,
        shadow_tint="#061b36",
        highlight_tint="#dcecff",
        shadow_strength=0.032,
        highlight_strength=0.026,
        vignette_strength=0.035,
        border_color="#a9c6df",
        border_width_ratio=0.0035,
    ),
    "emerald_onyx": LuxuryTheme(
        name="emerald_onyx",
        display_name="Emerald Onyx",
        description="Elegant teal-green depth with polished contrast.",
        brightness=1.01,
        contrast=1.11,
        saturation=1.08,
        sharpness=1.10,
        shadow_tint="#061d18",
        highlight_tint="#c7f2dc",
        shadow_strength=0.030,
        highlight_strength=0.025,
        vignette_strength=0.034,
        border_color="#54b891",
        border_width_ratio=0.0035,
    ),
    "ruby_noir": LuxuryTheme(
        name="ruby_noir",
        display_name="Ruby Noir",
        description="Refined ruby accents with strong black-level separation.",
        brightness=1.01,
        contrast=1.13,
        saturation=1.07,
        sharpness=1.11,
        shadow_tint="#211018",
        highlight_tint="#ffd5dd",
        shadow_strength=0.034,
        highlight_strength=0.026,
        vignette_strength=0.040,
        border_color="#c95770",
        border_width_ratio=0.0035,
    ),
}

THEME_ALIASES = {
    "gold": "obsidian_gold",
    "ivory": "champagne_ivory",
    "champagne": "champagne_ivory",
    "sapphire": "sapphire_platinum",
    "emerald": "emerald_onyx",
    "ruby": "ruby_noir",
}

OFF_VALUES = {"", "none", "off", "false", "disabled", "disable"}


def luxury_theme_metadata() -> list[dict[str, Any]]:
    """Return theme metadata for API discovery."""

    return [asdict(theme) for theme in LUXURY_THEMES.values()]


def apply_luxury_theme(result: RenderResult, data: dict[str, Any]) -> RenderResult:
    """Apply a requested luxury theme to a rendered image result."""

    theme = resolve_luxury_theme(data)
    if theme is None or not result.media_type.startswith("image/"):
        return result

    intensity = _theme_intensity(data)
    if result.media_type == "image/gif":
        content = _theme_gif(result.content, theme, intensity)
    else:
        content = _theme_static_image(result.content, theme, intensity)

    return RenderResult(
        content=content,
        media_type=result.media_type,
        file_extension=result.file_extension,
        legend_type=result.legend_type,
        style=result.style,
    )


def resolve_luxury_theme(data: dict[str, Any]) -> LuxuryTheme | None:
    """Resolve configured theme and record the concrete selection in the data payload."""

    requested = str(data.get("luxury_theme", data.get("visual_theme", ""))).strip().lower()
    if requested in OFF_VALUES:
        return None
    if requested == "random":
        theme_names = sorted(LUXURY_THEMES)
        seed = data.get("luxury_theme_seed", data.get("theme_seed"))
        rng = random.Random(str(seed)) if seed is not None else random.SystemRandom()
        requested = rng.choice(theme_names)

    requested = THEME_ALIASES.get(requested, requested)
    theme = LUXURY_THEMES.get(requested)
    if theme is None:
        return None

    data["_resolved_luxury_theme"] = theme.name
    return _theme_with_overrides(theme, data.get("luxury_theme_overrides"))


def _theme_with_overrides(theme: LuxuryTheme, overrides: Any) -> LuxuryTheme:
    if not isinstance(overrides, dict):
        return theme
    values = asdict(theme)
    for key, value in overrides.items():
        if key not in values:
            continue
        if isinstance(values[key], float):
            numeric = _to_float(value)
            if numeric is not None:
                values[key] = numeric
        elif isinstance(value, str):
            values[key] = value
    return LuxuryTheme(**values)


def _theme_static_image(content: bytes, theme: LuxuryTheme, intensity: float) -> bytes:
    with Image.open(BytesIO(content)) as image:
        themed = _apply_theme_to_image(image.convert("RGB"), theme, intensity)
        buffer = BytesIO()
        themed.save(buffer, format="PNG")
        return buffer.getvalue()


def _theme_gif(content: bytes, theme: LuxuryTheme, intensity: float) -> bytes:
    with Image.open(BytesIO(content)) as image:
        frames = [
            _apply_theme_to_image(frame.convert("RGB"), theme, intensity)
            for frame in ImageSequence.Iterator(image)
        ]
        buffer = BytesIO()
        frames[0].save(
            buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=image.info.get("duration", 90),
            loop=image.info.get("loop", 0),
            disposal=2,
        )
        return buffer.getvalue()


def _apply_theme_to_image(image: Image.Image, theme: LuxuryTheme, intensity: float) -> Image.Image:
    image = ImageEnhance.Brightness(image).enhance(_factor(theme.brightness, intensity))
    image = ImageEnhance.Contrast(image).enhance(_factor(theme.contrast, intensity))
    image = ImageEnhance.Color(image).enhance(_factor(theme.saturation, intensity))
    image = ImageEnhance.Sharpness(image).enhance(_factor(theme.sharpness, intensity))
    image = _apply_tone_tints(image, theme, intensity)
    image = _apply_vignette(image, theme.vignette_strength * intensity)
    return _apply_border(image, theme, intensity)


def _apply_tone_tints(image: Image.Image, theme: LuxuryTheme, intensity: float) -> Image.Image:
    arr = np.asarray(image).astype(np.float32) / 255.0
    luma = arr[:, :, 0] * 0.2126 + arr[:, :, 1] * 0.7152 + arr[:, :, 2] * 0.0722
    shadow_mask = np.clip((0.58 - luma) / 0.58, 0, 1)[:, :, None]
    highlight_mask = np.clip((luma - 0.56) / 0.44, 0, 1)[:, :, None]
    shadow_strength = theme.shadow_strength * intensity
    highlight_strength = theme.highlight_strength * intensity
    shadow_tint = np.array(_hex_to_rgb(theme.shadow_tint), dtype=np.float32) / 255.0
    highlight_tint = np.array(_hex_to_rgb(theme.highlight_tint), dtype=np.float32) / 255.0

    arr = arr * (1 - shadow_mask * shadow_strength) + shadow_tint * shadow_mask * shadow_strength
    arr = arr * (1 - highlight_mask * highlight_strength) + highlight_tint * highlight_mask * highlight_strength
    return Image.fromarray(np.uint8(np.clip(arr, 0, 1) * 255), mode="RGB")


def _apply_vignette(image: Image.Image, strength: float) -> Image.Image:
    if strength <= 0:
        return image
    width, height = image.size
    y, x = np.ogrid[-1:1 : complex(height), -1:1 : complex(width)]
    distance = np.clip(np.sqrt(x * x + y * y), 0, 1)
    mask = 1 - distance[:, :, None] * strength
    arr = np.asarray(image).astype(np.float32) / 255.0
    themed = np.clip(arr * mask, 0, 1)
    return Image.fromarray(np.uint8(themed * 255), mode="RGB")


def _apply_border(image: Image.Image, theme: LuxuryTheme, intensity: float) -> Image.Image:
    width, height = image.size
    border_width = max(int(min(width, height) * theme.border_width_ratio * intensity), 1)
    draw = ImageDraw.Draw(image)
    color = _hex_to_rgb(theme.border_color)
    for offset in range(border_width):
        draw.rectangle(
            [offset, offset, width - 1 - offset, height - 1 - offset],
            outline=color,
        )
    return image


def _factor(value: float, intensity: float) -> float:
    return 1.0 + (value - 1.0) * intensity


def _theme_intensity(data: dict[str, Any]) -> float:
    return float(np.clip(_to_float(data.get("luxury_theme_intensity")) or 1.0, 0.0, 2.0))


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) != 6:
        return 255, 255, 255
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)

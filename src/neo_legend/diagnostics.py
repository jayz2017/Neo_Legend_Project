"""Image diagnostics, comparison, and automatic post-render tuning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageEnhance, ImageSequence


@dataclass(frozen=True)
class ImageMetrics:
    """Loggable image-level metrics used for visual tuning."""

    width: int
    height: int
    frame_count: int
    aspect_ratio: float
    mean_luma: float
    contrast: float
    saturation: float
    edge_density: float
    foreground_ratio: float
    dominant_colors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ComparisonResult:
    """Comparison details between one generated image and reference images."""

    best_reference: str | None
    score: float | None
    generated_metrics: ImageMetrics
    reference_metrics: ImageMetrics | None
    deltas: dict[str, float]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "best_reference": self.best_reference,
            "score": self.score,
            "generated_metrics": self.generated_metrics.to_dict(),
            "reference_metrics": self.reference_metrics.to_dict()
            if self.reference_metrics is not None
            else None,
            "deltas": self.deltas,
            "recommendations": self.recommendations,
        }


def image_metrics_from_path(path: Path) -> ImageMetrics:
    with Image.open(path) as image:
        return image_metrics(image)


def image_metrics_from_bytes(content: bytes) -> ImageMetrics:
    with Image.open(BytesIO(content)) as image:
        return image_metrics(image)


def image_metrics(image: Image.Image) -> ImageMetrics:
    """Compute stable visual metrics from the first frame of an image."""

    frame_count = getattr(image, "n_frames", 1)
    image.seek(0)
    rgb = image.convert("RGB")
    width, height = rgb.size
    sampled = rgb.copy()
    sampled.thumbnail((384, 384))
    arr = np.asarray(sampled).astype(np.float32) / 255.0
    luma = arr[:, :, 0] * 0.2126 + arr[:, :, 1] * 0.7152 + arr[:, :, 2] * 0.0722
    max_rgb = arr.max(axis=2)
    min_rgb = arr.min(axis=2)
    saturation = np.divide(max_rgb - min_rgb, max_rgb + 1e-6).mean()
    edge_density = _edge_density(luma)
    foreground_ratio = _foreground_ratio(arr)

    return ImageMetrics(
        width=width,
        height=height,
        frame_count=frame_count,
        aspect_ratio=round(width / height, 5),
        mean_luma=round(float(luma.mean()), 5),
        contrast=round(float(luma.std()), 5),
        saturation=round(float(saturation), 5),
        edge_density=round(float(edge_density), 5),
        foreground_ratio=round(float(foreground_ratio), 5),
        dominant_colors=_dominant_colors(rgb),
    )


def compare_to_references(generated_path: Path, reference_paths: list[Path]) -> ComparisonResult:
    generated_metrics = image_metrics_from_path(generated_path)
    available_refs = [path for path in reference_paths if path.exists()]
    if not available_refs:
        return ComparisonResult(
            best_reference=None,
            score=None,
            generated_metrics=generated_metrics,
            reference_metrics=None,
            deltas={},
            recommendations=["未找到该样式的参考图，保留原始渲染结果。"],
        )

    scored: list[tuple[float, Path, ImageMetrics, dict[str, float]]] = []
    for ref_path in available_refs:
        ref_metrics = image_metrics_from_path(ref_path)
        deltas = metric_deltas(generated_metrics, ref_metrics)
        scored.append((_score_deltas(deltas), ref_path, ref_metrics, deltas))

    score, best_reference, ref_metrics, deltas = min(scored, key=lambda item: item[0])
    return ComparisonResult(
        best_reference=str(best_reference),
        score=round(score, 5),
        generated_metrics=generated_metrics,
        reference_metrics=ref_metrics,
        deltas=deltas,
        recommendations=_recommendations(deltas),
    )


def metric_deltas(generated: ImageMetrics, reference: ImageMetrics) -> dict[str, float]:
    return {
        "aspect_ratio": round(generated.aspect_ratio - reference.aspect_ratio, 5),
        "mean_luma": round(generated.mean_luma - reference.mean_luma, 5),
        "contrast": round(generated.contrast - reference.contrast, 5),
        "saturation": round(generated.saturation - reference.saturation, 5),
        "edge_density": round(generated.edge_density - reference.edge_density, 5),
        "foreground_ratio": round(generated.foreground_ratio - reference.foreground_ratio, 5),
    }


def tune_content_to_reference(
    content: bytes,
    media_type: str,
    generated_metrics: ImageMetrics,
    reference_metrics: ImageMetrics | None,
) -> tuple[bytes, dict[str, Any]]:
    """Apply conservative image-level tuning toward the best reference metrics."""

    if reference_metrics is None:
        return content, {"applied": False, "reason": "no_reference"}

    factors = {
        "brightness": _bounded_ratio(reference_metrics.mean_luma, generated_metrics.mean_luma),
        "contrast": _bounded_ratio(reference_metrics.contrast, generated_metrics.contrast),
        "saturation": _bounded_ratio(reference_metrics.saturation, generated_metrics.saturation),
    }
    if all(abs(value - 1.0) < 0.02 for value in factors.values()):
        return content, {"applied": False, "reason": "already_close", "factors": factors}

    if media_type == "image/gif":
        tuned = _tune_gif(content, factors)
    else:
        tuned = _tune_static_image(content, factors)
    return tuned, {"applied": True, "factors": factors}


def reference_paths_for_style(
    *,
    project_root: Path,
    styles: list[dict[str, Any]],
    style_name: str,
) -> list[Path]:
    """Resolve reference image paths for a style, falling back to any sibling references."""

    requested_refs: list[str] = []
    fallback_refs: list[str] = []
    matched_style = False
    for style in styles:
        refs = list(style.get("reference_images") or [])
        if style.get("name") == style_name:
            matched_style = True
            requested_refs.extend(refs)
        fallback_refs.extend(refs)

    refs = requested_refs if matched_style else fallback_refs
    return [project_root / ref for ref in refs]


def _score_deltas(deltas: dict[str, float]) -> float:
    weights = {
        "aspect_ratio": 0.40,
        "mean_luma": 1.10,
        "contrast": 0.90,
        "saturation": 0.70,
        "edge_density": 0.80,
        "foreground_ratio": 0.80,
    }
    return sum(abs(deltas[key]) * weight for key, weight in weights.items())


def _recommendations(deltas: dict[str, float]) -> list[str]:
    recommendations: list[str] = []
    if abs(deltas["aspect_ratio"]) > 0.03:
        recommendations.append("调整画布宽高比，使输出图与参考图更接近。")
    if deltas["mean_luma"] > 0.06:
        recommendations.append("整体亮度高于参考图，建议降低背景和文字亮度。")
    elif deltas["mean_luma"] < -0.06:
        recommendations.append("整体亮度低于参考图，建议提高主体元素亮度。")
    if deltas["contrast"] > 0.04:
        recommendations.append("对比度高于参考图，建议降低极亮/极暗区域差异。")
    elif deltas["contrast"] < -0.04:
        recommendations.append("对比度低于参考图，建议增强主体和背景分离。")
    if deltas["saturation"] > 0.05:
        recommendations.append("饱和度高于参考图，建议压低高饱和色彩。")
    elif deltas["saturation"] < -0.05:
        recommendations.append("饱和度低于参考图，建议增强关键热区或球队色。")
    if deltas["edge_density"] < -0.015:
        recommendations.append("细节密度低于参考图，建议增加点位、网格线或标签。")
    elif deltas["edge_density"] > 0.015:
        recommendations.append("细节密度高于参考图，建议减少过密点位或线条。")
    if not recommendations:
        recommendations.append("核心视觉指标已接近参考图，保留当前样式。")
    return recommendations


def _tune_static_image(content: bytes, factors: dict[str, float]) -> bytes:
    with Image.open(BytesIO(content)) as image:
        tuned = _apply_factors(image.convert("RGB"), factors)
        buffer = BytesIO()
        tuned.save(buffer, format="PNG")
        return buffer.getvalue()


def _tune_gif(content: bytes, factors: dict[str, float]) -> bytes:
    with Image.open(BytesIO(content)) as image:
        frames = [_apply_factors(frame.convert("RGB"), factors) for frame in ImageSequence.Iterator(image)]
        duration = image.info.get("duration", 90)
        loop = image.info.get("loop", 0)
        buffer = BytesIO()
        frames[0].save(
            buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=loop,
            disposal=2,
        )
        return buffer.getvalue()


def _apply_factors(image: Image.Image, factors: dict[str, float]) -> Image.Image:
    image = ImageEnhance.Brightness(image).enhance(factors["brightness"])
    image = ImageEnhance.Contrast(image).enhance(factors["contrast"])
    return ImageEnhance.Color(image).enhance(factors["saturation"])


def _bounded_ratio(target: float, current: float) -> float:
    if current <= 1e-6:
        return 1.0
    return round(float(np.clip(target / current, 0.75, 1.35)), 4)


def _edge_density(luma: np.ndarray) -> float:
    gx = np.abs(np.diff(luma, axis=1))
    gy = np.abs(np.diff(luma, axis=0))
    shared = gx[:-1, :] + gy[:, :-1]
    return float((shared > 0.18).mean())


def _foreground_ratio(arr: np.ndarray) -> float:
    corners = np.concatenate(
        [
            arr[:12, :12].reshape(-1, 3),
            arr[:12, -12:].reshape(-1, 3),
            arr[-12:, :12].reshape(-1, 3),
            arr[-12:, -12:].reshape(-1, 3),
        ],
        axis=0,
    )
    background = np.median(corners, axis=0)
    distance = np.linalg.norm(arr - background, axis=2)
    return float((distance > 0.08).mean())


def _dominant_colors(image: Image.Image) -> list[str]:
    sampled = image.copy()
    sampled.thumbnail((80, 80))
    palette = sampled.convert("P", palette=Image.Palette.ADAPTIVE, colors=6)
    colors = palette.getcolors(maxcolors=80 * 80) or []
    raw_palette = palette.getpalette() or []
    output: list[str] = []
    for _, index in sorted(colors, reverse=True)[:6]:
        offset = index * 3
        rgb = raw_palette[offset : offset + 3]
        output.append("#" + "".join(f"{component:02x}" for component in rgb))
    return output

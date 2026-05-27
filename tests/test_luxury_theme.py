from __future__ import annotations

from io import BytesIO

from PIL import Image

from neo_legend.luxury_theme import (
    LUXURY_THEMES,
    apply_luxury_theme,
    luxury_theme_metadata,
    resolve_luxury_theme,
)
from neo_legend.models import RenderRequest, RenderResult


def test_luxury_theme_metadata_lists_presets() -> None:
    names = {theme["name"] for theme in luxury_theme_metadata()}

    assert {"obsidian_gold", "champagne_ivory", "sapphire_platinum", "emerald_onyx", "ruby_noir"} <= names


def test_resolve_random_luxury_theme_is_seedable() -> None:
    first = {"luxury_theme": "random", "luxury_theme_seed": "stable"}
    second = {"luxury_theme": "random", "luxury_theme_seed": "stable"}

    assert resolve_luxury_theme(first) == resolve_luxury_theme(second)
    assert first["_resolved_luxury_theme"] == second["_resolved_luxury_theme"]


def test_apply_luxury_theme_changes_static_image() -> None:
    source = Image.new("RGB", (80, 80), "#6688aa")
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    result = RenderResult(
        content=buffer.getvalue(),
        media_type="image/png",
        file_extension="png",
        legend_type="test",
        style="default",
    )

    themed = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold"})

    assert themed.media_type == "image/png"
    assert themed.content != result.content
    assert Image.open(BytesIO(themed.content)).format == "PNG"


def test_apply_luxury_theme_keeps_gif_format(registry) -> None:
    result = registry.render(
        RenderRequest(
            legend_type="court_shot_animation",
            style="pulse",
            width=700,
            height=700,
            data={"luxury_theme": "ruby_noir", "frame_count": 2},
        )
    )

    assert result.media_type == "image/gif"
    assert Image.open(BytesIO(result.content)).format == "GIF"


# ==================== 主题别名解析测试 ====================

def test_resolve_gold_alias_to_obsidian_gold() -> None:
    """测试 gold 别名正确解析为 obsidian_gold"""
    data = {"luxury_theme": "gold"}
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.name == "obsidian_gold"
    assert data["_resolved_luxury_theme"] == "obsidian_gold"


def test_resolve_ivory_alias_to_champagne_ivory() -> None:
    """测试 ivory 别名正确解析为 champagne_ivory"""
    data = {"luxury_theme": "ivory"}
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.name == "champagne_ivory"


def test_resolve_sapphire_alias_to_sapphire_platinum() -> None:
    """测试 sapphire 别名正确解析为 sapphire_platinum"""
    data = {"luxury_theme": "sapphire"}
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.name == "sapphire_platinum"


def test_resolve_emerald_alias_to_emerald_onyx() -> None:
    """测试 emerald 别名正确解析为 emerald_onyx"""
    data = {"luxury_theme": "emerald"}
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.name == "emerald_onyx"


def test_resolve_ruby_alias_to_ruby_noir() -> None:
    """测试 ruby 别名正确解析为 ruby_noir"""
    data = {"luxury_theme": "ruby"}
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.name == "ruby_noir"


# ==================== Random 主题测试 ====================

def test_resolve_random_returns_valid_theme() -> None:
    """测试 random 主题返回有效的 LuxuryTheme 对象"""
    data = {"luxury_theme": "random", "luxury_theme_seed": "test_seed_123"}
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.name in LUXURY_THEMES
    assert "_resolved_luxury_theme" in data


# ==================== OFF 值测试 ====================

def test_resolve_empty_string_returns_none() -> None:
    """测试空字符串 "" 返回 None（关闭主题）"""
    data = {"luxury_theme": ""}
    assert resolve_luxury_theme(data) is None


def test_resolve_none_value_returns_none() -> None:
    """测试 "none" 值返回 None"""
    data = {"luxury_theme": "none"}
    assert resolve_luxury_theme(data) is None


def test_resolve_off_value_returns_none() -> None:
    """测试 "off" 值返回 None"""
    data = {"luxury_theme": "off"}
    assert resolve_luxury_theme(data) is None


def test_resolve_false_value_returns_none() -> None:
    """测试 "false" 值返回 None"""
    data = {"luxury_theme": "false"}
    assert resolve_luxury_theme(data) is None


# ==================== luxury_theme_intensity 参数测试 ====================

def test_intensity_zero_has_minimal_effect() -> None:
    """测试 intensity=0.0 时主题效果最弱，使用较大图片验证差异"""
    source = Image.new("RGB", (400, 400), "#6688aa")
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    original_content = buffer.getvalue()
    result = RenderResult(
        content=original_content,
        media_type="image/png",
        file_extension="png",
        legend_type="test",
        style="default",
    )

    zero_intensity = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold", "luxury_theme_intensity": 0.0})
    full_intensity = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold", "luxury_theme_intensity": 2.0})

    zero_image = Image.open(BytesIO(zero_intensity.content)).convert("RGB")
    full_image = Image.open(BytesIO(full_intensity.content)).convert("RGB")
    original_image = Image.open(BytesIO(original_content)).convert("RGB")

    zero_pixels = list(zero_image.getdata())
    full_pixels = list(full_image.getdata())
    original_pixels = list(original_image.getdata())

    zero_diff = sum(abs(a - b) for (r1, g1, b1), (r2, g2, b2) in zip(original_pixels, zero_pixels)
                    for a, b in [(r1, r2), (g1, g2), (b1, b2)]) / len(original_pixels)
    full_diff = sum(abs(a - b) for (r1, g1, b1), (r2, g2, b2) in zip(original_pixels, full_pixels)
                    for a, b in [(r1, r2), (g1, g2), (b1, b2)]) / len(original_pixels)

    assert zero_diff < full_diff, f"intensity=0.0 ({zero_diff:.2f}) 应小于 intensity=2.0 ({full_diff:.2f})"


def test_intensity_two_has_maximal_effect() -> None:
    """测试 intensity=2.0 时主题效果最强"""
    source = Image.new("RGB", (80, 80), "#6688aa")
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    result = RenderResult(
        content=buffer.getvalue(),
        media_type="image/png",
        file_extension="png",
        legend_type="test",
        style="default",
    )

    light = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold", "luxury_theme_intensity": 0.5})
    strong = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold", "luxury_theme_intensity": 2.0})

    assert strong.content != light.content


def test_default_intensity_is_one() -> None:
    """测试不指定 intensity 时默认值为 1.0"""
    source = Image.new("RGB", (80, 80), "#6688aa")
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    result = RenderResult(
        content=buffer.getvalue(),
        media_type="image/png",
        file_extension="png",
        legend_type="test",
        style="default",
    )

    default_themed = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold"})
    explicit_one = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold", "luxury_theme_intensity": 1.0})

    assert default_themed.content == explicit_one.content


# ==================== luxury_theme_overrides 参数测试 ====================

def test_overrides_single_property_brightness() -> None:
    """测试 overrides 可以覆盖单个属性（brightness）"""
    from neo_legend.luxury_theme import LUXURY_THEMES

    base_theme = LUXURY_THEMES["obsidian_gold"]
    data = {
        "luxury_theme": "obsidian_gold",
        "luxury_theme_overrides": {"brightness": 1.20}
    }
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.brightness == 1.20
    assert theme.contrast == base_theme.contrast


def test_overrides_single_property_contrast() -> None:
    """测试 overrides 可以覆盖 contrast 属性"""
    data = {
        "luxury_theme": "sapphire_platinum",
        "luxury_theme_overrides": {"contrast": 1.25}
    }
    theme = resolve_luxury_theme(data)

    assert theme is not None
    assert theme.contrast == 1.25


# ==================== 非图片格式不处理测试 ====================

def test_apply_non_image_media_type_returns_original() -> None:
    """测试对非图片格式（media_type 不是 image/ 开头）不处理，直接返回原结果"""
    result = RenderResult(
        content=b"not an image",
        media_type="application/json",
        file_extension="json",
        legend_type="test",
        style="default",
    )

    themed = apply_luxury_theme(result, {"luxury_theme": "obsidian_gold"})

    assert themed is result
    assert themed.content == b"not an image"


def test_apply_text_plain_returns_original() -> None:
    """测试 text/plain 格式不被处理"""
    result = RenderResult(
        content=b"plain text content",
        media_type="text/plain",
        file_extension="txt",
        legend_type="test",
        style="default",
    )

    themed = apply_luxury_theme(result, {"luxury_theme": "ruby_noir"})

    assert themed is result

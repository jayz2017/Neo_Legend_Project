from __future__ import annotations

"""奢华视觉主题模块 —— 跨渲染器输出的共享全局滤镜系统

该模块实现了一套可叠加在任意渲染结果上的奢华视觉后处理管线，
通过 14 个可调参数（亮度、对比度、饱和度、锐度、阴影/高光色调、暗角、边框等）
为图表图像添加电影级调色效果。
"""


import random
from dataclasses import asdict, dataclass
from io import BytesIO
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageSequence

from neo_legend.models import RenderResult


@dataclass(frozen=True)
class LuxuryTheme:
    """单个奢华主题的全部 14 个可调参数定义（frozen dataclass，不可变）

    每个参数都经过精心调校以产生协调的视觉效果，参数值通常接近 1.0（无变化），
    微小的偏移即可产生显著的视觉差异。

    Attributes:
        name: 主题唯一标识符（如 "obsidian_gold"）
        display_name: 主题显示名称（如 "Obsidian Gold"）
        description: 主题的人类可读描述
        brightness: 亮度因子（1.0=原始，>1.0=更亮，<1.0=更暗）
        contrast: 对比度因子（1.0=原始，>1.0=更高对比度）
        saturation: 饱和度/色彩强度因子（1.0=原始，>1.0=更鲜艳）
        sharpness: 锐化因子（1.0=原始，>1.0=更锐利）
        shadow_tint: 阴影区域色调（十六进制颜色，如 "#07090d" 为深蓝黑色）
        highlight_tint: 高光区域色调（十六进制颜色，如 "#ffd27a" 为暖金色）
        shadow_strength: 阴影色调混合强度（0.0~1.0，值越大阴影越偏向 shadow_tint）
        highlight_strength: 高光色调混合强度（0.0~1.0，值越大高光越偏向 highlight_tint）
        vignette_strength: 暗角强度（0.0=无暗角，值越大边缘越暗）
        border_color: 边框颜色（十六进制颜色）
        border_width_ratio: 边框宽度占短边的比例（如 0.004 表示短边的 0.4%）
    """
    name: str
    display_name: str
    description: str
    brightness: float  # 亮度因子
    contrast: float  # 对比度因子
    saturation: float  # 饱和度因子
    sharpness: float  # 锐化因子
    shadow_tint: str  # 阴影区十六进制色调
    highlight_tint: str  # 高光区十六进制色调
    shadow_strength: float  # 阴影色调混合强度
    highlight_strength: float  # 高光色调混合强度
    vignette_strength: float  # 暗角强度
    border_color: str  # 边框颜色
    border_width_ratio: float  # 边框宽度比例


# ========== 5 个内置奢华主题实例 ==========

LUXURY_THEMES: dict[str, LuxuryTheme] = {
    "obsidian_gold": LuxuryTheme(
        name="obsidian_gold",
        display_name="Obsidian Gold",
        description="深邃对比 + 温暖金色高光",
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
        description="明亮洁净 + 香槟暖调",
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
        description="冷峻阴影 + 铂金高光",
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
        description="翡翠绿深度 + 抛光对比",
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
        description="红宝石点缀 + 强黑位分离",
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

# ========== 6 个短别名映射（方便用户使用简短名称）==========

THEME_ALIASES = {
    "gold": "obsidian_gold",       # gold → Obsidian Gold
    "ivory": "champagne_ivory",     # ivory → Champagne Ivory
    "champagne": "champagne_ivory", # champagne → Champagne Ivory
    "sapphire": "sapphire_platinum",# sapphire → Sapphire Platinum
    "emerald": "emerald_onyx",      # emerald → Emerald Onyx
    "ruby": "ruby_noir",            # ruby → Ruby Noir
}

# ========== 6 个关闭值（当 luxury_theme 参数匹配这些值时不应用任何主题）==========

OFF_VALUES = {"", "none", "off", "false", "disabled", "disable"}


def luxury_theme_metadata() -> list[dict[str, Any]]:
    """返回全部主题的序列化字典列表 —— 供 /luxury-themes API 端点使用

    将 LUXURY_THEMES 中每个 LuxuryTheme 实例转换为普通字典，
    前端可直接用于渲染主题选择 UI 或展示文档说明。

    Returns:
        包含所有 5 个主题完整参数的字典列表
    """

    return [asdict(theme) for theme in LUXURY_THEMES.values()]


def apply_luxury_theme(result: RenderResult, data: dict[str, Any]) -> RenderResult:
    """核心滤镜应用函数 —— 根据请求中的配置对渲染结果应用奢华主题后处理

    处理流程：
    1. 调用 resolve_luxury_theme() 从 data 字典中解析目标主题（可能返回 None）
    2. 若无主题或非图像类型则直接返回原始结果（零开销短路）
    3. 从 data 中提取主题强度（默认 1.0，范围 0.0~2.0）
    4. 根据 media_type 分发到静态图（PNG）或动图（GIF）处理路径
    5. 返回应用了滤镜的新 RenderResult（原始 result 保持不变）

    Args:
        result: 渲染器产出的原始 RenderResult
        data: 包含 luxury_theme 等参数的请求字典

    Returns:
        可能已应用奢华主题滤镜的新 RenderResult
    """
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
    """从 data dict 中提取并解析主题名称（支持别名/random/OFF 值）

    解析优先级与逻辑：
    1. 从 data["luxury_theme"] 或 data["visual_theme"]（兼容旧字段名）中读取请求值
    2. 若值为 OFF_VALUES 集合中的任一值 → 返回 None（不应用主题）
    3. 若值为 "random" → 使用指定种子或系统随机数生成器随机选择一个主题
    4. 通过 THEME_ALIASES 别名映射将短名称解析为完整标识符
    5. 在 LUXURY_THEMES 字典中查找，未找到则返回 None
    6. 将最终解析出的主题名称记录到 data["_resolved_luxury_theme"]（供日志追踪）
    7. 支持通过 luxury_theme_overrides 字典微调单个参数值

    Args:
        data: 渲染请求的数据字典（包含 luxury_theme 等字段）

    Returns:
        解析出的 LuxuryTheme 实例；若无需应用主题则返回 None
    """
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
    """应用用户自定义参数覆盖 —— 允许调用者微调主题的单个参数值

    Args:
        theme: 基础 LuxuryTheme 实例
        overrides: 参数覆盖字典（如 {"brightness": 1.05, "border_color": "#ff0000"}）

    Returns:
        应用覆盖后的新 LuxuryTheme 实例（原实例不变）
    """
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
    """对静态图像（PNG）应用奢华主题滤镜

    Args:
        content: PNG 编码的字节数据
        theme: 目标 LuxuryTheme
        intensity: 主题强度系数

    Returns:
        应用滤镜后重新编码的 PNG 字节数据
    """
    with Image.open(BytesIO(content)) as image:
        themed = _apply_theme_to_image(image.convert("RGB"), theme, intensity)
        buffer = BytesIO()
        themed.save(buffer, format="PNG")
        return buffer.getvalue()


def _theme_gif(content: bytes, theme: LuxuryTheme, intensity: float) -> bytes:
    """对 GIF 动图逐帧应用奢华主题滤镜

    遍历 GIF 的每一帧，分别应用完整的滤镜管线后重新组装为 GIF。
    保留原始帧时长和循环设置。

    Args:
        content: GIF 编码的字节数据
        theme: 目标 LuxuryTheme
        intensity: 主题强度系数

    Returns:
        逐帧处理后重新编码的 GIF 字节数据
    """
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
    """核心滤镜链 —— 按顺序依次应用 7 个图像处理阶段

    处理管线（顺序重要）：
    1. Brightness（亮度调整）—— 全局明暗
    2. Contrast（对比度调整）—— 明暗层次分离
    3. Saturation / Color（饱和度调整）—— 色彩浓郁度
    4. Sharpness（锐化）—— 边缘清晰度
    5. Tone Tints（色调偏移）—— 阴影/高光分区着色
    6. Vignette（暗角）—— 边缘渐暗
    7. Border（边框）—— 外围装饰线框

    Args:
        image: 输入的 RGB 图像
        theme: 目标 LuxuryTheme 参数集
        intensity: 强度系数（0.0=无效果，1.0=标准效果，2.0=双倍效果）

    Returns:
        经过完整滤镜链处理的 RGB 图像
    """
    image = ImageEnhance.Brightness(image).enhance(_factor(theme.brightness, intensity))
    image = ImageEnhance.Contrast(image).enhance(_factor(theme.contrast, intensity))
    image = ImageEnhance.Color(image).enhance(_factor(theme.saturation, intensity))
    image = ImageEnhance.Sharpness(image).enhance(_factor(theme.sharpness, intensity))
    image = _apply_tone_tints(image, theme, intensity)
    image = _apply_vignette(image, theme.vignette_strength * intensity)
    return _apply_border(image, theme, intensity)


def _apply_tone_tints(image: Image.Image, theme: LuxuryTheme, intensity: float) -> Image.Image:
    """色调偏移滤镜 —— 基于亮度掩码对阴影和高光区域分别施加不同的颜色倾向

    算法原理：
    1. 计算每个像素的亮度值（luma，使用 BT.709 系数：R*0.2126 + G*0.7152 + B*0.0722）
    2. 构建阴影掩码：luma < 0.58 的像素，越暗掩码值越高（线性插值）
    3. 构建高光掩码：luma > 0.56 的像素，越亮掩码值越高（线性插值）
    4. 阴影区向 shadow_tint 混合，高光区向 highlight_tint 混合
    5. 使用 alpha 混合公式：out = original * (1 - mask * strength) + tint * mask * strength

    Args:
        image: 输入 RGB 图像
        theme: 包含 shadow_tint / highlight_tint / strength 的主题
        intensity: 强度系数

    Returns:
        应用了分区色调偏移的 RGB 图像
    """
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
    """暗角滤镜 —— 使图像边缘逐渐变暗，产生聚焦中心的视觉效果

    算法原理：
    1. 计算每个像素到图像中心的归一化距离（0=中心，1=角落）
    2. 生成径向衰减掩码：mask = 1 - distance * strength
    3. 将原图与掩码逐像素相乘，使边缘区域按距离比例变暗

    Args:
        image: 输入 RGB 图像
        strength: 暗角强度（0.0=无效果，值越大暗角越明显）

    Returns:
        应用了暗角效果的 RGB 图像（strength <= 0 时直接返回原图）
    """
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
    """装饰边框滤镜 —— 在图像外围绘制指定颜色的矩形边框

    边框宽度根据图像短边尺寸和主题配置的比例计算（至少 1 像素），
    通过多次绘制递增偏移量的矩形来实现多像素宽度的边框效果。

    Args:
        image: 输入 RGB 图像（会被原地修改）
        theme: 包含 border_color / border_width_ratio 的主题
        intensity: 强度系数（影响实际边框宽度）

    Returns:
        绘制了边框后的同一图像对象
    """
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
    """计算带强度缩放的增强因子

    当 intensity=1.0 时返回原始 value；
    当 intensity=0.0 时返回 1.0（无效果）；
    当 intensity=2.0 时效果翻倍。

    公式：result = 1.0 + (value - 1.0) * intensity

    Args:
        value: 主题定义的基础因子值
        intensity: 用户指定的强度系数

    Returns:
        经强度缩放后的实际增强因子
    """
    return 1.0 + (value - 1.0) * intensity


def _theme_intensity(data: dict[str, Any]) -> float:
    """从 data 字典中提取并约束主题强度值

    读取 luxury_theme_intensity 参数，将其裁剪到 [0.0, 2.0] 有效范围内。
    未指定时默认返回 1.0（标准强度）。

    Args:
        data: 请求数据字典

    Returns:
        裁剪后的强度浮点数
    """
    return float(np.clip(_to_float(data.get("luxury_theme_intensity")) or 1.0, 0.0, 2.0))


def _to_float(value: Any) -> float | None:
    """安全地将任意值转换为 float

    显式排除 bool 类型（因为 bool 是 int 的子类，True 会转为 1.0）和 None。
    转换失败时静默返回 None。

    Args:
        value: 待转换的任意值

    Returns:
        转换成功返回 float；无法转换则返回 None
    """
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    """将十六进制颜色字符串转换为 RGB 元组

    支持 "#RRGGBB" 和 "RRGGBB" 两种格式。
    格式无效时回退到白色 (255, 255, 255)。

    Args:
        value: 十六进制颜色字符串

    Returns:
        (R, G, B) 三元组，每个分量范围 0~255
    """
    raw = value.strip().lstrip("#")
    if len(raw) != 6:
        return 255, 255, 255
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)

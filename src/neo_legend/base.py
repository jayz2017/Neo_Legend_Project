from __future__ import annotations

"""独立渲染器技能的基类定义模块"""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from neo_legend.errors import UnknownStyleError
from neo_legend.models import LegendStyleInfo, LegendTypeInfo, RenderRequest, RenderResult


@dataclass(frozen=True)
class StyleDefinition:
    """样式元数据容器 —— 描述单个渲染器支持的一种样式变体"""

    name: str  # 样式名称标识符（如 "neon_glow"、"terrain"）
    description: str  # 样式的人类可读描述
    reference_images: tuple[str, ...] = ()  # 参考图片路径列表（可选）


class BaseLegendSkill(ABC):
    """所有渲染器技能的抽象基类 —— 定义统一的渲染契约和公共工具方法

    每个具体的图表渲染器（如雷达图、柱状图、球场图等）都必须继承此类，
    并实现 render() 抽象方法。基类提供了样式解析、尺寸计算、结果构建等通用逻辑。
    """

    # ========== 类级别常量（子类必须覆盖）==========

    legend_type: ClassVar[str]  # 图表类型唯一标识符（如 "radar_chart"、"court_shot"）
    display_name: ClassVar[str]  # 图表的显示名称（如 "华丽雷达图"）
    default_style: ClassVar[str]  # 默认样式名称（当请求未指定样式时使用）
    default_size: ClassVar[tuple[int, int]] = (1179, 1454)  # 默认输出尺寸 (宽, 高)，单位像素
    media_type: ClassVar[str] = "image/png"  # 输出媒体的 MIME 类型
    file_extension: ClassVar[str] = "png"  # 输出文件的扩展名
    style_definitions: ClassVar[tuple[StyleDefinition, ...]]  # 该渲染器支持的所有样式定义元组

    def metadata(self) -> LegendTypeInfo:
        """构建图类型信息对象，返回给 /legend-types 端点供 API 发现使用

        将本渲染器的类级别元数据（类型名、显示名、默认样式、支持的样式列表等）
        序列化为 LegendTypeInfo 结构化对象。
        """
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
        """样式名称解析与默认值回退

        处理流程：
        1. 若传入样式为空，回退到 default_style
        2. 统一规范化：去除首尾空白 → 转小写 → 将连字符替换为下划线
        3. 若规范化后为 "default" 字面量，再次回退到 default_style
        4. 校验是否在允许的样式列表中，否则抛出 UnknownStyleError 异常
        """
        normalized = (style or self.default_style).strip().lower().replace("-", "_")
        if normalized == "default":
            normalized = self.default_style

        allowed_styles = [style_definition.name for style_definition in self.style_definitions]
        if normalized not in allowed_styles:
            raise UnknownStyleError(self.legend_type, normalized, allowed_styles)
        return normalized

    def output_size(self, request: RenderRequest) -> tuple[int, int]:
        """计算实际输出尺寸（支持自定义宽度/高度覆盖默认值）

        - 宽度始终取请求中指定的 width
        - 高度优先取请求中的 height；若未指定则回退到 default_size[1]
        """
        return request.width, request.height or self.default_size[1]

    def result(self, content: bytes, style: str) -> RenderResult:
        """构建 RenderResult 返回对象 —— 将渲染输出的字节流封装为标准结果结构

        Args:
            content: 渲染生成的图像字节数据（PNG/GIF 等）
            style: 实际使用的样式名称（经过 resolve_style 解析后的值）

        Returns:
            封装完整的 RenderResult 不可变对象，包含内容、媒体类型、文件扩展名等元数据
        """
        return RenderResult(
            content=content,
            media_type=self.media_type,
            file_extension=self.file_extension,
            legend_type=self.legend_type,
            style=style,
        )

    @abstractmethod
    def render(self, request: RenderRequest) -> RenderResult:
        """抽象渲染方法 —— 子类必须实现此方法以生成实际的图表图像

        典型实现流程：
        1. 调用 resolve_style() 解析目标样式
        2. 调用 output_size() 确定输出尺寸
        3. 使用 Matplotlib / PIL 等库绑制图表
        4. 编码为字节数据并调用 result() 返回
        """

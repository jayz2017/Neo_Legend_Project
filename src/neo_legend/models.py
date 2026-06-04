from __future__ import annotations

"""Pydantic 数据模型与渲染结果契约定义模块"""


from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class RenderRequest(BaseModel):
    """渲染请求模型（Pydantic BaseModel）—— 定义所有图表渲染接口的统一输入契约

    该模型同时服务于 GET /render（查询参数）和 POST /render（JSON body）两种调用方式，
    通过 Pydantic 的字段验证约束确保输入数据的合法性与安全性。
    """

    # ========== 核心必填字段 ==========

    legend_type: str = Field(
        ...,
        min_length=1,
        description="要渲染的图表类型标识符（如 'radar_chart'、'court_shot'）",
    )
    # Field(...) 表示该字段为必填；min_length=1 约束字符串至少 1 个字符

    style: str = Field(
        "default",
        min_length=1,
        description="样式变体名称（如 'neon_glow'、'terrain'），默认 'default'",
    )
    # 默认值 "default"；min_length=1 确保非空字符串

    # ========== 可选文本覆盖字段 ==========

    title: str | None = Field(None, description="可选的标题文本覆盖")
    subtitle: str | None = Field(None, description="可选的副标题文本覆盖")
    kicker: str | None = Field(
        None,
        description="可选的小标签头文本覆盖（用于报告风格图表的左上角小字）",
    )
    theme_label: str | None = Field(
        None,
        description="可选的主题标签文本覆盖（用于报告风格图表的右上角标签）",
    )
    footer: str | None = Field(None, description="可选的页脚文本覆盖")

    # ========== 渲染器专用数据与尺寸 ==========

    data: dict[str, Any] = Field(
        default_factory=dict,
        description="渲染器专用的数据字典（如图表节点、数据系列等），同时承载奢华主题参数",
    )

    width: int = Field(
        1179,
        ge=640,
        le=2400,
        description="输出图像宽度（像素）",
    )
    # ge=640 (greater or equal): 最小值 640 像素
    # le=2400 (less or equal): 最大值 2400 像素
    # 默认值 1179 像素（接近标准 A4 纵向比例）

    height: int | None = Field(
        None,
        ge=640,
        le=3200,
        description="输出图像高度（像素），为 None 时使用渲染器的默认高度",
    )
    # 可选字段；ge/le 约束范围 640~3200

    @field_validator("legend_type", "style")
    @classmethod
    def normalize_token(cls, value: str) -> str:
        """字段验证器 —— 将 legend_type 和 style 统一规范化为小写下划线格式

        处理逻辑：去除首尾空白 → 转小写 → 将连字符替换为下划线
        例如："Court-Shot" → "court_shot"
        """
        return value.strip().lower().replace("-", "_")

    @model_validator(mode="after")
    def mirror_report_text_fields(self) -> RenderRequest:
        """模型级验证器 —— 将 kicker/theme_label/footer 字段自动镜像同步到 data 字典中

        这样做的好处是：渲染器只需从 request.data 中读取这些文本字段，
        而不需要分别检查顶层字段和 data 字典，简化了渲染器内部的访问逻辑。
        """
        data = dict(self.data)
        changed = False
        for key in ("kicker", "theme_label", "footer"):
            value = getattr(self, key)
            if value is not None:
                data[key] = value
                changed = True
        if changed:
            self.data = data
        return self


class LegendStyleInfo(BaseModel):
    """单个样式的公共元数据 —— 供 /legend-types API 端点返回给前端"""

    name: str  # 样式标识符
    description: str  # 样式描述
    reference_images: list[str] = Field(default_factory=list)  # 参考图片 URL 列表


class LegendTypeInfo(BaseModel):
    """单个已注册图渲染器的公共元数据 —— 供 /legend-types API 端点返回"""

    legend_type: str  # 图表类型标识符
    display_name: str  # 显示名称
    default_style: str  # 默认样式名
    styles: list[LegendStyleInfo]  # 支持的所有样式列表
    media_type: str  # 输出媒体 MIME 类型


class BatchGenerateRequest(BaseModel):
    """批量生成请求模型 —— 用于 /batch-generate 端点，一次性生成所有内置示例图像"""

    output_dir: str = Field(
        r"G:\echaet",
        min_length=1,
        description="生成图像的输出目录路径",
    )
    project_root: str | None = Field(
        None,
        description="项目根目录路径（用于定位 README 参考图片），默认为当前工作目录",
    )


class BatchGenerateSummary(BaseModel):
    """批量生成响应摘要模型 —— 返回批量生成的统计信息"""

    output_dir: str  # 输出目录路径
    log_dir: str  # 日志目录路径
    raw_image_dir: str  # 原始图像目录路径
    image_count: int  # 生成的图像总数
    average_score: float | None  # 平均质量评分（可能为 None）


@dataclass(frozen=True)
class RenderResult:
    """渲染结果数据类（frozen dataclass）—— 不可变的返回对象

    frozen=True 表示创建后不可修改，确保渲染结果在传递过程中不会被意外篡改。
    该对象由各渲染器 skill 的 render() 方法产出，最终由 FastAPI 路由封装为 HTTP 响应。
    """

    content: bytes  # 图像二进制数据（PNG 编码字节流或 GIF 帧数据）
    media_type: str  # MIME 类型（"image/png" 或 "image/gif"）
    file_extension: str  # 文件扩展名（"png" 或 "gif"）
    legend_type: str  # 图表类型标识符（用于响应头 X-Legend-Type）
    style: str  # 实际使用的样式名（用于响应头 X-Legend-Style）

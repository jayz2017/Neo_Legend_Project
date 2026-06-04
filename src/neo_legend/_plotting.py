from __future__ import annotations

"""共享 Matplotlib 绑制工具函数模块 —— 供所有渲染器 Skill 复用的底层图形基础设施

该模块封装了 Matplotlib 的 Figure 创建、画布管理、图像编码等通用操作，
确保所有渲染器输出的图像具有一致的 DPI、尺寸计算方式和编码格式。
"""


from io import BytesIO
from typing import Iterable

import matplotlib

matplotlib.use("Agg")  # 使用非交互式 Agg 后端（服务器环境无 GUI，必须使用此后端）

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_hex
from matplotlib.figure import Figure
import numpy as np

# ========== 全局中文字体配置 ==========
# Matplotlib 默认使用 DejaVu Sans，不支持 CJK 字符。
# 在 Windows 环境下依次尝试微软雅黑、黑体、宋体、Noto Sans CJK，
# 找到第一个可用字体后设为全局默认 sans-serif 字体族的首选字体。
from pathlib import Path as _Path

_CJK_FONT_CANDIDATES = (
    r"C:\Windows\Fonts\msyh.ttc",        # 微软雅黑
    r"C:\Windows\Fonts\simhei.ttf",       # 黑体
    r"C:\Windows\Fonts\simsun.ttc",       # 宋体
    r"C:\Windows\Fonts\NotoSansCJK-Regular.ttc",  # Noto Sans CJK
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Linux
    "/System/Library/Fonts/PingFang.ttc",  # macOS
)

_cjk_font_name: str | None = None
for _fp in _CJK_FONT_CANDIDATES:
    if _Path(_fp).exists():
        from matplotlib.font_manager import FontProperties as _FP, fontManager as _fm
        _prop = _FP(fname=_fp)
        _cjk_font_name = _prop.get_name()
        # 将 CJK 字体插入 sans-serif 字体族的首位
        _current = plt.rcParams.get("font.sans-serif", [])
        plt.rcParams["font.sans-serif"] = [_cjk_font_name] + [f for f in _current if f != _cjk_font_name]
        break

# 关闭 Unicode 减号替换（避免负号显示异常）
plt.rcParams["axes.unicode_minus"] = False

DPI = 100  # 全局默认分辨率：每英寸 100 像素


def create_figure(width: int, height: int, background: str) -> Figure:
    """创建指定尺寸和背景色的 Matplotlib Figure 对象

    尺寸计算方式：像素值 / DPI = 英寸值，Matplotlib 内部以英寸为单位工作。
    通过 subplots_adjust 将边距归零，使绘图区域完全填满整个 Figure，
    实现精确的像素级定位控制。

    Args:
        width: 图像宽度（像素）
        height: 图像高度（像素）
        background: 背景色（十六进制颜色字符串，如 "#0a0a1a"）

    Returns:
        配置完成的 matplotlib.figure.Figure 对象
    """
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI, facecolor=background)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    return fig


def add_canvas(fig: Figure) -> plt.Axes:
    """在 Figure 上创建一个全尺寸绑图画布（Axes）并返回

    创建的 Axes 坐标范围为 [0, 1] × [0, 1]（归一化坐标），
    关闭坐标轴显示（set_axis_off），使其成为纯粹的绘图画布。
    所有渲染器都在这个 Axes 上进行文本、形状、线条等元素的绘制。

    Args:
        fig: 由 create_figure() 创建的 Figure 对象

    Returns:
        配置为全屏画布模式的 matplotlib.axes.Axes 对象
    """
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    return ax


def save_png(fig: Figure) -> bytes:
    """将 Figure 编码为 PNG 格式的字节数据

    编码配置：
    - format="png"：PNG 无损格式
    - dpi=fig.dpi：保持创建时设定的 DPI 值
    - facecolor=fig.get_facecolor()：保留背景色填充
    - pad_inches=0：去除保存时的额外白边填充

    编码完成后显式关闭 Figure 以释放内存。

    Args:
        fig: 已完成绘制内容的 Figure 对象

    Returns:
        PNG 编码的二进制字节数据
    """
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=fig.dpi, facecolor=fig.get_facecolor(), pad_inches=0)
    plt.close(fig)
    return buffer.getvalue()


def make_gradient(colors: Iterable[str], name: str) -> LinearSegmentedColormap:
    """从一组颜色列表创建线性分段渐变色图（Colormap）

    颜色在 [0, 1] 范围内均匀分布，适用于热力图、渐变填充等场景。
    例如传入 ["#000000", "#ff0000", "#ffffff"] 可创建黑→红→白的三段渐变。

    Args:
        colors: 十六进制颜色字符串的可迭代对象（至少需要 2 个颜色）
        name: 色图的名称标识符

    Returns:
        matplotlib.colors.LinearSegmentedColormap 实例
    """
    return LinearSegmentedColormap.from_list(name, list(colors))


def cmap_color(colors: list[str], value: float) -> str:
    """根据数值在颜色渐变中插值并返回对应的十六进制颜色字符串

    将 value 映射到 [0, 1] 范围后查询色图，返回最接近的离散颜色值。
    典型用途：根据数据值动态确定数据点的填充颜色。

    Args:
        colors: 渐变色列表（如 ["#00ff88", "#ffcc00", "#ff3344"]）
        value: 插值位置（会被裁剪到 [0, 1] 范围）

    Returns:
        十六进制颜色字符串（如 "#ff8800"）
    """
    cmap = make_gradient(colors, "local_gradient")
    return to_hex(cmap(float(np.clip(value, 0, 1))))


def seeded_rng(seed: int = 2026) -> np.random.Generator:
    """创建带固定种子的随机数生成器（用于可复现的随机效果）

    所有渲染器中涉及随机布局/抖动的地方都应使用此函数获取 RNG，
    确保相同输入参数始终产生相同的输出图像（便于调试和回归测试）。

    Args:
        random seed: 随机种子值，默认 2026

    Returns:
        numpy.random.Generator 实例
    """
    return np.random.default_rng(seed)


def add_reference_footer(canvas: plt.Axes, text: str, color: str = "#d6d6d6") -> None:
    """在画布底部中央添加参考图专用的页脚文本

    用于批量生成的示例图片底部的版本标注或来源说明。
    文本位置固定在 y=0.025（距底部 2.5%），半透明显示。

    Args:
        canvas: 目标 Axes 画布
        text: 页脚文本内容
        color: 文本颜色（默认浅灰色），alpha 固定为 0.72
    """
    canvas.text(
        0.5,
        0.025,
        text,
        color=color,
        fontsize=11,
        ha="center",
        va="center",
        alpha=0.72,
        fontweight="bold",
    )

from __future__ import annotations

from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from neo_legend.animated_court_shot import AnimatedCourtShotSkill
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


@pytest.fixture
def registry():
    return build_default_registry()


def test_pulse_style_returns_gif_format(registry):
    """测试 pulse 样式返回 GIF 格式（非 PNG）"""
    request = RenderRequest(legend_type="court_shot_animation", style="pulse", width=700, height=700)
    result = registry.render(request)

    assert result.media_type == "image/gif"
    assert result.file_extension == "gif"

    image = Image.open(BytesIO(result.content))
    assert image.format == "GIF"


def test_sweep_style_returns_gif_format(registry):
    """测试 sweep 样式返回 GIF 格式"""
    request = RenderRequest(legend_type="court_shot_animation", style="sweep", width=700, height=700)
    result = registry.render(request)

    assert result.media_type == "image/gif"

    image = Image.open(BytesIO(result.content))
    assert image.format == "GIF"


def test_sweep_alpha_reveals_data_progressively():
    early = AnimatedCourtShotSkill._progressive_sweep_alpha(
        total_count=20,
        frame_index=1,
        frame_count=5,
    )
    late = AnimatedCourtShotSkill._progressive_sweep_alpha(
        total_count=20,
        frame_index=4,
        frame_count=5,
    )

    early_visible = int(np.count_nonzero(early > 0))
    late_visible = int(np.count_nonzero(late > 0))

    assert 0 < early_visible < late_visible
    assert np.all(late[:early_visible] > 0)
    assert late_visible == 20


def test_gif_contains_multiple_frames(registry):
    """验证 GIF 文件包含多帧动画"""
    request = RenderRequest(
        legend_type="court_shot_animation",
        style="pulse",
        width=700,
        height=700,
        data={"frame_count": 10}
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.is_animated  # PIL 属性检查是否为动画
    assert image.n_frames >= 10  # 验证帧数


def test_custom_frame_count_parameter(registry):
    """测试自定义 frame_count 参数影响帧数"""
    few_frames = registry.render(RenderRequest(
        legend_type="court_shot_animation",
        style="pulse",
        width=700,
        height=700,
        data={"frame_count": 5}
    ))
    many_frames = registry.render(RenderRequest(
        legend_type="court_shot_animation",
        style="pulse",
        width=700,
        height=700,
        data={"frame_count": 15}
    ))

    img_few = Image.open(BytesIO(few_frames.content))
    img_many = Image.open(BytesIO(many_frames.content))

    assert img_few.n_frames == 5
    assert img_many.n_frames == 15


def test_custom_title_and_subtitle(registry):
    """测试自定义标题和副标题"""
    request = RenderRequest(
        legend_type="court_shot_animation",
        style="pulse",
        width=700,
        height=700,
        title="ANIMATED TEST",
        subtitle="CUSTOM SUBTITLE HERE"
    )
    result = registry.render(request)

    image = Image.open(BytesIO(result.content))
    assert image.format == "GIF"


def test_invalid_style_raises_error(registry):
    """测试无效 style 参数抛出异常"""
    from neo_legend.errors import UnknownStyleError

    with pytest.raises(UnknownStyleError):
        registry.render(RenderRequest(legend_type="court_shot_animation", style="invalid"))


def test_different_styles_produce_different_gifs(registry):
    """测试 pulse 和 sweep 样式产生不同的 GIF 内容"""
    pulse = registry.render(RenderRequest(
        legend_type="court_shot_animation",
        style="pulse",
        width=700,
        height=700,
        data={"frame_count": 5}
    ))
    sweep = registry.render(RenderRequest(
        legend_type="court_shot_animation",
        style="sweep",
        width=700,
        height=700,
        data={"frame_count": 5}
    ))

    assert pulse.content != sweep.content

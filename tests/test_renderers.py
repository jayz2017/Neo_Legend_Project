from __future__ import annotations

from io import BytesIO

from PIL import Image

from neo_legend.models import RenderRequest


def test_all_renderer_styles_return_valid_images(registry) -> None:
    for metadata in registry.list_types():
        for style in metadata.styles:
            request = RenderRequest(
                legend_type=metadata.legend_type,
                style=style.name,
                width=720,
                height=900,
            )

            result = registry.render(request)
            image = Image.open(BytesIO(result.content))

            assert result.media_type == metadata.media_type
            assert image.width == 720
            assert image.height == 900
            assert image.format in {"PNG", "GIF"}


def test_style_parameter_changes_render_variant(registry) -> None:
    terrain = registry.render(RenderRequest(legend_type="court_shot", style="terrain", width=720, height=900))
    zone = registry.render(RenderRequest(legend_type="court_shot", style="zone", width=720, height=900))

    assert terrain.content != zone.content
    assert terrain.style == "terrain"
    assert zone.style == "zone"


def test_all_20_legend_types_registered(registry):
    """验证全部 14 种 legend_type 均可渲染"""
    expected_types = [
        "court_shot", "dual_court_shot", "court_shot_animation",
        "coordinate", "plus_minus_coordinate", "rose", "table", "points_location",
        "radar_chart", "dual_radar_chart", "bar_chart", "line_chart", "combo_chart",
        "bubble_chart", "sankey_chart", "calendar_chart", "matrix_bubble_chart",
        "chord_chart", "scatter_matrix_chart", "stacked_bar_chart"
    ]

    registered = {t.legend_type for t in registry.list_types()}
    for t in expected_types:
        assert t in registered, f"{t} not in registry"

        req = RenderRequest(legend_type=t, width=640, height=640)
        result = registry.render(req)

        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(result.content))
        assert img.format in {"PNG", "GIF"}


def test_all_style_variants_render_successfully(registry):
    """测试每个 legend_type 的所有 style 变体均可正常渲染"""
    from io import BytesIO
    from PIL import Image

    for metadata in registry.list_types():
        for style_info in metadata.styles:
            request = RenderRequest(
                legend_type=metadata.legend_type,
                style=style_info.name,
                width=640,
                height=640
            )
            result = registry.render(request)

            image = Image.open(BytesIO(result.content))
            assert image.format in {"PNG", "GIF"}, \
                f"{metadata.legend_type}/{style_info.name} produced invalid format"


def test_boundary_min_dimensions(registry):
    """测试最小尺寸请求（640x640）正常处理"""
    for legend_type in ["court_shot", "table", "coordinate"]:
        request = RenderRequest(legend_type=legend_type, width=640, height=640)
        result = registry.render(request)

        from io import BytesIO
        from PIL import Image
        image = Image.open(BytesIO(result.content))
        assert image.size == (640, 640)


def test_boundary_max_dimensions(registry):
    """测试最大尺寸请求（2400x3200）正常处理"""
    request = RenderRequest(legend_type="court_shot", width=2400, height=3200)
    result = registry.render(request)

    from io import BytesIO
    from PIL import Image
    image = Image.open(BytesIO(result.content))
    assert image.size == (2400, 3200)

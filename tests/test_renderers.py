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

from __future__ import annotations

from io import BytesIO

from PIL import Image


def test_health(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_legend_types_endpoint(client) -> None:
    response = client.get("/legend-types")

    assert response.status_code == 200
    legend_types = {item["legend_type"] for item in response.json()}
    assert "court_shot" in legend_types
    assert "table" in legend_types


def test_get_render_uses_type_and_style_params(client) -> None:
    response = client.get(
        "/render",
        params={"legend_type": "coordinate", "style": "gold_scorers", "width": 700, "height": 800},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-legend-type"] == "coordinate"
    assert response.headers["x-legend-style"] == "gold_scorers"
    image = Image.open(BytesIO(response.content))
    assert image.size == (700, 800)


def test_post_render_accepts_custom_payload(client) -> None:
    payload = {
        "legend_type": "table",
        "style": "heatmap_light",
        "width": 700,
        "height": 900,
        "title": "Custom Table",
        "data": {
            "rows": [
                {
                    "team": "NEO",
                    "team_color": "#29b98f",
                    "name": "Example",
                    "pts_created": 42.0,
                    "ts": 61,
                    "ast_tov": 2.4,
                    "mpg": 35.0,
                }
            ]
        },
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert Image.open(BytesIO(response.content)).format == "PNG"


def test_animation_returns_gif(client) -> None:
    response = client.get(
        "/render",
        params={"legend_type": "court_shot_animation", "style": "pulse", "width": 700, "height": 700},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/gif"
    assert Image.open(BytesIO(response.content)).format == "GIF"


def test_unknown_legend_type_returns_404(client) -> None:
    response = client.get("/render", params={"legend_type": "missing"})

    assert response.status_code == 404


def test_unknown_style_returns_400(client) -> None:
    response = client.get("/render", params={"legend_type": "court_shot", "style": "missing"})

    assert response.status_code == 400
    assert "allowed_styles" in response.json()["detail"]

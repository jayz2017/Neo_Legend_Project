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


def test_render_points_location_via_api(client):
    """测试 GET /render 新增 points_location 类型"""
    response = client.get(
        "/render",
        params={"legend_type": "points_location", "style": "default", "width": 700, "height": 900}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers["x-legend-type"] == "points_location"

    from io import BytesIO
    from PIL import Image
    image = Image.open(BytesIO(response.content))
    assert image.format == "PNG"


def test_post_render_with_large_custom_data(client):
    """测试 POST /render 携带大量自定义数据"""
    import json

    payload = {
        "legend_type": "table",
        "style": "heatmap_light",
        "width": 700,
        "height": 900,
        "data": {
            "rows": [
                {
                    "team": f"TEAM_{i}",
                    "team_color": "#29b98f",
                    "name": f"Player {i}",
                    "pts_created": float(30 + i),
                    "ts": float(50 + i),
                    "ast_tov": float(1.0 + i * 0.2),
                    "mpg": float(30 + i * 0.5)
                }
                for i in range(20)  # 20 行数据
            ]
        }
    }

    response = client.post("/render", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_missing_required_field_error_format(client):
    """测试缺少必填字段时的错误响应格式一致性"""
    response = client.post("/render", json={})

    assert response.status_code == 422  # Pydantic validation error
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, list)
    assert any("legend_type" in str(err).lower() for err in error_detail)


def test_get_legend_types_includes_points_location(client):
    """测试 GET /legend-types 包含新增的 points_location 类型"""
    response = client.get("/legend-types")

    assert response.status_code == 200
    legend_types = response.json()
    type_names = [item["legend_type"] for item in legend_types]

    assert "points_location" in type_names


def test_render_radar_chart_via_api(client):
    response = client.get("/render", params={"legend_type": "radar_chart", "style": "neon_glow", "width": 700, "height": 900})
    assert response.status_code == 200
    assert response.headers["x-legend-type"] == "radar_chart"

def test_render_bar_chart_via_api(client):
    response = client.get("/render", params={"legend_type": "bar_chart", "style": "glass_3d", "width": 700, "height": 900})
    assert response.status_code == 200

def test_render_sankey_chart_via_api(client):
    response = client.get("/render", params={"legend_type": "sankey_chart", "style": "golden_paths", "width": 700, "height": 900})
    assert response.status_code == 200

def test_legend_types_includes_new_types(client):
    response = client.get("/legend-types")
    types = [item["legend_type"] for item in response.json()]
    new_types = ["radar_chart", "dual_radar_chart", "bar_chart", "combo_chart", "bubble_chart", "sankey_chart"]
    for t in new_types:
        assert t in types

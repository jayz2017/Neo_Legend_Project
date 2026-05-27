"""FastAPI application for rendering legend graphics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from neo_legend.batch_generate import generate_all
from neo_legend.errors import UnknownLegendTypeError, UnknownStyleError
from neo_legend.luxury_theme import luxury_theme_metadata
from neo_legend.models import (
    BatchGenerateRequest,
    BatchGenerateSummary,
    LegendTypeInfo,
    RenderRequest,
    RenderResult,
)
from neo_legend.registry import build_default_registry

app = FastAPI(
    title="Neo Legend Renderer",
    version="1.0.0",
    description="""
## Neo Legend 图表渲染引擎 API

专业的 NBA 风格数据可视化图表渲染服务，支持 **14 种图表类型**、**42 种样式变体** 和 **5 种奢华视觉主题**。

### 📊 支持的图表类型 (14 种)

| 类型标识 | 名称 | 样式数 | 输出格式 |
|---------|------|--------|---------|
| `court_shot` | 球场投射图 | 4 | PNG |
| `dual_court_shot` | 双球场对比图 | 2 | PNG |
| `court_shot_animation` | 动态球场图 | 3 | **GIF** |
| `coordinate` | 坐标散点图 | 2 | PNG |
| `plus_minus_coordinate` | 正负四象限图 | 2 | PNG |
| `rose` | 玫瑰图 | 2 | PNG |
| `table` | 表格图 | 3 | PNG |
| `points_location` | 总分位置热力图 | 2 | PNG |
| `radar_chart` | 华丽雷达图 ⭐ | 3 | PNG |
| `dual_radar_chart` | 双雷达对比图 ⭐ | 3 | PNG |
| `bar_chart` | 华丽柱状图 ⭐ | 4 | PNG |
| `combo_chart` | 组合图表 ⭐ | 4 | PNG |
| `bubble_chart` | 华丽水滴图 ⭐ | 4 | PNG |
| `sankey_chart` | 华丽桑基图 ⭐ | 4 | PNG |

### 🎨 奢华视觉主题 (Luxury Themes)

通过 `luxury_theme` 参数为任意图表叠加全局奢华滤镜效果：

| 主题标识 | 显示名称 | 描述 | 别名 |
|---------|---------|------|------|
| `obsidian_gold` | Obsidian Gold | 深邃对比 + 温暖金色高光 | `gold` |
| `champagne_ivory` | Champagne Ivory | 明亮洁净 + 香槟暖调 | `ivory`, `champagne` |
| `sapphire_platinum` | Sapphire Platinum | 冷峻阴影 + 铂金高光 | `sapphire` |
| `emerald_onyx` | Emerald Onyx | 翡翠绿深度 + 抛光对比 | `emerald` |
| `ruby_noir` | Ruby Noir | 红宝石点缀 + 强黑位分离 | `ruby` |
| `random` | 随机主题 | 随机选择一个奢华主题 | - |

### 🔧 GET /render 奢华主题参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `luxury_theme` | string | 无 | 主题名称或别名，`random` 随机，留空不应用 |
| `luxury_theme_seed` | string | 无 | 随机种子（用于 `random` 主题的可复现） |
| `luxury_theme_intensity` | float | 1.0 | 主题强度 (0.0=无效果 ~ 2.0=最强) |

### 📝 使用示例

**基础渲染:**
```
GET /render?legend_type=radar_chart&style=neon_glow&width=1200&height=1400
```

**带奢华主题:**
```
GET /render?legend_type=bar_chart&style=glass_3d&luxury_theme=gold&luxury_theme_intensity=1.5
```

**POST 自定义数据:**
```json
POST /render
{
  "legend_type": "sankey_chart",
  "style": "golden_paths",
  "data": {
    "nodes": [...],
    "flows": [...],
    "luxury_theme": "ruby_noir"
  }
}
```
""",
)
registry = build_default_registry()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/legend-types", response_model=list[LegendTypeInfo])
def legend_types() -> list[LegendTypeInfo]:
    return registry.list_types()


@app.get("/luxury-themes")
def luxury_themes() -> list[dict[str, Any]]:
    return luxury_theme_metadata()


@app.get("/render")
def render_preview(
    legend_type: str = Query(..., description="Legend type, for example court_shot."),
    style: str = Query("default", description="Style variant, for example terrain."),
    title: str | None = Query(None),
    subtitle: str | None = Query(None),
    width: int = Query(1179, ge=640, le=2400),
    height: int | None = Query(None, ge=640, le=3200),
    luxury_theme: str | None = Query(None, description="Optional global luxury theme or random."),
    luxury_theme_seed: str | None = Query(None, description="Optional seed for reproducible random theme."),
    luxury_theme_intensity: float | None = Query(None, ge=0.0, le=2.0),
) -> Response:
    data: dict[str, Any] = {}
    if luxury_theme is not None:
        data["luxury_theme"] = luxury_theme
    if luxury_theme_seed is not None:
        data["luxury_theme_seed"] = luxury_theme_seed
    if luxury_theme_intensity is not None:
        data["luxury_theme_intensity"] = luxury_theme_intensity
    request = RenderRequest(
        legend_type=legend_type,
        style=style,
        title=title,
        subtitle=subtitle,
        data=data,
        width=width,
        height=height,
    )
    return _render_response(request)


@app.post("/render")
def render_from_body(request: RenderRequest) -> Response:
    return _render_response(request)


@app.post("/batch-generate", response_model=BatchGenerateSummary)
def batch_generate(request: BatchGenerateRequest) -> BatchGenerateSummary:
    project_root = Path(request.project_root) if request.project_root else Path.cwd()
    report = generate_all(output_dir=Path(request.output_dir), project_root=project_root)
    return BatchGenerateSummary(
        output_dir=report["output_dir"],
        log_dir=report["log_dir"],
        raw_image_dir=report["raw_image_dir"],
        image_count=report["image_count"],
        average_score=report["average_score"],
    )


def _render_response(request: RenderRequest) -> Response:
    result = _render_or_http_error(request)
    filename = f"{result.legend_type}-{result.style}.{result.file_extension}"
    headers = {
        "Content-Disposition": f'inline; filename="{filename}"',
        "X-Legend-Type": result.legend_type,
        "X-Legend-Style": result.style,
    }
    return Response(content=result.content, media_type=result.media_type, headers=headers)


def _render_or_http_error(request: RenderRequest) -> RenderResult:
    try:
        return registry.render(request)
    except UnknownLegendTypeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UnknownStyleError as exc:
        detail: dict[str, Any] = {
            "message": str(exc),
            "legend_type": exc.legend_type,
            "style": exc.style,
            "allowed_styles": exc.allowed_styles,
        }
        raise HTTPException(status_code=400, detail=detail) from exc

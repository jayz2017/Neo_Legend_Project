from __future__ import annotations

"""FastAPI 应用模块 —— 图表渲染引擎的 HTTP API 服务入口"""


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


# ========== FastAPI 应用实例（含 Swagger/OpenAPI 文档配置）==========

app = FastAPI(
    title="Neo Legend Renderer",
    version="1.0.0",
    description="""
## Neo Legend 图表渲染引擎 API

专业的 NBA 风格数据可视化图表渲染服务，支持 **20 种图表类型**、**56 种样式变体** 和 **5 种奢华视觉主题**。

### 📊 支持的图表类型 (20 种)

#### 🏀 球场数据类（5 种）

| 类型标识 | 名称 | 样式数 | 输出格式 |
|---------|------|--------|---------|
| `court_shot` | 球场投射图 | 5 | PNG |
| `dual_court_shot` | 双球场对比图 | 2 | PNG |
| `court_shot_animation` | 动态球场图 | 3 | **GIF** |
| `coordinate` | 坐标散点图 | 2 | PNG |
| `plus_minus_coordinate` | 正负四象限图 | 2 | PNG |

#### 📈 统计分析类（8 种）

| 类型标识 | 名称 | 样式数 | 输出格式 |
|---------|------|--------|---------|
| `radar_chart` | 华丽雷达图 ⭐ | 3 | PNG |
| `dual_radar_chart` | 双雷达对比图 ⭐ | 3 | PNG |
| `bar_chart` | 华丽柱状图 ⭐ | 4 | PNG |
| `combo_chart` | 组合图表 ⭐ | 4 | PNG |
| `bubble_chart` | 华丽水滴图 ⭐ | 4 | PNG |
| `line_chart` | 华丽折线图 ⭐ | 3 | PNG |
| `stacked_bar_chart` | 圆角堆叠柱状图 | 2 | PNG |
| `rose` | 玫瑰环形图 | 2 | PNG |

#### 🔗 关系与分布类（4 种）

| 类型标识 | 名称 | 样式数 | 输出格式 |
|---------|------|--------|---------|
| `sankey_chart` | 华丽桑基图 ⭐ | 4 | PNG |
| `chord_chart` | 资金流向弦图 | 2 | PNG |
| `scatter_matrix_chart` | 散点矩阵图 | 2 | PNG |
| `matrix_bubble_chart` | 相关性气泡矩阵 | 2 | PNG |

#### 📋 数据展示类（3 种）

| 类型标识 | 名称 | 样式数 | 输出格式 |
|---------|------|--------|---------|
| `table` | 热力排名表格图 | 3 | PNG |
| `points_location` | 总分位置热力图 | 2 | PNG |
| `calendar_chart` | 高管日历图 | 2 | PNG |

> ⭐ 标记为新增的华丽视觉风格图表

### 🎨 全部样式变体总览

| 图表类型 | 样式列表 |
|---------|----------|
| court_shot (5) | terrain, points_location, kobe_shots, hex, zone |
| dual_court_shot (2) | year_over_year, split_hex |
| court_shot_animation (3) | arena_arc, pulse, sweep |
| coordinate (2) | dark_bubble, gold_scorers |
| plus_minus_coordinate (2) | paper_quadrant, clean_quadrant |
| radar_chart (3) | neon_glow, crystal_metal, gradient_rainbow |
| dual_radar_chart (3) | versus_battle, mirror_compare, evolution_track |
| bar_chart (4) | glass_3d, neon_tubes, gradient_sky, crystal_pillars |
| combo_chart (4) | crystal_stream, neon_pulse, sunset_gradient, ocean_depths |
| bubble_chart (4) | water_drops, fireflies, galaxy_stars, crystal_orbs |
| line_chart (3) | executive_trend, champagne_forecast, aurora_stream |
| stacked_bar_chart (2) | wall_street_stack, portfolio_stack |
| rose (2) | proposal_comparison, lottery_black |
| sankey_chart (4) | neon_streams, energy_flow, crystal_rivers, golden_paths |
| chord_chart (2) | capital_flows, sector_rotation |
| scatter_matrix_chart (2) | macro_quadrants, portfolio_pairs |
| matrix_bubble_chart (2) | correlation_board, risk_heat_matrix |
| table (3) | heatmap_light, scoreboard_dark, league_standings_gradient |
| points_location (2) | default, warm_gradient |
| calendar_chart (2) | executive_month, earnings_calendar |

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

**随机主题 + 可复现种子:**
```
GET /render?legend_type=sankey_chart&style=neon_streams&luxury_theme=random&luxury_theme_seed=my_seed_42
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
# 创建全局注册表实例（包含所有 20 个内置 Skill）
registry = build_default_registry()


# ========== 路由端点定义 ==========


@app.get("/health")
def health() -> dict[str, str]:
    """健康检查端点 —— 用于负载均衡器、Kubernetes 探针等基础设施的健康探测

    Returns:
        固定返回 {"status": "ok"} 表示服务正常运行
    """
    return {"status": "ok"}


@app.get("/legend-types", response_model=list[LegendTypeInfo])
def legend_types() -> list[LegendTypeInfo]:
    """图表类型列表端点 —— 返回所有已注册图表类型的元数据和可用样式列表

        前端可调用此端点动态构建类型/样式选择下拉框。
        返回数据按 legend_type 字母序排列。

    Returns:
        LegendTypeInfo 列表，每项包含类型标识、显示名称、默认样式和完整样式定义
    """
    return registry.list_types()


@app.get("/luxury-themes")
def luxury_themes() -> list[dict[str, Any]]:
    """奢华主题列表端点 —— 返回所有内置奢华主题的可调参数详情

        前端可调用此端点展示主题选择 UI 或文档说明。
        每个主题包含 14 个可调参数（亮度、对比度、饱和度等）。

    Returns:
        主题字典列表，每个字典包含一个 LuxuryTheme 的全部字段
    """
    return luxury_theme_metadata()


@app.get("/render")
def render_preview(
    legend_type: str = Query(..., description="图表类型标识符，例如 court_shot"),
    style: str = Query("default", description="样式变体名称，例如 terrain"),
    title: str | None = Query(None),
    subtitle: str | None = Query(None),
    kicker: str | None = Query(None, description="可选的小标签头文本（用于报告风格图表）"),
    theme_label: str | None = Query(None, description="可选的右上角主题标签文本（用于报告风格图表）"),
    footer: str | None = Query(None, description="可选的页脚文本（用于报告风格图表）"),
    width: int = Query(1179, ge=640, le=2400),
    height: int | None = Query(None, ge=640, le=3200),
    luxury_theme: str | None = Query(None, description="可选的全局奢华主题名称或 'random'"),
    luxury_theme_seed: str | None = Query(None, description="可选的随机种子（用于 random 主题的可复现性）"),
    luxury_theme_intensity: float | None = Query(None, ge=0.0, le=2.0),
) -> Response:
    """GET 渲染端点 —— 通过 URL 查询参数发起渲染请求

        适用于浏览器直接访问、<img> 标签 src 嵌入、分享链接等场景。
        奢华主题相关参数会被提取到 data 字典中传递给后端管线。

    Args:
        legend_type: 必填，目标图表类型
        style: 样式变体，默认 "default"
        width/height: 输出尺寸（像素），有范围约束
        luxury_theme*: 奢华主题参数组（可选）

    Returns:
        图像二进制数据的 HTTP 响应（Content-Type: image/png 或 image/gif）
    """
    data: dict[str, Any] = {}
    # 将奢华主题参数从查询参数提取到 data 字典中
    if luxury_theme is not None:
        data["luxury_theme"] = luxury_theme
    if luxury_theme_seed is not None:
        data["luxury_theme_seed"] = luxury_theme_seed
    if luxury_theme_intensity is not None:
        data["luxury_theme_intensity"] = luxury_theme_intensity
    # 构建 RenderRequest 对象并委托给统一的响应处理函数
    request = RenderRequest(
        legend_type=legend_type,
        style=style,
        title=title,
        subtitle=subtitle,
        kicker=kicker,
        theme_label=theme_label,
        footer=footer,
        data=data,
        width=width,
        height=height,
    )
    return _render_response(request)


@app.post("/render")
def render_from_body(request: RenderRequest) -> Response:
    """POST 渲染端点 —— 通过 JSON Body 发起渲染请求

        适用于需要传递复杂自定义数据（如节点列表、流量数据等）的场景，
        或程序化批量调用的场景。请求体为完整的 RenderRequest JSON 对象。

    Args:
        request: Pydantic 自动解析并验证的渲染请求对象

    Returns:
        图像二进制数据的 HTTP 响应
    """
    return _render_response(request)


@app.post("/batch-generate", response_model=BatchGenerateSummary)
def batch_generate(request: BatchGenerateRequest) -> BatchGenerateSummary:
    """批量生成端点 —— 一次性生成所有内置图表类型的示例图像

        遍历所有已注册 Skill 的每种样式，生成完整的示例图片集，
        并输出质量评分统计。用于 CI/CD 中的视觉回归测试或示例图库构建。

    Args:
        request: 包含输出目录路径和项目根目录的批量生成配置

    Returns:
        批量生成的摘要信息（输出目录、图像总数、平均质量评分等）
    """
    project_root = Path(request.project_root) if request.project_root else Path.cwd()
    report = generate_all(output_dir=Path(request.output_dir), project_root=project_root)
    return BatchGenerateSummary(
        output_dir=report["output_dir"],
        log_dir=report["log_dir"],
        raw_image_dir=report["raw_image_dir"],
        image_count=report["image_count"],
        average_score=report["average_score"],
    )


# ========== 内部辅助函数 ==========


def _render_response(request: RenderRequest) -> Response:
    """统一渲染响应构造函数 —— 将 RenderResult 封装为带有完整 HTTP 头的 Response 对象

    设置的响应头包括：
    - Content-Type: 图像 MIME 类型（image/png 或 image/gif）
    - Content-Disposition: 内联展示 + 建议文件名（格式: {类型}-{样式}.{扩展名}）
    - X-Legend-Type: 实际使用的图表类型标识符（便于客户端日志追踪）
    - X-Legend-Style: 实际使用的样式名称

    Args:
        request: 已验证的渲染请求

    Returns:
        FastAPI Response 对象，body 为图像字节流
    """
    result = _render_or_http_error(request)
    filename = f"{result.legend_type}-{result.style}.{result.file_extension}"
    headers = {
        "Content-Disposition": f'inline; filename="{filename}"',
        "X-Legend-Type": result.legend_type,
        "X-Legend-Style": result.style,
    }
    return Response(content=result.content, media_type=result.media_type, headers=headers)


def _render_or_http_error(request: RenderRequest) -> RenderResult:
    """错误处理包装函数 —— 将注册表渲染异常转换为标准 HTTP 错误响应

    异常映射规则：
    - UnknownLegendTypeError → HTTP 404 Not Found（未知的图表类型）
    - UnknownStyleError → HTTP 400 Bad Request（未知的样式，附带允许的样式列表）
    - 其他异常 → 由 FastAPI 全局异常处理器捕获 → HTTP 500 Internal Server Error

    Args:
        request: 渲染请求对象

    Returns:
        成功时返回 RenderResult；失败时抛出 HTTPException 终止请求

    Raises:
        HTTPException(404): 当 legend_type 未注册时
        HTTPException(400): 当 style 不被对应渲染器支持时（detail 中包含 allowed_styles 列表）
    """
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

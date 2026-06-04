---
name: neo-legend-bar-chart
description: >-
  Maintain and tune the Neo Legend `bar_chart` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `bar_chart` 渲染器。当在 Neo_Legend_Project 中修改此图表的视觉样式、布局、数据映射、主题行为、示例图片、测试或生成的报表输出时使用。
---

# Luxury Bar Chart
# 华丽柱状图

## Renderer Contract
## 渲染器契约

- Legend type: `bar_chart` — 图例类型：`bar_chart`
- Renderer class: `BarChartSkill` — 渲染器类：`BarChartSkill`
- Source file: `src/neo_legend/bar_chart.py` — 源文件：`src/neo_legend/bar_chart.py`
- Default style: `glass_3d` — 默认样式：`glass_3d`
- Default size: `1179x1454` — 默认尺寸：`1179x1454`
- Media type: `image/png` — 媒体类型：`image/png`
- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`. — 报表头部字段：`title`、`subtitle`、`kicker`、`theme_label`、`footer` 或 `data.report_header`

## Supported Styles
## 支持的样式

| Style | Intent | Current sample output |
| --- | --- | --- |
| `glass_3d` | Glass-texture 3D bar chart with rounded bars, shadows and highlights. | `G:/echaet/bar_chart__glass_3d.png` |
| `neon_tubes` | Neon glow tube effect bar chart with multi-layer glowing borders. | `G:/echaet/bar_chart__neon_tubes.png` |
| `gradient_sky` | Sky-gradient sunset-themed bar chart with per-bar independent gradients. | `G:/echaet/bar_chart__gradient_sky.png` |
| `crystal_pillars` | Crystal pillar bar chart with refraction texture and golden labels. | `G:/echaet/bar_chart__crystal_pillars.png` |

| 样式 | 设计意图 | 当前示例输出 |
| --- | --- | --- |
| `glass_3d` | 玻璃质感3D柱状图，圆角柱体+阴影+高光。 | `G:/echaet/bar_chart__glass_3d.png` |
| `neon_tubes` | 霓虹灯管效果柱状图，多层发光边框。 | `G:/echaet/bar_chart__neon_tubes.png` |
| `gradient_sky` | 天空渐变日落主题柱状图，每根柱子独立渐变。 | `G:/echaet/bar_chart__gradient_sky.png` |
| `crystal_pillars` | 水晶柱柱状图，折射纹理+金色标签。 | `G:/echaet/bar_chart__crystal_pillars.png` |

## Data Contract
## 数据契约

### `glass_3d`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `neon_tubes`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `gradient_sky`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `crystal_pillars`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `bar_chart`. — 将此 Skill 视为 `bar_chart` 的产品级规范。
2. Read `src/neo_legend/bar_chart.py` only after this Skill does not answer the change. — 仅当此 Skill 无法回答变更时才阅读 `src/neo_legend/bar_chart.py`。
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`. — 保持渲染器的公开请求契约：`legend_type`、`style`、`title`、`subtitle`、`data`、`width` 和 `height`。
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values. — 优先使用可配置的 `data` 字段作为面向用户的调优旋钮，而非硬编码数值。
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference. — 在 `G:/echaet` 中重新生成受影响的示例图片，并与预期参考进行对比。
6. Update this Skill when a new input field, theme, style, or layout rule is added. — 当新增输入字段、主题、样式或布局规则时更新此 Skill。

## Tuning Notes
## 调优说明

- Keep visual changes scoped to this renderer unless shared helpers are required. — 将视觉变更限制在此渲染器范围内，除非需要共享辅助工具。

## Validation
## 验证

- Run focused render tests for this renderer first. — 首先运行此渲染器的专项渲染测试。
- Run `python -m pytest tests/test_report_header_text.py -q` when changing report headers. — 修改报表头部时运行 `python -m pytest tests/test_report_header_text.py -q`。
- Run `python -m pytest -q` before considering the change complete. — 在确认变更完成前运行 `python -m pytest -q`。
- Regenerate all outputs with: — 使用以下命令重新生成所有输出：

```powershell
$env:PYTHONPATH='src'; python -m neo_legend.batch_generate --output-dir G:\echaet --project-root E:\haochenkeji\Neo_Legend_Project
```

## Related Tests
## 相关测试

- `tests/test_api.py`
- `tests/test_bar_chart.py`
- `tests/test_business_report_charts.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`
- `tests/test_report_header_text.py`

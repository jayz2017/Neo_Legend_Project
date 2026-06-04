---
name: neo-legend-bubble-chart
description: >-
  Maintain and tune the Neo Legend `bubble_chart` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `bubble_chart` 渲染器。当在 Neo_Legend_Project 中修改此图表的视觉样式、布局、数据映射、主题行为、示例图片、测试或生成的报表输出时使用。
---

# Luxury Bubble Chart
# 华丽气泡图

## Renderer Contract
## 渲染器契约

- Legend type: `bubble_chart` — 图例类型：`bubble_chart`
- Renderer class: `BubbleChartSkill` — 渲染器类：`BubbleChartSkill`
- Source file: `src/neo_legend/bubble_chart.py` — 源文件：`src/neo_legend/bubble_chart.py`
- Default style: `water_drops` — 默认样式：`water_drops`
- Default size: `1179x1454` — 默认尺寸：`1179x1454`
- Media type: `image/png` — 媒体类型：`image/png`
- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`. — 报表头部字段：`title`、`subtitle`、`kicker`、`theme_label`、`footer` 或 `data.report_header`

## Supported Styles
## 支持的样式

| Style | Intent | Current sample output |
| --- | --- | --- |
| `water_drops` | Deep-blue teardrop bubbles with refraction highlights and soft shadows. | `G:/echaet/bubble_chart__water_drops.png` |
| `fireflies` | Glowing firefly particles with motion trails in a dark night. | `G:/echaet/bubble_chart__fireflies.png` |
| `galaxy_stars` | Stellar star-shaped markers with halos and a milky-way backdrop. | `G:/echaet/bubble_chart__galaxy_stars.png` |
| `crystal_orbs` | 3D crystal spheres with internal textures and rainbow dispersion. | `G:/echaet/bubble_chart__crystal_orbs.png` |

| 样式 | 设计意图 | 当前示例输出 |
| --- | --- | --- |
| `water_drops` | 深蓝色水滴气泡，折射高光+柔和阴影。 | `G:/echaet/bubble_chart__water_drops.png` |
| `fireflies` | 萤火虫效果粒子，暗夜中带运动轨迹的发光点。 | `G:/echaet/bubble_chart__fireflies.png` |
| `galaxy_stars` | 星形标记+光晕+银河背景。 | `G:/echaet/bubble_chart__galaxy_stars.png` |
| `crystal_orbs` | 3D水晶球体，内部纹理+彩虹色散。 | `G:/echaet/bubble_chart__crystal_orbs.png` |

## Data Contract
## 数据契约

### `water_drops`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `fireflies`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `galaxy_stars`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `crystal_orbs`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `bubble_chart`. — 将此 Skill 视为 `bubble_chart` 的产品级规范。
2. Read `src/neo_legend/bubble_chart.py` only after this Skill does not answer the change. — 仅当此 Skill 无法回答变更时才阅读 `src/neo_legend/bubble_chart.py`。
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
- `tests/test_bubble_chart.py`
- `tests/test_business_report_charts.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`
- `tests/test_report_header_text.py`

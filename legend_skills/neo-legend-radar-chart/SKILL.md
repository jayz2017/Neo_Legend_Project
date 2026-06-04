---
name: neo-legend-radar-chart
description: >-
  Maintain and tune the Neo Legend `radar_chart` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `radar_chart`（雷达图）渲染器。当需要在 Neo_Legend_Project 中更改此图表的视觉风格、布局、数据映射、主题行为、示例图片、测试或生成的报告输出时使用。
---

# Luxury Radar Chart
# 奢华雷达图

## Renderer Contract
## 渲染器契约

- Legend type: `radar_chart`（图例类型：雷达图）
- Renderer class: `RadarChartSkill`（渲染器类）
- Source file: `src/neo_legend/radar_chart.py`（源文件）
- Default style: `neon_glow`（默认样式：霓虹发光）
- Default size: `1200x1400`（默认尺寸）
- Media type: `image/png`（媒体类型）
- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`.（报告头部字段）

## Supported Styles
## 支持的样式

| Style | 样式 | Intent | 设计意图 | Current sample output | 当前示例输出 |
| --- | --- | --- | --- | --- | --- |
| `neon_glow` | 霓虹发光 | Neon glow effect with deep dark background and luminous lines. | 深色背景搭配发光线条的霓虹效果。 | `G:/echaet/radar_chart__neon_glow.png` | |
| `crystal_metal` | 晶体金属 | Crystal metallic texture with silver gradients and reflective highlights. | 银色渐变与反射高光的晶体金属质感。 | `G:/echaet/radar_chart__crystal_metal.png` | |
| `gradient_rainbow` | 彩虹渐变 | Rainbow gradient with HSV color transitions and star markers. | HSV 色彩过渡与星形标记的彩虹渐变。 | `G:/echaet/radar_chart__gradient_rainbow.png` | |

## Data Contract
## 数据契约

### `neon_glow`
- No required custom data; renderer can synthesize defaults.（无需自定义数据；渲染器可合成默认值。）

### `crystal_metal`
- No required custom data; renderer can synthesize defaults.（无需自定义数据；渲染器可合成默认值。）

### `gradient_rainbow`
- No required custom data; renderer can synthesize defaults.（无需自定义数据；渲染器可合成默认值。）

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `radar_chart`.（将此技能作为 `radar_chart` 的产品级规范。）
2. Read `src/neo_legend/radar_chart.py` only after this Skill does not answer the change.（仅在此技能无法回答变更时，再阅读源码文件。）
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`.（保持渲染器的公开请求契约不变。）
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values.（优先使用可配置的 `data` 字段作为用户调节旋钮，避免硬编码值。）
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference.（在 `G:/echaet` 中重新生成受影响的示例图片，并与预期参考进行对比。）
6. Update this Skill when a new input field, theme, style, or layout rule is added.（当新增输入字段、主题、样式或布局规则时，更新此技能文档。）

## Tuning Notes
## 调优说明

- Keep visual changes scoped to this renderer unless shared helpers are required.（将视觉变更限制在此渲染器内，除非需要共享辅助工具。）

## Validation
## 验证

- Run focused render tests for this renderer first.（首先运行此渲染器的专项渲染测试。）
- Run `python -m pytest tests/test_report_header_text.py -q` when changing report headers.（更改报告头时运行此测试。）
- Run `python -m pytest -q` before considering the change complete.（在认为变更完成前运行全量测试。）
- Regenerate all outputs with:（使用以下命令重新生成所有输出：）

```powershell
$env:PYTHONPATH='src'; python -m neo_legend.batch_generate --output-dir G:\echaet --project-root E:\haochenkeji\Neo_Legend_Project
```

## Related Tests
## 相关测试

- `tests/test_api.py`
- `tests/test_dual_radar_chart.py`
- `tests/test_radar_chart.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`
- `tests/test_report_header_text.py`

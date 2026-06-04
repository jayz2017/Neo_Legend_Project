---
name: neo-legend-combo-chart
description: >-
  Maintain and tune the Neo Legend `combo_chart` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `combo_chart` 渲染器。当在 Neo_Legend_Project 中修改此图表的视觉样式、布局、数据映射、主题行为、示例图片、测试或生成的报表输出时使用。
---

# Luxury Combo Chart
# 华丽组合图表

## Renderer Contract
## 渲染器契约

- Legend type: `combo_chart` — 图例类型：`combo_chart`
- Renderer class: `ComboChartSkill` — 渲染器类：`ComboChartSkill`
- Source file: `src/neo_legend/combo_chart.py` — 源文件：`src/neo_legend/combo_chart.py`
- Default style: `crystal_stream` — 默认样式：`crystal_stream`
- Default size: `1400x900` — 默认尺寸：`1400x900`
- Media type: `image/png` — 媒体类型：`image/png`
- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`. — 报表头部字段：`title`、`subtitle`、`kicker`、`theme_label`、`footer` 或 `data.report_header`

## Supported Styles
## 支持的样式

| Style | Intent | Current sample output |
| --- | --- | --- |
| `crystal_stream` | Crystal glow effect with ice-blue bars and golden bezier curve. | `G:/echaet/combo_chart__crystal_stream.png` |
| `neon_pulse` | Neon tube bars with pulse-ring data points and dashed trend line. | `G:/echaet/combo_chart__neon_pulse.png` |
| `sunset_gradient` | Warm sunset gradient bars with golden smooth spline curve. | `G:/echaet/combo_chart__sunset_gradient.png` |
| `ocean_depths` | Deep ocean blue bars with wave-modulated cyan line and bubbles. | `G:/echaet/combo_chart__ocean_depths.png` |

| 样式 | 设计意图 | 当前示例输出 |
| --- | --- | --- |
| `crystal_stream` | 水晶流光效果，冰蓝色柱体+金色贝塞尔曲线。 | `G:/echaet/combo_chart__crystal_stream.png` |
| `neon_pulse` | 霓虹灯管柱体，脉冲环数据点+虚线趋势线。 | `G:/echaet/combo_chart__neon_pulse.png` |
| `sunset_gradient` | 温暖日落渐变柱体，金色平滑样条曲线。 | `G:/echaet/combo_chart__sunset_gradient.png` |
| `ocean_depths` | 深海蓝色柱体，波浪调制青色线条+气泡。 | `G:/echaet/combo_chart__ocean_depths.png` |

## Data Contract
## 数据契约

### `crystal_stream`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `neon_pulse`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `sunset_gradient`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `ocean_depths`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `combo_chart`. — 将此 Skill 视为 `combo_chart` 的产品级规范。
2. Read `src/neo_legend/combo_chart.py` only after this Skill does not answer the change. — 仅当此 Skill 无法回答变更时才阅读 `src/neo_legend/combo_chart.py`。
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
- `tests/test_combo_chart.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`
- `tests/test_report_header_text.py`

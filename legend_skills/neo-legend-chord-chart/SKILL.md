---
name: neo-legend-chord-chart
description: >-
  Maintain and tune the Neo Legend `chord_chart` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `chord_chart` 渲染器。当在 Neo_Legend_Project 中修改此图表的视觉样式、布局、数据映射、主题行为、示例图片、测试或生成的报表输出时使用。
---

# Capital Flow Chord
# 资金流向弦图

## Renderer Contract
## 渲染器契约

- Legend type: `chord_chart` — 图例类型：`chord_chart`
- Renderer class: `ChordChartSkill` — 渲染器类：`ChordChartSkill`
- Source file: `src/neo_legend/business_report_charts.py` — 源文件：`src/neo_legend/business_report_charts.py`
- Default style: `capital_flows` — 默认样式：`capital_flows`
- Default size: `1200x1000` — 默认尺寸：`1200x1000`
- Media type: `image/png` — 媒体类型：`image/png`
- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`. — 报表头部字段：`title`、`subtitle`、`kicker`、`theme_label`、`footer` 或 `data.report_header`

## Supported Styles
## 支持的样式

| Style | Intent | Current sample output |
| --- | --- | --- |
| `capital_flows` | Circular capital flow chord report. | `G:/echaet/chord_chart__capital_flows.png` |
| `sector_rotation` | Sector rotation chord with muted institutional palette. | `G:/echaet/chord_chart__sector_rotation.png` |

| 样式 | 设计意图 | 当前示例输出 |
| --- | --- | --- |
| `capital_flows` | 圆形资金流向弦图报表。 | `G:/echaet/chord_chart__capital_flows.png` |
| `sector_rotation` | 板块轮动弦图，采用柔和机构配色。 | `G:/echaet/chord_chart__sector_rotation.png` |

## Data Contract
## 数据契约

### `capital_flows`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

### `sector_rotation`
- No required custom data; renderer can synthesize defaults. — 无需自定义数据；渲染器可合成默认值。

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `chord_chart`. — 将此 Skill 视为 `chord_chart` 的产品级规范。
2. Read `src/neo_legend/business_report_charts.py` only after this Skill does not answer the change. — 仅当此 Skill 无法回答变更时才阅读 `src/neo_legend/business_report_charts.py`。
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
- `tests/test_business_report_charts.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`
- `tests/test_report_header_text.py`

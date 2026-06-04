---
name: neo-legend-calendar-chart
description: >-
  Maintain and tune the Neo Legend `calendar_chart` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `calendar_chart` 渲染器。当在 Neo_Legend_Project 中修改此图表的视觉样式、布局、数据映射、主题行为、示例图片、测试或生成的报表输出时使用。
---

# Executive Calendar Chart
# 高管日历图

## Renderer Contract
## 渲染器契约

- Legend type: `calendar_chart` — 图例类型：`calendar_chart`
- Renderer class: `CalendarChartSkill` — 渲染器类：`CalendarChartSkill`
- Source file: `src/neo_legend/business_report_charts.py` — 源文件：`src/neo_legend/business_report_charts.py`
- Default style: `executive_month` — 默认样式：`executive_month`
- Default size: `1400x900` — 默认尺寸：`1400x900`
- Media type: `image/png` — 媒体类型：`image/png`
- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`. — 报表头部字段：`title`、`subtitle`、`kicker`、`theme_label`、`footer` 或 `data.report_header`

## Supported Styles
## 支持的样式

| Style | Intent | Current sample output |
| --- | --- | --- |
| `executive_month` | Commercial report calendar with event markers and KPI summary. | `G:/echaet/calendar_chart__executive_month.png` |
| `earnings_calendar` | Wall Street earnings and macro-event calendar layout. | `G:/echaet/calendar_chart__earnings_calendar.png` |

| 样式 | 设计意图 | 当前示例输出 |
| --- | --- | --- |
| `executive_month` | 商业报表日历，带事件标记和KPI汇总。 | `G:/echaet/calendar_chart__executive_month.png` |
| `earnings_calendar` | 华尔街财报与宏观事件日历布局。 | `G:/echaet/calendar_chart__earnings_calendar.png` |

## Data Contract
## 数据契约

### `executive_month`
- `days`: int value `31` — 天数：整数值 `31`
- `events`: list[11] of objects with keys: day, impact, type — 事件列表[11]，对象包含键：day（日期）、impact（影响）、type（类型）
- `month_label`: str value `May 2026` — 月份标签：字符串值 `May 2026`
- `start_weekday`: int value `4` — 起始星期：整数值 `4`

### `earnings_calendar`
- `days`: int value `31` — 天数：整数值 `31`
- `events`: list[11] of objects with keys: day, impact, type — 事件列表[11]，对象包含键：day（日期）、impact（影响）、type（类型）
- `month_label`: str value `May 2026` — 月份标签：字符串值 `May 2026`
- `start_weekday`: int value `4` — 起始星期：整数值 `4`

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `calendar_chart`. — 将此 Skill 视为 `calendar_chart` 的产品级规范。
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

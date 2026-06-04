---
name: neo-legend-coordinate
description: >-
  Maintain and tune the Neo Legend `coordinate` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `coordinate` 渲染器。当在 Neo_Legend_Project 中修改此图表的视觉样式、布局、数据映射、主题行为、示例图片、测试或生成的报表输出时使用。
---

# Coordinate Bubble Chart
# 坐标散点图

## Renderer Contract
## 渲染器契约

- Legend type: `coordinate` — 图例类型：`coordinate`
- Renderer class: `CoordinateSkill` — 渲染器类：`CoordinateSkill`
- Source file: `src/neo_legend/coordinate.py` — 源文件：`src/neo_legend/coordinate.py`
- Default style: `dark_bubble` — 默认样式：`dark_bubble`
- Default size: `1179x1463` — 默认尺寸：`1179x1463`
- Media type: `image/png` — 媒体类型：`image/png`
- Header fields: `title` and `subtitle` are the primary text overrides for this renderer. — 头部字段：`title` 和 `subtitle` 是此渲染器的主要文本覆盖字段。

## Supported Styles
## 支持的样式

| Style | Intent | Current sample output |
| --- | --- | --- |
| `dark_bubble` | Dark NBA scorer bubble chart with labels and average line. | `G:/echaet/coordinate__dark_bubble.png` |
| `gold_scorers` | Warmer scorer chart with stronger gold highlights. | `G:/echaet/coordinate__gold_scorers.png` |

| 样式 | 设计意图 | 当前示例输出 |
| --- | --- | --- |
| `dark_bubble` | 暗色NBA得分者气泡图，带标签和平均线。 | `G:/echaet/coordinate__dark_bubble.png` |
| `gold_scorers` | 更暖色调的得分者图表，金色高光更突出。 | `G:/echaet/coordinate__gold_scorers.png` |

## Data Contract
## 数据契约

### `dark_bubble`
- `points`: list[18] of objects with keys: label, size, x, y — 点位列表[18]，对象包含键：label（标签）、size（大小）、x、y

### `gold_scorers`
- `points`: list[18] of objects with keys: label, size, x, y — 点位列表[18]，对象包含键：label（标签）、size（大小）、x、y

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `coordinate`. — 将此 Skill 视为 `coordinate` 的产品级规范。
2. Read `src/neo_legend/coordinate.py` only after this Skill does not answer the change. — 仅当此 Skill 无法回答变更时才阅读 `src/neo_legend/coordinate.py`。
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
- `tests/test_coordinate_charts.py`
- `tests/test_edge_cases.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`

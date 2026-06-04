---
name: neo-legend-rose
description: >-
  Maintain and tune the Neo Legend `rose` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `rose`（玫瑰图）渲染器。当需要在 Neo_Legend_Project 中更改此图表的视觉风格、布局、数据映射、主题行为、示例图片、测试或生成的报告输出时使用。
---

# Rose Donut Chart
# 玫瑰环形图

## Renderer Contract
## 渲染器契约

- Legend type: `rose`（图例类型：玫瑰图）
- Renderer class: `RoseSkill`（渲染器类）
- Source file: `src/neo_legend/rose.py`（源文件）
- Default style: `proposal_comparison`（默认样式：提案对比）
- Default size: `1179x1459`（默认尺寸）
- Media type: `image/png`（媒体类型）
- Header fields: `title` and `subtitle` are the primary text overrides for this renderer.（头部字段：`title` 和 `subtitle` 是此渲染器的主要文本覆盖字段。）

## Supported Styles
## 支持的样式

| Style | 样式 | Intent | 设计意图 | Current sample output | 当前示例输出 |
| --- | --- | --- | --- | --- | --- |
| `proposal_comparison` | 提案对比 | Black-background current/proposed lottery donut comparison. | 黑底当前/提案乐透环形对比图。 | `G:/echaet/rose__proposal_comparison.png` | |
| `lottery_black` | 乐透黑底 | Single black-background rose donut chart. | 单一黑底玫瑰环形图。 | `G:/echaet/rose__lottery_black.png` | |

## Data Contract
## 数据契约

### `proposal_comparison`
- `current_values`: list[14]（当前值列表）
- `proposed_values`: list[18]（提案值列表）

### `lottery_black`
- `current_values`: list[14]（当前值列表）
- `proposed_values`: list[18]（提案值列表）

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `rose`.（将此技能作为 `rose` 的产品级规范。）
2. Read `src/neo_legend/rose.py` only after this Skill does not answer the change.（仅在此技能无法回答变更时，再阅读源码文件。）
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

- `tests/test_edge_cases.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`
- `tests/test_rose_and_table.py`

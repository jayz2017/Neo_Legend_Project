---
name: neo-legend-table
description: >-
  Maintain and tune the Neo Legend `table` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `table`（表格图）渲染器。当需要在 Neo_Legend_Project 中更改此图表的视觉风格、布局、数据映射、主题行为、示例图片、测试或生成的报告输出时使用。
---

# Heatmap Ranking Table
# 热力排名表格图

## Renderer Contract
## 渲染器契约

- Legend type: `table`（图例类型：表格图）
- Renderer class: `TableSkill`（渲染器类）
- Source file: `src/neo_legend/table.py`（源文件）
- Default style: `heatmap_light`（默认样式：热力图浅色）
- Default size: `1179x1481`（默认尺寸）
- Media type: `image/png`（媒体类型）
- Header fields: `title` and `subtitle` are the primary text overrides for this renderer.（头部字段：`title` 和 `subtitle` 是此渲染器的主要文本覆盖字段。）

## Supported Styles
## 支持的样式

| Style | 样式 | Intent | 设计意图 | Current sample output | 当前示例输出 |
| --- | --- | --- | --- | --- | --- |
| `heatmap_light` | 热力图浅色 | White-background ranking table with heat colored stat cells. | 白底排名表格，统计单元格使用热力色彩。 | `G:/echaet/table__heatmap_light.png` | |
| `scoreboard_dark` | 记分牌暗色 | Dark scoreboard-style table with high-contrast cells. | 暗色记分牌风格表格，高对比度单元格。 | `G:/echaet/table__scoreboard_dark.png` | |
| `league_standings_gradient` | 联赛排名渐变 | Single-line header table with configurable average-centered gradient columns. | 单行头部表格，可配置均值居中渐变列。 | `G:/echaet/table__league_standings_gradient.png` | |

## Data Contract
## 数据契约

### `heatmap_light`
- `rows`: list[15] of objects with keys: ast_tov, mpg, name, pts_created, team, team_color, ts（15 行对象列表，包含以下键：）

### `scoreboard_dark`
- `rows`: list[15] of objects with keys: ast_tov, mpg, name, pts_created, team, team_color, ts（15 行对象列表，包含以下键：）

### `league_standings_gradient`
- `average_row`: object with keys: def_rating, def_turnover_rate, efg, foul_rate, ft_rate, losses, net_rating, off_rating, opp_efg, opp_orb_rate, orb_rate, team, turnover_rate, wins（平均行对象，包含以下键：）
- `color_theme`: str value `random`（颜色主题，字符串值）
- `columns`: list[26] of objects with keys: format, key, label, width（26 列对象列表，包含以下键：）
- `gradient_columns`: object with keys: def_rating_rank, def_turnover_rank, efg_rank, foul_rank, ft_rank, net_rank, off_rating_rank, opp_efg_rank, opp_orb_rank, orb_rank, turnover_rank（渐变列对象，包含排名键：）
- `header_groups`: list[3] of objects with keys: columns, label, show_children（3 个头部分组对象列表，包含以下键：）
- `header_height`: float value `0.11`（头部高度，浮点值）
- `rows`: list[14] of objects with keys: def_rating, def_rating_rank, def_turnover_rank, def_turnover_rate, efg, efg_rank, foul_rank, foul_rate, ft_rank, ft_rate, losses, net_rank, net_rating, off_rating, off_rating_rank, opp_efg, opp_efg_rank, opp_orb_rank, opp_orb_rate, orb_rank, orb_rate, rank, team, turnover_rank, turnover_rate, wins（14 行数据对象列表，包含完整数据键：）

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `table`.（将此技能作为 `table` 的产品级规范。）
2. Read `src/neo_legend/table.py` only after this Skill does not answer the change.（仅在此技能无法回答变更时，再阅读源码文件。）
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`.（保持渲染器的公开请求契约不变。）
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values.（优先使用可配置的 `data` 字段作为用户调节旋钮，避免硬编码值。）
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference.（在 `G:/echaet` 中重新生成受影响的示例图片，并与预期参考进行对比。）
6. Update this Skill when a new input field, theme, style, or layout rule is added.（当新增输入字段、主题、样式或布局规则时，更新此技能文档。）

## Tuning Notes
## 调优说明

- `header_groups` controls merged parent headers and child headers.（`header_groups` 控制合并父级头部与子级头部。）
- `gradient_columns` or `gradients` controls average-centered cell color scaling.（`gradient_columns` 或 `gradients` 控制均值居中的单元格颜色缩放。）
- `left_image` or `left_image_path` composes an external image on the left side.（`left_image` 或 `left_image_path` 在左侧合成外部图片。）

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
- `tests/test_edge_cases.py`
- `tests/test_luxury_theme.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`
- `tests/test_rose_and_table.py`

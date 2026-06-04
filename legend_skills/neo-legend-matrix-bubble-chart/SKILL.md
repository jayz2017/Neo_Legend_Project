---
name: neo-legend-matrix-bubble-chart
description: >-
  Maintain and tune the Neo Legend `matrix_bubble_chart` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `matrix_bubble_chart` 渲染器。当在 Neo_Legend_Project 中更改此图表的视觉样式、布局、数据映射、主题行为、示例图像、测试或生成的报告输出时使用。
---

# Correlation Bubble Matrix
# 相关性气泡矩阵图

## Renderer Contract
## 渲染器契约

- Legend type: `matrix_bubble_chart` | 图例类型：`matrix_bubble_chart`
- Renderer class: `MatrixBubbleChartSkill` | 渲染器类：`MatrixBubbleChartSkill`
- Source file: `src/neo_legend/business_report_charts.py` | 源文件：`src/neo_legend/business_report_charts.py`
- Default style: `correlation_board` | 默认样式：`correlation_board`（相关性面板）
- Default size: `1400x900` | 默认尺寸：`1400x900`
- Media type: `image/png` | 媒体类型：`image/png`
- Report header fields: `title`, `subtitle`, `kicker`, `theme_label`, `footer`, or `data.report_header`. | 报告标题字段：`title`、`subtitle`、`kicker`、`theme_label`、`footer` 或 `data.report_header`。

## Supported Styles
## 支持的样式

| Style | 样式 | Intent | 设计意图 | Current sample output | 当前示例输出 |
| --- | --- | --- | --- | --- | --- |
| `correlation_board` | 相关性面板 | Wall Street correlation matrix with sized bubbles. | 华尔街风格相关性矩阵，带尺寸气泡。 | `G:/echaet/matrix_bubble_chart__correlation_board.png` |
| `risk_heat_matrix` | 风险热力矩阵 | Risk heat matrix with diverging impact colors. | 风险热力矩阵，带发散影响颜色。 | `G:/echaet/matrix_bubble_chart__risk_heat_matrix.png` |

## Data Contract
## 数据契约

### `correlation_board`
### 相关性面板
- No required custom data; renderer can synthesize defaults. | 无需自定义数据；渲染器可以合成默认值。

### `risk_heat_matrix`
### 风险热力矩阵
- No required custom data; renderer can synthesize defaults. | 无需自定义数据；渲染器可以合成默认值。

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `matrix_bubble_chart`. | 将此技能视为 `matrix_bubble_chart` 的产品级规范。
2. Read `src/neo_legend/business_report_charts.py` only after this Skill does not answer the change. | 仅在此技能无法解答变更时，才阅读 `src/neo_legend/business_report_charts.py`。
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`. | 保持渲染器的公共请求契约：`legend_type`、`style`、`title`、`subtitle`、`data`、`width` 和 `height`。
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values. | 优先使用可配置的 `data` 字段作为用户面向的调优旋钮，而不是硬编码值。
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference. | 在 `G:/echaet` 中重新生成受影响的示例图像，并与预期参考进行对比。
6. Update this Skill when a new input field, theme, style, or layout rule is added. | 当添加新的输入字段、主题、样式或布局规则时，更新此技能。

## Tuning Notes
## 调优说明

- Bubble size encodes absolute magnitude; color encodes direction. | 气泡大小编码绝对幅度；颜色编码方向。
- The report header supports `title`, `subtitle`, `kicker`, `theme_label`, and `footer`. | 报告标题支持 `title`、`subtitle`、`kicker`、`theme_label` 和 `footer`。

## Validation
## 验证

- Run focused render tests for this renderer first. | 首先运行针对此渲染器的聚焦渲染测试。
- Run `python -m pytest tests/test_report_header_text.py -q` when changing report headers. | 更改报告标题时，运行 `python -m pytest tests/test_report_header_text.py -q`。
- Run `python -m pytest -q` before considering the change complete. | 在认为变更完成之前，运行 `python -m pytest -q`。
- Regenerate all outputs with: | 使用以下命令重新生成所有输出：

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

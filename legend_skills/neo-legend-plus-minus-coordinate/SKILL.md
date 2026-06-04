---
name: neo-legend-plus-minus-coordinate
description: >-
  Maintain and tune the Neo Legend `plus_minus_coordinate` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `plus_minus_coordinate` 渲染器。当在 Neo_Legend_Project 中更改此图表的视觉样式、布局、数据映射、主题行为、示例图像、测试或生成的报告输出时使用。
---

# Positive Negative Coordinate Chart
# 正负坐标图

## Renderer Contract
## 渲染器契约

- Legend type: `plus_minus_coordinate` | 图例类型：`plus_minus_coordinate`
- Renderer class: `PlusMinusCoordinateSkill` | 渲染器类：`PlusMinusCoordinateSkill`
- Source file: `src/neo_legend/plus_minus_coordinate.py` | 源文件：`src/neo_legend/plus_minus_coordinate.py`
- Default style: `paper_quadrant` | 默认样式：`paper_quadrant`（纸质象限）
- Default size: `1179x1174` | 默认尺寸：`1179x1174`
- Media type: `image/png` | 媒体类型：`image/png`
- Header fields: `title` and `subtitle` are the primary text overrides for this renderer. | 标题字段：`title` 和 `subtitle` 是此渲染器的主要文本覆盖字段。

## Supported Styles
## 支持的样式

| Style | 样式 | Intent | 设计意图 | Current sample output | 当前示例输出 |
| --- | --- | --- | --- | --- | --- |
| `paper_quadrant` | 纸质象限 | Light textured efficiency quadrant chart with diagonal benchmark. | 浅色纹理效率象限图，带对角基准线。 | `G:/echaet/plus_minus_coordinate__paper_quadrant.png` |
| `clean_quadrant` | 干净象限 | Cleaner quadrant chart with stronger team markers. | 更简洁的象限图，带更强的球队标记。 | `G:/echaet/plus_minus_coordinate__clean_quadrant.png` |

## Data Contract
## 数据契约

### `paper_quadrant`
### 纸质象限
- `points`: list[13] of objects with keys: color, label, note, x, y | 点位：包含键 color、label、note、x、y 的对象列表[13]

### `clean_quadrant`
### 干净象限
- `points`: list[13] of objects with keys: color, label, note, x, y | 点位：包含键 color、label、note、x、y 的对象列表[13]

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `plus_minus_coordinate`. | 将此技能视为 `plus_minus_coordinate` 的产品级规范。
2. Read `src/neo_legend/plus_minus_coordinate.py` only after this Skill does not answer the change. | 仅在此技能无法解答变更时，才阅读 `src/neo_legend/plus_minus_coordinate.py`。
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`. | 保持渲染器的公共请求契约：`legend_type`、`style`、`title`、`subtitle`、`data`、`width` 和 `height`。
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values. | 优先使用可配置的 `data` 字段作为用户面向的调优旋钮，而不是硬编码值。
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference. | 在 `G:/echaet` 中重新生成受影响的示例图像，并与预期参考进行对比。
6. Update this Skill when a new input field, theme, style, or layout rule is added. | 当添加新的输入字段、主题、样式或布局规则时，更新此技能。

## Tuning Notes
## 调优说明

- Keep visual changes scoped to this renderer unless shared helpers are required. | 将视觉变更限制在此渲染器范围内，除非需要共享辅助函数。

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

- `tests/test_coordinate_charts.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`

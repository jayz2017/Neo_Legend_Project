---
name: neo-legend-court-shot-animation
description: >-
  Maintain and tune the Neo Legend `court_shot_animation` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `court_shot_animation` 渲染器。当在 Neo_Legend_Project 中更改此图表的视觉样式、布局、数据映射、主题行为、示例图像、测试或生成的报告输出时使用。
---

# Animated Court Shooting Terrain
# 动画球场投篮地形图

## Renderer Contract
## 渲染器契约

- Legend type: `court_shot_animation` | 图例类型：`court_shot_animation`
- Renderer class: `AnimatedCourtShotSkill` | 渲染器类：`AnimatedCourtShotSkill`
- Source file: `src/neo_legend/animated_court_shot.py` | 源文件：`src/neo_legend/animated_court_shot.py`
- Default style: `arena_arc` | 默认样式：`arena_arc`（竞技场弧线）
- Default size: `1179x1165` | 默认尺寸：`1179x1165`
- Media type: `image/gif` | 媒体类型：`image/gif`
- Header fields: `title` and `subtitle` are the primary text overrides for this renderer. | 标题字段：`title` 和 `subtitle` 是此渲染器的主要文本覆盖字段。

## Supported Styles
## 支持的样式

| Style | 样式 | Intent | 设计意图 | Current sample output | 当前示例输出 |
| --- | --- | --- | --- | --- | --- |
| `arena_arc` | 竞技场弧线 | Black and gold 3D arena view with animated shot arcs. | 黑金3D竞技场视图，带动画投篮弧线。 | `G:/echaet/court_shot_animation__arena_arc.gif` |
| `pulse` | 脉冲 | Animated pulse over the shooting terrain. | 投篮地形上的动画脉冲效果。 | `G:/echaet/court_shot_animation__pulse.gif` |
| `sweep` | 扫描 | Animated progressive reveal over shot clusters. | 投篮聚类上的动画渐进式揭示效果。 | `G:/echaet/court_shot_animation__sweep.gif` |

## Data Contract
## 数据契约

### `arena_arc`
### 竞技场弧线
- `frame_count`: int value `14` | 帧数：整数值 `14`
- `seed`: int value `31` | 随机种子：整数值 `31`
- `shot_count`: int value `430` | 投篮次数：整数值 `430`

### `pulse`
### 脉冲
- `frame_count`: int value `10` | 帧数：整数值 `10`
- `seed`: int value `31` | 随机种子：整数值 `31`
- `shot_count`: int value `430` | 投篮次数：整数值 `430`

### `sweep`
### 扫描
- `frame_count`: int value `10` | 帧数：整数值 `10`
- `seed`: int value `31` | 随机种子：整数值 `31`
- `shot_count`: int value `430` | 投篮次数：整数值 `430`

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `court_shot_animation`. | 将此技能视为 `court_shot_animation` 的产品级规范。
2. Read `src/neo_legend/animated_court_shot.py` only after this Skill does not answer the change. | 仅在此技能无法解答变更时，才阅读 `src/neo_legend/animated_court_shot.py`。
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`. | 保持渲染器的公共请求契约：`legend_type`、`style`、`title`、`subtitle`、`data`、`width` 和 `height`。
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values. | 优先使用可配置的 `data` 字段作为用户面向的调优旋钮，而不是硬编码值。
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference. | 在 `G:/echaet` 中重新生成受影响的示例图像，并与预期参考进行对比。
6. Update this Skill when a new input field, theme, style, or layout rule is added. | 当添加新的输入字段、主题、样式或布局规则时，更新此技能。

## Tuning Notes
## 调优说明

- `sweep` must reveal shots cumulatively by data order, not by left-to-right masking. | `sweep` 必须按数据顺序累积显示投篮，而不是通过从左到右的遮罩方式。
- Keep GIF frame count, duration, and data progression readable before changing effects. | 在更改效果之前，保持 GIF 帧数、持续时间和数据进度的可读性。

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

- `tests/test_animated_court_shot.py`
- `tests/test_api.py`
- `tests/test_batch_generate.py`
- `tests/test_luxury_theme.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`

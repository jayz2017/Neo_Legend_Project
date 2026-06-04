---
name: neo-legend-court-shot
description: >-
  Maintain and tune the Neo Legend `court_shot` renderer. Use when changing this chart's visual style, layout, data mapping, theme behavior, sample image, tests, or generated report output in Neo_Legend_Project.
  维护和调优 Neo Legend `court_shot` 渲染器。当在 Neo_Legend_Project 中修改此图表的视觉样式、布局、数据映射、主题行为、示例图片、测试或生成的报表输出时使用。
---

# Court Shooting Terrain
# 球场投射地形图

## Renderer Contract
## 渲染器契约

- Legend type: `court_shot` — 图例类型：`court_shot`
- Renderer class: `CourtShotSkill` — 渲染器类：`CourtShotSkill`
- Source file: `src/neo_legend/court_shot.py` — 源文件：`src/neo_legend/court_shot.py`
- Default style: `terrain` — 默认样式：`terrain`
- Default size: `1179x1454` — 默认尺寸：`1179x1454`
- Media type: `image/png` — 媒体类型：`image/png`
- Header fields: `title` and `subtitle` are the primary text overrides for this renderer. — 头部字段：`title` 和 `subtitle` 是此渲染器的主要文本覆盖字段。

## Supported Styles
## 支持的样式

| Style | Intent | Current sample output |
| --- | --- | --- |
| `terrain` | Dark half-court shooting terrain with glowing efficiency zones. | `G:/echaet/court_shot__terrain.png` |
| `points_location` | Dark teal total-points-by-location hex map. | `G:/echaet/court_shot__points_location.png` |
| `kobe_shots` | White shot chart with made, missed, and assisted basketball markers. | `G:/echaet/court_shot__kobe_shots.png` |
| `hex` | Hex-bin shot profile with red, cream, blue zone colors. | `G:/echaet/court_shot__hex.png` |
| `zone` | Annotated zone shot map with light boundaries and point clusters. | `G:/echaet/court_shot__zone.png` |

| 样式 | 设计意图 | 当前示例输出 |
| --- | --- | --- |
| `terrain` | 暗色半场投射地形图，带发光效率区域。 | `G:/echaet/court_shot__terrain.png` |
| `points_location` | 深青色按位置总分六边形热力图。 | `G:/echaet/court_shot__points_location.png` |
| `kobe_shots` | 白色投篮图表，含命中、未命中和助攻标记。 | `G:/echaet/court_shot__kobe_shots.png` |
| `hex` | 六边形分箱投篮分布图，红/米色/蓝区域配色。 | `G:/echaet/court_shot__hex.png` |
| `zone` | 带标注的区域投篮地图，浅色边界+得分聚类。 | `G:/echaet/court_shot__zone.png` |

## Data Contract
## 数据契约

### `terrain`
- `seed`: int value `11` — 随机种子：整数值 `11`
- `shot_count`: int value `620` — 投篮次数：整数值 `620`

### `points_location`
- `max_points`: int value `800` — 最大分数：整数值 `800`
- `scoring_zones`: list[6] of objects with keys: center, count, name, points_per_event, spread — 得分区域列表[6]，对象包含键：center（中心）、count（数量）、name（名称）、points_per_event（每次事件得分）、spread（分布范围）
- `seed`: int value `2021` — 随机种子：整数值 `2021`

### `kobe_shots`
- `seed`: int value `11` — 随机种子：整数值 `11`
- `shot_count`: int value `620` — 投篮次数：整数值 `620`

### `hex`
- `seed`: int value `11` — 随机种子：整数值 `11`
- `shot_count`: int value `620` — 投篮次数：整数值 `620`

### `zone`
- `seed`: int value `11` — 随机种子：整数值 `11`
- `shot_count`: int value `620` — 投篮次数：整数值 `620`

## Modification Workflow
## 修改工作流

1. Treat this Skill as the product-level spec for `court_shot`. — 将此 Skill 视为 `court_shot` 的产品级规范。
2. Read `src/neo_legend/court_shot.py` only after this Skill does not answer the change. — 仅当此 Skill 无法回答变更时才阅读 `src/neo_legend/court_shot.py`。
3. Preserve the renderer's public request contract: `legend_type`, `style`, `title`, `subtitle`, `data`, `width`, and `height`. — 保持渲染器的公开请求契约：`legend_type`、`style`、`title`、`subtitle`、`data`、`width` 和 `height`。
4. Prefer configurable `data` fields for user-facing tuning knobs instead of hard-coding values. — 优先使用可配置的 `data` 字段作为面向用户的调优旋钮，而非硬编码数值。
5. Regenerate the affected sample image in `G:/echaet` and compare it with the intended reference. — 在 `G:/echaet` 中重新生成受影响的示例图片，并与预期参考进行对比。
6. Update this Skill when a new input field, theme, style, or layout rule is added. — 当新增输入字段、主题、样式或布局规则时更新此 Skill。

## Tuning Notes
## 调优说明

- `points_location` expects scoring zones; higher accumulated points must render brighter. — `points_location` 期望得分区域数据；累积分数越高渲染亮度越亮。
- Use court geometry helpers in `src/neo_legend/_court.py` for shot placement changes. — 投篮位置变更时请使用 `src/neo_legend/_court.py` 中的球场几何辅助工具。

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

- `tests/test_animated_court_shot.py`
- `tests/test_api.py`
- `tests/test_batch_generate.py`
- `tests/test_court_shot.py`
- `tests/test_diagnostics.py`
- `tests/test_dual_court_shot.py`
- `tests/test_edge_cases.py`
- `tests/test_luxury_theme.py`
- `tests/test_registry.py`
- `tests/test_renderers.py`

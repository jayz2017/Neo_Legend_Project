# Neo Legend 绘图服务计划书

## Project: Neo Legend FastAPI 图例绘制服务

**Goal**: 基于 README 中的参考图，构建一个 Python/FastAPI 绘图接口，能够按图例类型和样式自动选择独立 renderer skill，输出 PNG/GIF 图像，并覆盖完整测试用例。

**Timeline**: 3 周交付可用版本，后续按图例相似度持续迭代。

**Team**: 1 名后端/可视化工程师，1 名测试工程师，1 名设计/数据可视化评审。

**Constraints**: 参考图来自静态图片，当前阶段只能还原版式和视觉风格，无法精确复刻原作者字体、球员头像、队标素材和真实数据版权素材。

---

## Success Criteria

| Criteria | Done 标准 |
|---|---|
| FastAPI 服务可运行 | `uvicorn neo_legend.main:app --app-dir src` 可启动，接口返回图片 |
| 类型/样式参数可用 | `/render` 支持 `legend_type` 和 `style` 参数 |
| 自动组件选择 | registry 根据 `legend_type` 自动路由到对应 skill |
| 独立 skills | 每类图例有独立模块，后续可单独扩展、替换和测试 |
| 测试覆盖 | API、registry、全部图例类型和样式渲染均有 pytest 用例 |
| 视觉基线 | 默认样式匹配参考图的黑白/坐标/玫瑰/热力表等主要布局特征 |

---

## Deliverables

| Deliverable | Description |
|---|---|
| FastAPI 应用 | `src/neo_legend/main.py` 暴露健康检查、类型列表、绘图接口 |
| Renderer Registry | `src/neo_legend/registry.py` 负责 skill 注册、查找和自动选择 |
| 独立 Renderer Skills | 球场投射图、双球场投射图、动态图、坐标图、正负坐标图、玫瑰图、表格图 |
| 构建配置 | `pyproject.toml`、`requirements.txt`、Python `.gitignore` |
| 测试套件 | `tests/` 下覆盖接口、组件选择、图片格式和错误分支 |
| 项目计划书 | 当前文件，作为开发、验收和后续迭代依据 |

---

## Milestones

| # | Milestone | Target Date | Owner | Success Criteria |
|---|---|---|---|---|
| 1 | 架构与合同冻结 | 第 1 周第 2 天 | 后端工程师 | API schema、legend_type、style、registry 合同明确 |
| 2 | 首版 renderer skills 完成 | 第 1 周第 5 天 | 后端工程师 | 7 类图例均可输出图片 |
| 3 | 测试和构建完成 | 第 2 周第 3 天 | 测试工程师 | pytest 覆盖全部图例类型、样式和错误分支 |
| 4 | 视觉评审与调优 | 第 2 周第 5 天 | 设计评审 | 主要版式、配色、密度、标题层级通过评审 |
| 5 | 数据接入与发布准备 | 第 3 周第 5 天 | 全员 | 文档、部署方式、真实数据适配策略完成 |

---

## Phase 1: 架构设计与接口合同（第 1 周）

| Task | Effort | Owner | Depends On | Done Criteria |
|---|---:|---|---|---|
| 梳理 README 图例类型 | 2h | 后端工程师 | - | 形成 7 类 `legend_type` 清单 |
| 定义请求模型 | 3h | 后端工程师 | 图例类型清单 | `RenderRequest` 包含 `legend_type`、`style`、`title`、`subtitle`、`data`、尺寸参数 |
| 定义 renderer skill 基类 | 4h | 后端工程师 | 请求模型 | skill 统一暴露 metadata、style resolution、render |
| 定义 registry 自动选择 | 4h | 后端工程师 | skill 基类 | 输入类型可自动选择组件，未知类型返回明确错误 |
| 定义输出合同 | 2h | 后端工程师 | 请求模型 | PNG/GIF 的 media type、headers、错误码明确 |

**Total Effort**: 15h

---

## Phase 2: 图例 renderer 实现（第 1-2 周）

| Task | Effort | Owner | Depends On | Done Criteria |
|---|---:|---|---|---|
| 公共绘图工具 | 6h | 后端工程师 | Phase 1 | Matplotlib canvas、PNG 输出、尺寸归一化可复用 |
| 球场绘制工具 | 6h | 后端工程师 | 公共绘图工具 | 半场线、篮筐、三分线、油漆区可复用 |
| 球场投射图 skill | 8h | 后端工程师 | 球场绘制工具 | 支持 terrain、hex、zone 样式 |
| 双球场投射图 skill | 6h | 后端工程师 | 球场绘制工具 | 支持上下赛季对比布局 |
| 动态球场投射图 skill | 6h | 后端工程师 | 球场投射图 skill | 输出 GIF，脉冲/扫描样式可选 |
| 坐标图 skill | 6h | 后端工程师 | 公共绘图工具 | 支持深色气泡散点风格 |
| 正负坐标图 skill | 6h | 后端工程师 | 公共绘图工具 | 支持纸张象限、对角线和球队标记 |
| 玫瑰图 skill | 5h | 后端工程师 | 公共绘图工具 | 支持单图/方案对比 donut rose 图 |
| 表格图 skill | 6h | 后端工程师 | 公共绘图工具 | 支持热力表、亮色榜单样式 |

**Total Effort**: 55h

---

## Phase 3: 测试、质量和验收（第 2 周）

| Task | Effort | Owner | Depends On | Done Criteria |
|---|---:|---|---|---|
| registry 单元测试 | 3h | 测试工程师 | Phase 2 | 类型列表、自动选择、未知类型覆盖 |
| renderer 参数化测试 | 5h | 测试工程师 | Phase 2 | 每个 skill 的每个 style 都可生成有效图片 |
| API 测试 | 4h | 测试工程师 | FastAPI 应用 | GET/POST `/render`、`/legend-types`、错误分支覆盖 |
| 图片格式校验 | 3h | 测试工程师 | renderer 测试 | PNG/GIF 可被 PIL 读取，尺寸满足请求 |
| lint/格式检查 | 2h | 后端工程师 | 测试完成 | ruff 无关键问题 |
| 视觉抽检 | 6h | 设计评审 | renderer 完成 | 输出图与参考图在版式、配色、密度上接近 |

**Total Effort**: 23h

---

## Phase 4: 数据与部署扩展（第 3 周）

| Task | Effort | Owner | Depends On | Done Criteria |
|---|---:|---|---|---|
| 真实数据 schema 设计 | 6h | 后端工程师 | API 稳定 | 各 skill 的 `data` 字段支持业务数据 |
| 素材策略确认 | 4h | 设计评审 | 视觉抽检 | 球队 logo、球员头像、字体授权路径明确 |
| Docker/CI 扩展 | 6h | 后端工程师 | 构建配置 | 可容器化启动，CI 可跑测试 |
| 性能基准 | 4h | 后端工程师 | 数据接入 | 单张图生成耗时、内存峰值有基线 |
| 发布文档 | 4h | 全员 | 部署扩展 | 部署、接口、示例请求和错误码说明完成 |

**Total Effort**: 24h

---

## Dependencies Map

```text
README 分析
  -> API 请求模型
  -> BaseLegendSkill
  -> Registry 自动选择
  -> 各类 Renderer Skills
  -> API 接口
  -> 测试套件
  -> 视觉验收
  -> 部署扩展
```

**Critical Path**: API 请求模型 -> BaseLegendSkill -> Registry -> Renderer Skills -> API 测试 -> 视觉验收。

---

## Legend Type Matrix

| legend_type | 默认 style | 输出 | 参考 README 类型 | Skill 模块 |
|---|---|---|---|---|
| `court_shot` | `terrain` | PNG | 球场投射图 | `court_shot.py` |
| `dual_court_shot` | `year_over_year` | PNG | 双球场投射图 | `dual_court_shot.py` |
| `court_shot_animation` | `pulse` | GIF | 球场投射动态图 | `animated_court_shot.py` |
| `coordinate` | `dark_bubble` | PNG | 坐标图 | `coordinate.py` |
| `plus_minus_coordinate` | `paper_quadrant` | PNG | 正负坐标图 | `plus_minus_coordinate.py` |
| `rose` | `proposal_comparison` | PNG | 玫瑰图 | `rose.py` |
| `table` | `heatmap_light` | PNG | 表格图 | `table.py` |

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| 参考图无结构化数据 | High | High | 首版使用可替换示例数据，后续把 `data` schema 明确化 |
| 版权素材缺失 | Medium | High | 使用占位标记/文字，不内置真实队标和头像 |
| 视觉还原度主观 | Medium | Medium | 建立视觉评审清单：背景、标题、布局、密度、色带、标签层级 |
| Matplotlib 字体差异 | Medium | Medium | 使用通用字体并允许后续通过样式配置注入字体 |
| GIF 生成性能 | Medium | Medium | 限制帧数和尺寸上限，后续增加缓存 |
| 单接口参数过多 | Low | Medium | POST 使用 JSON body，GET 保留基础预览参数 |

---

## Resource Allocation

| Role | Hours/Week | Key Responsibilities |
|---|---:|---|
| 后端/可视化工程师 | 30-40h | API、registry、skills、构建配置、性能 |
| 测试工程师 | 15-20h | pytest、接口测试、图片格式校验、回归套件 |
| 设计/数据可视化评审 | 6-10h | 参考图拆解、视觉验收、样式调优建议 |

---

## Acceptance Checklist

- [x] 项目有 Python 构建配置。
- [x] FastAPI 暴露绘图接口。
- [x] `legend_type` 参数可指定图例类型。
- [x] `style` 参数可指定图例样式。
- [x] registry 自动选择对应 skill。
- [x] 每类图例有独立 skill 模块。
- [x] 测试覆盖全部图例类型和样式。
- [ ] 真实业务数据 schema 完成。
- [ ] 真实 logo、头像、字体授权素材接入。
- [ ] 视觉相似度建立人工或自动化基准。


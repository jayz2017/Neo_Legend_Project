# Tasks

## 阶段 1: 核心图表 Skills 实现（可并行）✅ 全部完成

- [x] Task 1: 实现 RadarSkill（华丽雷达图 - 3种样式）
  - [x] 1.1 创建 `src/neo_legend/skills/radar_chart.py`
  - [x] 1.2 实现雷达图核心绘制逻辑（极坐标系统、多边形网格）
  - [x] 1.3 实现 `neon_glow` 样式：霓虹发光效果 ✅
  - [x] 1.4 实现 `crystal_metal` 样式：晶体金属质感 ✅
  - [x] 1.5 实现 `gradient_rainbow` 样式：彩虹渐变 ✅
  - [x] 1.6 支持自定义数据输入（categories + datasets）
  - [x] 1.7 添加标题、副标题和图例系统

- [x] Task 2: 实现 DualRadarSkill（双雷达对比图 - 3种样式）
  - [x] 2.1 创建 `src/neo_legend/skills/dual_radar_chart.py`
  - [x] 2.2 实现左右对称双面板布局
  - [x] 2.3 实现 `versus_battle` 样式：对抗模式 ✅
  - [x] 2.4 实现 `mirror_compare` 样式：镜像对比 ✅
  - [x] 2.5 实现 `evolution_track` 样式：进化轨迹 ✅
  - [x] 2.6 自动计算并显示最大差异维度标签

- [x] Task 3: 实现 BarChartSkill（华丽柱状图 - 4种样式）
  - [x] 3.1 创建 `src/neo_legend/skills/bar_chart.py`
  - [x] 3.2 实现圆角矩形柱体绘制
  - [x] 3.3 实现 `glass_3d` 样式：玻璃质感 3D ✅
  - [x] 3.4 实现 `neon_tubes` 样式：霓虹灯管 ✅
  - [x] 3.5 实现 `gradient_sky` 样式：天空渐变 ✅
  - [x] 3.6 实现 `crystal_pillars` 样式：水晶柱状图 ✅
  - [x] 3.7 支持分组/堆叠/瀑布图模式

- [x] Task 4: 实现 ComboChartSkill（柱状+折线组合 - 4种样式）
  - [x] 4.1 创建 `src/neo_legend/skills/combo_chart.py`
  - [x] 4.2 实现双 Y 轴布局（twinx）
  - [x] 4.3 实现 `crystal_stream` 样式：水晶流光 ✅
  - [x] 4.4 实现 `neon_pulse` 样式：霓虹脉冲 ✅
  - [x] 4.5 实现 `sunset_gradient` 样式：日落渐变 ✅
  - [x] 4.6 实现 `ocean_depths` 样式：海洋深度 ✅
  - [x] 4.7 关键节点自动标注

- [x] Task 5: 实现 BubbleChartSkill（华丽水滴图 - 4种样式）
  - [x] 5.1 创建 `src/neo_legend/skills/bubble_chart.py`
  - [x] 5.2 实现水滴形状 marker（自定义 Path）
  - [x] 5.3 实现 `water_drops` 样式：水滴气泡 ✅
  - [x] 5.4 实现 `fireflies` 样式：萤火虫效果 ✅
  - [x] 5.5 实现 `galaxy_stars` 样式：星空银河 ✅
  - [x] 5.6 实现 `crystal_orbs` 样式：水晶球体 ✅
  - [x] 5.7 实现气泡防重叠算法

- [x] Task 6: 实现 SankeySkill（华丽桑基图 - 4种样式）
  - [x] 6.1 创建 `src/neo_legend/skills/sankey_chart.py`
  - [x] 6.2 使用自定义 Bezier 曲线绘制流带
  - [x] 6.3 实现 `neon_streams` 样式：霓虹流光 ✅
  - [x] 6.4 实现 `energy_flow` 样式：能量流动 ✅
  - [x] 6.5 实现 `crystal_rivers` 样式：晶体河流 ✅
  - [x] 6.6 实现 `golden_paths` 样式：黄金之路 ✅
  - [x] 6.7 支持多层级结构和循环流检测

## 阶段 2: 注册与集成 ✅ 完成

- [x] Task 7: 更新注册表和配置
  - [x] 7.1 编辑 `src/neo_legend/registry.py`：导入并注册全部 14 个 Skill
  - [x] 7.2 验证注册表包含全部 14 种图例类型

## 阶段 3: 测试套件 ✅ 全部通过

- [x] Task 8: 为 RadarSkill 创建测试 (9个测试 ✅)
- [x] Task 9: 为 DualRadarSkill 创建测试 (7个测试 ✅)
- [x] Task 10: 为 BarChartSkill 创建测试 (9个测试 ✅)
- [x] Task 11: 为 ComboChartSkill 创建测试 (9个测试 ✅)
- [x] Task 12: 为 BubbleChartSkill 创建测试 (9个测试 ✅)
- [x] Task 13: 为 SankeySkill 创建测试 (9个测试 ✅)

- [x] Task 14: 集成测试和更新现有测试
  - [x] 14.1 更新 test_renderers.py：验证 14 种类型 × 所有样式均可渲染
  - [x] 14.2 更新 test_api.py：添加新类型的 API 测试 (+4个)
  - [x] 14.3 更新 test_registry.py：注册表应包含 14 种类型
  - [x] 14.4 更新 test_batch_generate.py：image_count = 39
  - [x] 14.5 运行完整测试套件：**138 passed, 0 failed** ✅

# Task Dependencies
- [Task 1-6] 可完全并行执行（相互独立的 Skill 实现） ✅
- [Task 7] 依赖 [Task 1-6]（需要先实现才能注册） ✅
- [Task 8-13] 可与 [Task 1-6] 并行（测试可在 Skill 完成后立即编写） ✅
- [Task 14] 依赖所有前序任务（最终集成验证） ✅

# Tasks

- [x] Task 1: 实现 PointsLocationSkill（Total Points By Location 六边形热力图）
  - [x] 1.1 创建 `src/neo_legend/skills/points_location.py` 文件
  - [x] 1.2 实现 `PointsLocationSkill` 类，继承 `BaseLegendSkill`
  - [x] 1.3 定义 `legend_type = "points_location"` 和 `display_name`
  - [x] 1.4 实现至少 2 种样式变体：
    - `default`: 经典青色六边形热力图（匹配参考图片 `0ece60f1e357e60d332c2983bac940dd.jpg`）
    - `warm_gradient`: 暖色系替代方案（橙-红渐变）
  - [x] 1.5 实现核心渲染逻辑 `_render_png()` 方法：
    - 深色纹理背景绘制
    - 半场篮球场地轮廓线
    - 六边形网格热力图（hexbin）
    - 青色/蓝绿色渐变色映射
    - 底部颜色图例（5 级分段：Less Than 200, 200-400, 400-600, 600-800, More Than 800）
    - 左下角品牌标识区域
    - 标题和副标题文本
  - [x] 1.6 支持自定义数据输入：从 `request.data.shots` 读取投篮位置和得分数据，若无则使用 `sample_shots()` 生成默认数据
  - [x] 1.7 更新 `src/neo_legend/registry.py` 的 `build_default_registry()` 函数，注册新 Skill

- [x] Task 2: 补充 CourtShotSkill 测试用例 (9个测试全部通过 ✅)
  - [x] 2.1 创建 `tests/test_court_shot.py`
  - [x] 2.2 测试 terrain 样式默认数据渲染成功且图片有效
  - [x] 2.3 测试 hex 样式渲染成功且与 terrain 样式输出不同
  - [x] 2.4 测试 zone 样式区域标注正确性
  - [x] 2.5 测试自定义 shot_count 和 seed 参数影响输出
  - [x] 2.6 测试自定义 title 和 subtitle 正确显示
  - [x] 2.7 测试无效 style 参数抛出 UnknownStyleError

- [x] Task 3: 补充 DualCourtShotSkill 测试用例 (8个测试全部通过 ✅)
  - [x] 3.1 创建 `tests/test_dual_court_shot.py`
  - [x] 3.2 测试 year_over_year 样式双面板布局正确（上下两个球场）
  - [x] 3.3 测试 split_hex 样式渲染成功
  - [x] 3.4 测试自定义 panels 数据（两个赛季的 metrics）正确显示
  - [x] 3.5 测试 "MOST IMPROVED" 徽章在第二个面板正确显示
  - [x] 3.6 测试 FG%, 3P%, eFG% 统计指标面板正确渲染

- [x] Task 4: 补充 AnimatedCourtShotSkill 测试用例 (7个测试全部通过 ✅)
  - [x] 4.1 创建 `tests/test_animated_court_shot.py`
  - [x] 4.2 测试 pulse 样式返回 GIF 格式（非 PNG）
  - [x] 4.3 测试 sweep 样式返回 GIF 格式
  - [x] 4.4 测试自定义 frame_count 参数影响帧数
  - [x] 4.5 验证 GIF 文件可被 PIL 正常打开且包含多帧

- [x] Task 5: 补充 CoordinateSkill 和 PlusMinusCoordinateSkill 测试用例 (11个测试全部通过 ✅)
  - [x] 5.1 创建 `tests/test_coordinate_charts.py`
  - [x] 5.2 测试 CoordinateSkill dark_bubble 样式散点图标签可读性
  - [x] 5.3 测试 CoordinateSkill gold_scorers 样式配色差异
  - [x] 5.4 测试自定义 points 数据覆盖默认数据
  - [x] 5.5 测试 PlusMinusCoordinateSkill 四象限划分正确性
  - [x] 5.6 测试 paper_quadrant 样式纹理背景存在
  - [x] 5.7 测试 clean_quadrant 样式无纹理背景

- [x] Task 6: 补充 RoseSkill 和 TableSkill 测试用例 (11个测试全部通过 ✅)
  - [x] 6.1 创建 `tests/test_rose_and_table.py`
  - [x] 6.2 测试 RoseSkill proposal_comparison 样式双环对比图
  - [x] 6.3 测试 RoseSkill lottery_black 样式单环图
  - [x] 6.4 测试 TableSkill heatmap_light 样式表格行数和列数正确
  - [x] 6.5 测试 TableSkill scoreboard_dark 样式暗色主题
  - [x] 6.6 测试 TableSkill 自定义 rows 数据替换默认数据
  - [x] 6.7 测试 TableSkill 单元格条件格式颜色渐变正确

- [x] Task 7: 补充 PointsLocationSkill 测试用例 (8个测试全部通过 ✅)
  - [x] 7.1 在 Task 1 完成后创建 `tests/test_points_location.py`
  - [x] 7.2 测试 default 样式匹配参考图片视觉特征（深色背景、六边形网格、青色渐变、底部图例）
  - [x] 7.3 测试 warm_gradient 样式使用暖色系配色
  - [x] 7.4 测试自定义 shots 数据生成不同热力分布
  - [x] 7.5 测试颜色图例 5 个分段标签文本正确

- [x] Task 8: 补充集成测试和边界条件测试 (23个测试全部通过 ✅)
  - [x] 8.1 扩展 `tests/test_renderers.py`：
    - 测试所有已注册 legend_type 均可通过 registry.render() 成功调用
    - 测试每个 legend_type 的所有 style 变体均可正常渲染
    - 测试 width/height 边界值（最小 640, 最大 2400）
  - [x] 8.2 扩展 `tests/test_api.py`：
    - 测试 GET /render 新增 points_location 类型
    - 测试 POST /render 携带大量自定义数据的性能
    - 测试缺少必填字段时的错误响应格式一致性
  - [x] 8.3 创建 `tests/test_edge_cases.py`：
    - 测试空字典 data 参数的降级处理
    - 测试极端尺寸请求（如 640x640 或 2400x3200）
    - 测试特殊字符 title/subtitle（Unicode、长文本）

# Task Dependencies
- [Task 7] depends on [Task 1]
- [Task 2, 3, 4, 5, 6] 可并行执行（相互独立）
- [Task 8] 应在 [Task 2-7] 之后执行（需要先有各 Skill 的测试基础）

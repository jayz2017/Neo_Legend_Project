# 新增华丽图表类型 Spec

## Why
当前项目已实现 8 种核心图例（court_shot, dual_court_shot, court_shot_animation, coordinate, plus_minus_coordinate, rose, table, points_location），但还缺少以下重要的数据可视化类型，无法满足更丰富的体育数据分析场景需求。需要新增 **6 种华丽的图表类型**，每种都有独立的 Skill 实现、多种精美样式变体和丰富的色彩搭配。

## What Changes
- 新增 6 个独立的 Skill 类（雷达图、双雷达图、柱状图、柱状+折线组合、水滴图、桑基图）
- 每个 Skill 至少提供 2-3 种精美的样式变体（色彩丰富、视觉华丽）
- 扩展 `registry.py` 注册所有新 Skill
- 为每个新 Skill 创建完整的测试套件
- 更新 CI 流水线以包含新测试

## Impact
- Affected specs: 无（全新功能）
- Affected code:
  - `src/neo_legend/skills/` (新增 6 个文件)
  - `src/neo_legend/registry.py` (注册新 Skills)
  - `tests/` (新增 6+ 测试文件)

## ADDED Requirements

### Requirement 1: RadarSkill - 华丽雷达图
系统 SHALL 提供雷达图（蜘蛛网图）可视化能力，用于展示多维数据对比。

**特征要求**:
- 多边形网格背景（5-8 轴可选）
- 渐变色填充区域（半透明效果）
- 数据点标记（圆形/菱形/星形可选）
- 精美的轴线标签和刻度
- 支持单实体或多实体对比
- 华丽的配色方案（霓虹色系、金属质感、渐变彩虹等）

**样式变体**:
1. `neon_glow`: 霓虹发光效果（深色背景 + 发光线条 + 辉光填充）
2. `crystal_metal`: 晶体金属质感（渐变银色 + 高光反射）
3. `gradient_rainbow`: 彩虹渐变（多色平滑过渡）

**数据格式**:
```json
{
  "categories": ["得分", "篮板", "助攻", "抢断", "盖帽"],
  "datasets": [
    {"label": "Player A", "values": [85, 72, 90, 68, 75], "color": "#ff6b6b"},
    {"label": "Player B", "values": [78, 88, 65, 80, 70], "color": "#4ecdc4"}
  ]
}
```

#### Scenario: 单实体雷达图渲染
- **WHEN** 提供单个 dataset 和 categories
- **THEN** 系统 SHALL 渲染带有渐变填充的多边形雷达图

#### Scenario: 多实体对比雷达图
- **WHEN** 提供 2-5 个 datasets
- **THEN** 系统 SHALL 渲染半透明重叠的多个多边形，便于对比

---

### Requirement 2: DualRadarSkill - 双雷达对比图
系统 SHALL 提供左右并列的双雷达图，用于直观对比两个实体的各项指标。

**特征要求**:
- 左右对称布局的两个独立雷达图
- 中间共享标题和图例
- 差异高亮显示（数值差异用颜色或标记强调）
- 连接线连接对应轴的点（可选）
- 华丽的双色调配色（如红蓝对抗、冷暖对比）

**样式变体**:
1. `versus_battle`: 对抗模式（左右分立，中间 VS 标识）
2. `mirror_compare`: 镜像对比（对称配色，差异箭头）
3. `evolution_track`: 进化轨迹（上下时间轴 + 双雷达）

**特殊功能**:
- 自动计算并标注最大差异维度
- 性能提升/下降的箭头指示器
- 中央统计摘要面板（平均值、总分等）

---

### Requirement 3: BarChartSkill - 华丽柱状图
系统 SHALL 提供高度定制化的柱状图，支持多种华丽视觉效果。

**特征要求**:
- 圆角矩形柱体（可调圆角半径）
- 渐变色填充（垂直或水平渐变）
- 3D 立体效果（可选）
- 柱体阴影和高光
- 精美的坐标轴和网格线
- 数据标签（顶部/内部显示）
- 动态排序动画提示（静态图中用颜色深浅表示排名）

**样式变体**:
1. `glass_3d`: 玻璃质感 3D 柱状图（透明度 + 反光 + 阴影）
2. `neon_tubes`: 霓虹灯管效果（发光边缘 + 暗色背景）
3. `gradient_sky`: 天空渐变柱状图（日落/日出色彩过渡）
4. `crystal_pillars`: 水晶柱状图（折射效果 + 光泽纹理）

**高级特性**:
- 分组柱状图（Grouped Bars）
- 堆叠柱状图（Stacked Bars）
- 百分比堆叠（100% Stacked）
- 瀑布图（Waterfall）变体

---

### Requirement 4: ComboChartSkill - 柱状+折线组合图
系统 SHALL 提供柱状图与折线图的华丽组合，用于同时展示绝对值和趋势。

**特征要求**:
- 主 Y 轴：柱状图（体积/数量）
- 副 Y 轴：折线图（比率/百分比）
- 平滑曲线插值（贝塞尔曲线）
- 数据点标记（多样化：圆、方、三角、星）
- 区域填充（折线下方半透明）
- 交叉点高亮标注
- 双轴颜色协调

**样式变体**:
1. `crystal_stream`: 水晶流光效果（透明柱体 + 发光曲线）
2. `neon_pulse`: 霓虹脉冲（发光柱 + 动感虚线）
3. `sunset_gradient`: 日落渐变（暖色柱 + 金色曲线）
4. `ocean_depths`: 海洋深度（蓝色系柱 + 波浪曲线）

**交互元素**（静态模拟）:
- 关键节点标注框
- 趋势箭头指示
- 异常值警告标记

---

### Requirement 5: BubbleChartSkill - 华丽水滴/气泡图
系统 SHALL 提供水滴形状的气泡图，用于三维数据可视化（X, Y, Size）。

**特征要求**:
- 水滴/泪滴形状标记（非传统圆形）
- 大小映射到第三维数据
- 颜色映射到第四维数据（可选）
- 半透明叠加效果
- 气泡边框发光
- 悬浮阴影效果
- 精密的气泡防重叠算法

**样式变体**:
1. `water_drops`: 水滴气泡（泪滴形状 + 折射光泽）
2. `fireflies`: 萤火虫效果（发光粒子 + 拖尾轨迹）
3. `galaxy_stars`: 星空银河（星星形状 + 闪烁光晕）
4. `crystal_orbs`: 水晶球体（3D 球体 + 内部折射）

**高级特性**:
- 气泡标签智能避让算法
- 聚类边界圈选
- 四象限划分（类似 PlusMinusCoordinateSkill）
- 时间轴动画提示（用大小变化表示）

---

### Requirement 6: SankeySkill - 华丽桑基图
系统 SHALL 提供桑基图（流向图），用于展示流量分配和转化漏斗。

**特征要求**:
- 平滑的贝塞尔曲线路径
- 渐变色流带（源头到目标颜色过渡）
- 可变的流带宽度（表示流量大小）
- 节点自定义样式（圆形/矩形/椭圆）
- 节点标签和数值标注
- 分层布局（源 → 中间 → 目标）
- 华丽的背景装饰（暗色纹理 + 微光粒子）

**样式变体**:
1. `neon_streams`: 霓虹流光（发光路径 + 深色背景）
2. `energy_flow`: 能量流动（热力图配色 + 脉动效果暗示）
3. `crystal_rivers`: 晶体河流（透明渐变 + 折射纹理）
4. `golden_paths`: 黄金之路（金色调 + 华丽节点）

**高级特性**:
- 循环流检测和标注
- 流量百分比标注
- 节点悬停信息框（静态用注释替代）
- 多层级缩放支持
- 并行比较模式（左右两个桑基图）

---

## MODIFIED Requirements

### Requirement: Registry 扩展
`build_default_registry()` 函数 SHALL 包含所有 6 个新 Skill 实例。

### Requirement: pyproject.toml 配置
确保 pytest 配置支持新的测试文件发现。

## REMOVED Requirements
无

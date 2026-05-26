# 补充缺失图例代码与完善测试用例 Spec

## Why
通过分析项目现有代码发现：
1. 项目已实现 7 种核心图例类型（court_shot, dual_court_shot, animated_court_shot, coordinate, plus_minus_coordinate, rose, table），共 15+ 种样式变体
2. 用户提供的示例图片 `0ece60f1e357e60d332c2983bac940dd.jpg`（Total Points By Location 六边形热力图）**尚未实现**为独立 Skill
3. 现有测试覆盖不完整，缺少针对特定图例类型的专项测试、边界条件测试、数据验证测试

## What Changes
- 新增 `PointsLocationSkill` 图例类型（Total Points By Location 六边形热力图）
- 完善测试套件，补充以下缺失的测试场景：
  - 各 Skill 的数据验证逻辑测试
  - 自定义数据输入 vs 默认数据的差异化测试
  - 图片尺寸、格式、元数据的精确验证
  - 错误处理和边界条件测试
  - 视觉回归基准测试

## Impact
- Affected specs: 无（新增功能）
- Affected code: 
  - `src/neo_legend/skills/` (新增 points_location.py)
  - `src/neo_legend/registry.py` (注册新 Skill)
  - `tests/` (扩展测试覆盖)

## ADDED Requirements

### Requirement: PointsLocationSkill - Total Points By Location 六边形热力图
系统 SHALL 提供一个新的图例类型 `points_location`，用于绘制 Kirk Goldsberry 风格的"Total Points By Location"可视化图表。

**特征要求**：
- 深色纹理背景（#0a1929 或类似色值）
- 半场篮球场地轮廓线（白色/浅灰色）
- 六边形网格热力图（hexbin）
- 青色/蓝绿色渐变色映射（#1a5f7a → #57c4b4 → #a8e6cf）
- 底部颜色图例（Less Than 200, 200-400, 400-600, 600-800, More Than 800）
- 左下角品牌标识区域（BASKETBALL UNIVERSE logo + 装饰图标）
- 标题："Total Points By Location"
- 副标题：包含赛季信息和作者署名

#### Scenario: 成功渲染默认数据
- **WHEN** 用户请求 `legend_type="points_location"` 且 `style="default"`
- **THEN** 系统 SHALL 返回符合参考图片视觉风格的 PNG 图片（尺寸匹配 request 参数，包含所有必需元素）

#### Scenario: 自定义投篮数据输入
- **WHEN** 用户在 `request.data` 中提供自定义 `shots` 数组（含 x, y, points 字段）
- **THEN** 系统 SHALL 使用自定义数据生成热力图，而非使用随机生成的样本数据

### Requirement: 完善的测试用例体系
系统 SHALL 为每个已实现的 Skill 提供全面的测试覆盖，包括但不限于：

#### Scenario: 数据验证测试
- **WHEN** 传入空数据或缺失关键字段
- **THEN** Skill SHALL 使用合理的默认值进行降级处理，不会抛出异常

#### Scenario: 样式切换测试
- **WHEN** 对同一图例类型使用不同 style 参数
- **THEN** 生成的图片内容 SHALL 存在明显视觉差异（像素级不完全相同）

#### Scenario: 自定义标题和副标题测试
- **WHEN** 在 RenderRequest 中提供自定义 title 和 subtitle
- **THEN** 生成的图片 SHALL 包含用户指定的文本内容

#### Scenario: 输出格式和尺寸验证
- **WHEN** 指定 width 和 height 参数
- **THEN** 返回的图片 SHALL 具有精确匹配的尺寸，且格式符合 media_type 声明

## MODIFIED Requirements

### Requirement: Registry 注册机制
现有的 `build_default_registry()` 函数 SHALL 更新以包含新注册的 `PointsLocationSkill`。

## REMOVED Requirements
无

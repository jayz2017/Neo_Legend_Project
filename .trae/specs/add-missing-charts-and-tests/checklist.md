# Checklist

- [x] PointsLocationSkill 代码实现完成且符合 spec.md 要求
  - [x] 文件 `src/neo_legend/skills/points_location.py` 已创建
  - [x] 类继承 BaseLegendSkill 且实现 render() 方法
  - [x] legend_type, display_name, style_definitions 正确定义
  - [x] default 样式匹配参考图片视觉特征（深色背景、六边形热力图、青色渐变、底部图例、品牌标识）
  - [x] warm_gradient 样式使用暖色系替代配色
  - [x] 支持自定义 shots 数据输入
  - [x] registry.py 已注册新 Skill

- [x] CourtShotSkill 测试覆盖完整 (9个测试 ✅)
  - [x] terrain/hex/zone 三种样式均可成功渲染
  - [x] 不同样式输出内容存在差异
  - [x] 自定义参数（shot_count, seed, title, subtitle）生效
  - [x] 无效 style 参数正确抛出异常

- [x] DualCourtShotSkill 测试覆盖完整 (8个测试 ✅)
  - [x] year_over_year/split_hex 两种样式均可渲染
  - [x] 双面板布局和统计指标显示正确
  - [x] 自定义 panels 数据替换默认数据
  - [x] MOST IMPROVED 徽章逻辑正确

- [x] AnimatedCourtShotSkill 测试覆盖完整 (7个测试 ✅)
  - [x] pulse/sweep 两种样式均返回 GIF 格式
  - [x] GIF 包含多帧动画
  - [x] frame_count 参数可自定义

- [x] CoordinateSkill 和 PlusMinusCoordinateSkill 测试覆盖完整 (11个测试 ✅)
  - [x] CoordinateSkill 两种样式散点图可读性验证
  - [x] PlusMinusCoordinateSkill 四象限划分和纹理背景验证
  - [x] 自定义 points 数据覆盖默认数据

- [x] RoseSkill 和 TableSkill 测试覆盖完整 (11个测试 ✅)
  - [x] RoseSkill 双环/单环两种模式正常
  - [x] TableSkill 行列数、条件格式、暗色主题验证
  - [x] 自定义数据输入生效

- [x] PointsLocationSkill 测试覆盖完整 (8个测试 ✅)
  - [x] default/warm_gradient 两种样式渲染成功
  - [x] 视觉特征匹配参考图片
  - [x] 颜色图例 5 级分段标签正确
  - [x] 自定义 shots 数据生成不同分布

- [x] 集成测试和边界测试通过 (23个测试 ✅)
  - [x] 所有 legend_type × style 组合均可通过 API 渲染
  - [x] 边界尺寸请求正常处理（640×640 到 2400×3200）
  - [x] 错误响应格式一致且友好
  - [x] 特殊字符和极端输入降级处理无异常

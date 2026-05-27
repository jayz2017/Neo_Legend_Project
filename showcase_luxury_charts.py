"""
华丽图表展示脚本 - 生成雷达图和桑基图示例
"""
from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry
import os

# 创建输出目录
output_dir = "generated_charts"
os.makedirs(output_dir, exist_ok=True)

registry = build_default_registry()

print("=" * 60)
print("🎨 正在生成华丽图表...")
print("=" * 60)

# ==================== 雷达图展示 ====================
print("\n📡 [1/8] 生成 Radar Chart - neon_glow (霓虹发光)...")
req1 = RenderRequest(
    legend_type="radar_chart",
    style="neon_glow",
    width=1200,
    height=1400,
    title="PLAYER RADAR PROFILE",
    subtitle="MULTIDIMENSIONAL ANALYSIS | 2025-26 SEASON",
    data={
        "categories": ["得分", "篮板", "助攻", "抢断", "盖帽"],
        "datasets": [
            {"label": "超级巨星 A", "values": [95, 82, 88, 75, 80], "color": "#ff6b6b"},
            {"label": "全能战士 B", "values": [78, 90, 85, 88, 72], "color": "#4ecdc4"}
        ]
    }
)
result1 = registry.render(req1)
with open(os.path.join(output_dir, "01_radar_neon_glow.png"), "wb") as f:
    f.write(result1.content)
print(f"   ✅ 已保存: {len(result1.content):,} bytes")

print("\n💎 [2/8] 生成 Radar Chart - crystal_metal (晶体金属)...")
req2 = RenderRequest(
    legend_type="radar_chart",
    style="crystal_metal",
    width=1200,
    height=1400,
    title="CRYSTAL METAL RADAR",
    subtitle="PREMIUM EDITION"
)
result2 = registry.render(req2)
with open(os.path.join(output_dir, "02_radar_crystal_metal.png"), "wb") as f:
    f.write(result2.content)
print(f"   ✅ 已保存: {len(result2.content):,} bytes")

print("\n🌈 [3/8] 生成 Radar Chart - gradient_rainbow (彩虹渐变)...")
req3 = RenderRequest(
    legend_type="radar_chart",
    style="gradient_rainbow",
    width=1200,
    height=1400,
    title="RAINBOW SPECTRUM",
    subtitle="MULTI-DIMENSIONAL VISUALIZATION"
)
result3 = registry.render(req3)
with open(os.path.join(output_dir, "03_radar_gradient_rainbow.png"), "wb") as f:
    f.write(result3.content)
print(f"   ✅ 已保存: {len(result3.content):,} bytes")

# ==================== 桑基图展示 ====================
print("\n✨ [4/8] 生成 Sankey Diagram - neon_streams (霓虹流光)...")
req4 = RenderRequest(
    legend_type="sankey_chart",
    style="neon_streams",
    width=1400,
    height=1000,
    title="NEON STREAMS FLOW",
    subtitle="DATA TRAFFIC VISUALIZATION"
)
result4 = registry.render(req4)
with open(os.path.join(output_dir, "04_sankey_neon_streams.png"), "wb") as f:
    f.write(result4.content)
print(f"   ✅ 已保存: {len(result4.content):,} bytes")

print("\n🔥 [5/8] 生成 Sankey Diagram - energy_flow (能量流动)...")
req5 = RenderRequest(
    legend_type="sankey_chart",
    style="energy_flow",
    width=1400,
    height=1000,
    title="ENERGY FLOW DIAGRAM",
    subtitle="THERMAL DYNAMICS VISUALIZATION"
)
result5 = registry.render(req5)
with open(os.path.join(output_dir, "05_sankey_energy_flow.png"), "wb") as f:
    f.write(result5.content)
print(f"   ✅ 已保存: {len(result5.content):,} bytes")

print("\n🌊 [6/8] 生成 Sankey Diagram - crystal_rivers (晶体河流)...")
req6 = RenderRequest(
    legend_type="sankey_chart",
    style="crystal_rivers",
    width=1400,
    height=1000,
    title="CRYSTAL RIVERS",
    subtitle="TRANSPARENT FLOW VISUALIZATION"
)
result6 = registry.render(req6)
with open(os.path.join(output_dir, "06_sankey_crystal_rivers.png"), "wb") as f:
    f.write(result6.content)
print(f"   ✅ 已保存: {len(result6.content):,} bytes")

print("\n👑 [7/8] 生成 Sankey Diagram - golden_paths (黄金之路)...")
req7 = RenderRequest(
    legend_type="sankey_chart",
    style="golden_paths",
    width=1400,
    height=1000,
    title="GOLDEN PATHS",
    subtitle="ROYAL FLOW ANALYSIS"
)
result7 = registry.render(req7)
with open(os.path.join(output_dir, "07_sankey_golden_paths.png"), "wb") as f:
    f.write(result7.content)
print(f"   ✅ 已保存: {len(result7.content):,} bytes")

# ==================== 双雷达对比图展示 ====================
print("\n⚔️ [8/8] 生成 Dual Radar - versus_battle (对抗模式)...")
req8 = RenderRequest(
    legend_type="dual_radar_chart",
    style="versus_battle",
    width=1400,
    height=900,
    title="VERSUS BATTLE",
    subtitle="HEAD TO HEAD COMPARISON"
)
result8 = registry.render(req8)
with open(os.path.join(output_dir, "08_dual_radar_versus.png"), "wb") as f:
    f.write(result8.content)
print(f"   ✅ 已保存: {len(result8.content):,} bytes")

print("\n" + "=" * 60)
print("🎉 所有图表生成完成！")
print(f"📁 输出目录: {os.path.abspath(output_dir)}")
print("=" * 60)

# 列出所有生成的文件
print("\n📋 生成的文件列表:")
for i, filename in enumerate(sorted(os.listdir(output_dir)), 1):
    filepath = os.path.join(output_dir, filename)
    size = os.path.getsize(filepath)
    print(f"   {i}. {filename} ({size:,} bytes)")

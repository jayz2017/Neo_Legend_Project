"""
文档示例验证脚本
基于 docs/使用文档.md 中的 Python SDK 示例代码
逐一验证所有 14 种图表类型是否能正常生成
"""
import sys
import os
import time

sys.stdout.reconfigure(encoding="utf-8")

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry

registry = build_default_registry()
output_dir = "doc_verification_output"
os.makedirs(output_dir, exist_ok=True)

results = []
total_start = time.time()

print("=" * 70)
print("📋 Neo Legend 文档示例代码验证")
print("=" * 70)
print(f"输出目录: {os.path.abspath(output_dir)}\n")

# ─── 1. Court Shot（球场投射图）────────────────────────────
print("─" * 50)
print("1️⃣  Court Shot（球场投射图）")
try:
    request = RenderRequest(
        legend_type="court_shot",
        style="terrain",
        title="Scottie Pippen",
        subtitle="1997-98 Season | By @KirkGoldsberry",
        data={"shot_count": 800, "seed": 42}
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "01_court_shot_terrain.png")
    with open(path, "wb") as f:
        f.write(result.content)
    elapsed = time.time() - total_start
    size_kb = len(result.content) / 1024
    print(f"   ✅ terrain 样式 | {size_kb:.1f} KB | {result.media_type}")
    results.append(("court_shot/terrain", True, size_kb, elapsed))
except Exception as e:
    print(f"   ❌ terrain 样式失败: {e}")
    results.append(("court_shot/terrain", False, 0, 0))

try:
    request = RenderRequest(legend_type="court_shot", style="hex", data={"seed": 99})
    result = registry.render(request)
    path = os.path.join(output_dir, "01b_court_shot_hex.png")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    print(f"   ✅ hex 样式     | {size_kb:.1f} KB")
except Exception as e:
    print(f"   ❌ hex 样式失败: {e}")

# ─── 2. Dual Court Shot（双球场对比图）─────────────────────
print("\n" + "─" * 50)
print("2️⃣  Dual Court Shot（双球场对比图）")
try:
    request = RenderRequest(
        legend_type="dual_court_shot",
        style="year_over_year",
        data={
            "panels": [
                {
                    "season": "2024-25",
                    "attempts": "79 GAMES / 808 ATTEMPTS",
                    "seed": 12,
                    "metrics": {"FG%": "47.6%", "3P%": "33.2%", "eFG%": "53.7%"}
                },
                {
                    "season": "2025-26",
                    "attempts": "71 GAMES / 774 ATTEMPTS",
                    "seed": 44,
                    "metrics": {"FG%": "51.8%", "3P%": "42.0%", "eFG%": "58.4%"}
                }
            ]
        }
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "02_dual_court_shot.png")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    print(f"   ✅ year_over_year | {size_kb:.1f} KB | {result.media_type}")
    results.append(("dual_court_shot/year_over_year", True, size_kb, time.time() - total_start))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("dual_court_shot/year_over_year", False, 0, 0))

# ─── 3. Animated Court Shot（动态球场图）────────────────────
print("\n" + "─" * 50)
print("3️⃣  Animated Court Shot（动态球场图 GIF）")
try:
    request = RenderRequest(
        legend_type="court_shot_animation",
        style="pulse",
        data={"frame_count": 15}
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "03_animated_court.gif")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    is_gif = result.media_type == "image/gif"
    print(f"   ✅ pulse 动画 | {size_kb:.1f} KB | {result.media_type} {'(GIF✓)' if is_gif else '(⚠非GIF)'}")
    results.append(("animated/pulse", True, size_kb, time.time() - total_start))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("animated/pulse", False, 0, 0))

# ─── 4. Coordinate（坐标散点图）────────────────────────────
print("\n" + "─" * 50)
print("4️⃣  Coordinate（坐标散点图）")
try:
    request = RenderRequest(
        legend_type="coordinate",
        style="dark_bubble",
        data={
            "points": [
                {"label": "球员A", "x": 22.0, "y": 65.3, "size": 400, "color": "#FDB927"},
                {"label": "球员B", "x": 28.5, "y": 58.2, "size": 350, "color": "#06AAF4"},
                {"label": "球员C", "x": 18.2, "y": 72.5, "size": 500, "color": "#FF6B35"},
                {"label": "球员D", "x": 31.0, "y": 48.9, "size": 280, "color": "#E03C31"},
                {"label": "球员E", "x": 25.3, "y": 62.1, "size": 320, "color": "#00B050"},
            ]
        }
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "04_coordinate_dark_bubble.png")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    print(f"   ✅ dark_bubble | {size_kb:.1f} KB | {result.media_type}")
    results.append(("coordinate/dark_bubble", True, size_kb, time.time() - total_start))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("coordinate/dark_bubble", False, 0, 0))

# ─── 5. Plus-Minus Coordinate（正负四象限图）────────────────
print("\n" + "─" * 50)
print("5️⃣  Plus-Minus Coordinate（正负四象限图）")
try:
    request = RenderRequest(
        legend_type="plus_minus_coordinate",
        style="paper_quadrant",
        data={
            "points": [
                {"label": "球队A (攻强防强)", "x": 5.0, "y": 5.0, "color": "#2ecc71"},
                {"label": "球队B (攻强防弱)", "x": 5.0, "y": -3.0, "color": "#e74c3c"},
                {"label": "球队C (攻弱防强)", "x": -2.0, "y": 4.0, "color": "#3498db"},
                {"label": "球队D (攻弱防弱)", "x": -4.0, "y": -4.0, "color": "#95a5a6"},
            ]
        }
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "05_plus_minus_quadrant.png")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    print(f"   ✅ paper_quadrant | {size_kb:.1f} KB | {result.media_type}")
    results.append(("plus_minus/paper_quadrant", True, size_kb, time.time() - total_start))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("plus_minus/paper_quadrant", False, 0, 0))

# ─── 6. Rose（玫瑰图）──────────────────────────────────────
print("\n" + "─" * 50)
print("6️⃣  Rose Chart（玫瑰图）")
try:
    request = RenderRequest(
        legend_type="rose",
        style="proposal_comparison",
        data={
            "current_values": [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 1, 0.5, 0.3, 0.1],
            "proposed_values": [10, 10, 10, 10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5]
        }
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "06_rose_proposal.png")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    print(f"   ✅ proposal_comparison | {size_kb:.1f} KB | {result.media_type}")
    results.append(("rose/proposal_comparison", True, size_kb, time.time() - total_start))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("rose/proposal_comparison", False, 0, 0))

# ─── 7. Table（表格图）─────────────────────────────────────
print("\n" + "─" * 50)
print("7️⃣  Table（表格图）")
try:
    request = RenderRequest(
        legend_type="table",
        style="heatmap_light",
        data={
            "rows": [
                {"team": "NEO", "team_color": "#29b98f", "name": "Player Alpha", "pts_created": 45.5, "ts": 62, "ast_tov": 3.0, "mpg": 36.5},
                {"team": "LEG", "team_color": "#e74c3c", "name": "Player Beta", "pts_created": 38.2, "ts": 58, "ast_tov": 2.8, "mpg": 34.0},
                {"team": "END", "team_color": "#3498db", "name": "Player Gamma", "pts_created": 32.1, "ts": 55, "ast_tov": 4.2, "mpg": 33.5},
                {"team": "MYT", "team_color": "#f39c12", "name": "Player Delta", "pts_created": 28.7, "ts": 51, "ast_tov": 2.5, "mpg": 30.0},
            ]
        }
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "07_table_heatmap.png")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    print(f"   ✅ heatmap_light | {size_kb:.1f} KB | {result.media_type}")
    results.append(("table/heatmap_light", True, size_kb, time.time() - total_start))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("table/heatmap_light", False, 0, 0))

# ─── 8. Points Location（总分位置热力图）────────────────────
print("\n" + "─" * 50)
print("8️⃣  Points Location（总分位置热力图）")
try:
    import random
    random.seed(42)
    shots = []
    for _ in range(120):
        x = random.uniform(-250, 250)
        y = random.uniform(0, 480)
        points = int(random.uniform(50, 500))
        shots.append({"x": round(x, 1), "y": round(y, 1), "points": points})

    request = RenderRequest(
        legend_type="points_location",
        style="default",
        title="Total Points By Location",
        subtitle="2020-21 Season | By @KirkGoldsberry",
        data={"shots": shots}
    )
    result = registry.render(request)
    path = os.path.join(output_dir, "08_points_location.png")
    with open(path, "wb") as f:
        f.write(result.content)
    size_kb = len(result.content) / 1024
    print(f"   ✅ default 样式 | {size_kb:.1f} KB | {result.media_type}")
    results.append(("points_location/default", True, size_kb, time.time() - total_start))
except Exception as e:
    print(f"   ❌ 失败: {e}")
    results.append(("points_location/default", False, 0, 0))

# ─── 9. Radar Chart（华丽雷达图）⭐ 新增 ────────────────────
print("\n" + "─" * 50)
print("9️⃣  Radar Chart（华丽雷达图）⭐ 新增")
for style_name, desc in [("neon_glow", "霓虹发光"), ("crystal_metal", "晶体金属"), ("gradient_rainbow", "彩虹渐变")]:
    try:
        request = RenderRequest(
            legend_type="radar_chart",
            style=style_name,
            title=f"球员能力多维分析 - {desc}",
            width=1000, height=1100,
            data={
                "categories": ["得分", "篮板", "助攻", "抢断", "盖帽", "效率", "防守"],
                "datasets": [
                    {"label": "球员 A", "values": [95, 82, 88, 75, 80, 90, 78], "color": "#ff6b6b"},
                    {"label": "球员 B", "values": [78, 90, 85, 88, 72, 76, 85], "color": "#4ecdc4"},
                    {"label": "球员 C", "values": [65, 70, 92, 80, 88, 68, 72], "color": "#ffeaa7"}
                ]
            }
        )
        result = registry.render(request)
        safe_style = style_name.replace("_", "-")
        path = os.path.join(output_dir, f"09_radar_{safe_style}.png")
        with open(path, "wb") as f:
            f.write(result.content)
        size_kb = len(result.content) / 1024
        print(f"   ✅ {style_name:20s} ({desc}) | {size_kb:7.1f} KB")
        results.append((f"radar/{style_name}", True, size_kb, time.time() - total_start))
    except Exception as e:
        print(f"   ❌ {style_name}: {e}")
        results.append((f"radar/{style_name}", False, 0, 0))

# ─── 10. Dual Radar Chart（双雷达对比图）⭐ 新增 ────────────
print("\n" + "─" * 50)
print("🔟  Dual Radar Chart（双雷达对比图）⭐ 新增")
for style_name, desc in [("versus_battle", "对抗模式"), ("mirror_compare", "镜像对比"), ("evolution_track", "进化轨迹")]:
    try:
        request = RenderRequest(
            legend_type="dual_radar_chart",
            style=style_name,
            title=f"Dual Radar - {desc}",
            width=1300, height=850,
            data={
                "left": {
                    "label": "2024 Season",
                    "categories": ["PTS", "REB", "AST", "STL", "BLK", "EFF"],
                    "values": [28, 7.5, 8.2, 1.2, 0.9, 28.5]
                },
                "right": {
                    "label": "2025 Season",
                    "categories": ["PTS", "REB", "AST", "STL", "BLK", "EFF"],
                    "values": [32, 8.8, 9.5, 1.5, 1.2, 33.2]
                }
            }
        )
        result = registry.render(request)
        safe_style = style_name.replace("_", "-")
        path = os.path.join(output_dir, f"10_dual_radar_{safe_style}.png")
        with open(path, "wb") as f:
            f.write(result.content)
        size_kb = len(result.content) / 1024
        print(f"   ✅ {style_name:20s} ({desc}) | {size_kb:7.1f} KB")
        results.append((f"dual_radar/{style_name}", True, size_kb, time.time() - total_start))
    except Exception as e:
        print(f"   ❌ {style_name}: {e}")
        results.append((f"dual_radar/{style_name}", False, 0, 0))

# ─── 11. Bar Chart（华丽柱状图）⭐ 新增 ────────────────────
print("\n" + "─" * 50)
print("1️⃣1️⃣ Bar Chart（华丽柱状图）⭐ 新增")
bar_styles = [
    ("glass_3d", "玻璃质感3D"),
    ("neon_tubes", "霓虹灯管"),
    ("gradient_sky", "天空渐变"),
    ("crystal_pillars", "水晶柱"),
]
for style_name, desc in bar_styles:
    try:
        request = RenderRequest(
            legend_type="bar_chart",
            style=style_name,
            title=f"Bar Chart - {desc}",
            width=1100, height=850,
            data={
                "labels": ["一月", "二月", "三月", "四月", "五月", "六月"],
                "values": [85, 72, 90, 68, 75, 95],
                "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7", "#dda0dd"]
            }
        )
        result = registry.render(request)
        safe_style = style_name.replace("_", "-")
        path = os.path.join(output_dir, f"11_bar_{safe_style}.png")
        with open(path, "wb") as f:
            f.write(result.content)
        size_kb = len(result.content) / 1024
        print(f"   ✅ {style_name:20s} ({desc}) | {size_kb:7.1f} KB")
        results.append((f"bar/{style_name}", True, size_kb, time.time() - total_start))
    except Exception as e:
        print(f"   ❌ {style_name}: {e}")
        results.append((f"bar/{style_name}", False, 0, 0))

# ─── 12. Combo Chart（组合图表）⭐ 新增 ────────────────────
print("\n" + "─" * 50)
print("1️⃣2️⃣ Combo Chart（组合图表）⭐ 新增")
combo_styles = [
    ("crystal_stream", "水晶流光"),
    ("neon_pulse", "霓虹脉冲"),
    ("sunset_gradient", "日落渐变"),
    ("ocean_depths", "海洋深度"),
]
for style_name, desc in combo_styles:
    try:
        request = RenderRequest(
            legend_type="combo_chart",
            style=style_name,
            title=f"Combo Chart - {desc}",
            width=1300, height=850,
            data={
                "categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "bar_values": [120, 145, 132, 168, 155, 180],
                "line_values": [45, 52, 48, 62, 58, 70],
                "bar_label": "Revenue ($K)",
                "line_label": "Growth Rate (%)"
            }
        )
        result = registry.render(request)
        safe_style = style_name.replace("_", "-")
        path = os.path.join(output_dir, f"12_combo_{safe_style}.png")
        with open(path, "wb") as f:
            f.write(result.content)
        size_kb = len(result.content) / 1024
        print(f"   ✅ {style_name:20s} ({desc}) | {size_kb:7.1f} KB")
        results.append((f"combo/{style_name}", True, size_kb, time.time() - total_start))
    except Exception as e:
        print(f"   ❌ {style_name}: {e}")
        results.append((f"combo/{style_name}", False, 0, 0))

# ─── 13. Bubble Chart（华丽水滴图）⭐ 新增 ──────────────────
print("\n" + "─" * 50)
print("1️⃣3️⃣ Bubble Chart（华丽水滴图）⭐ 新增")
bubble_styles = [
    ("water_drops", "水滴气泡"),
    ("fireflies", "萤火虫效果"),
    ("galaxy_stars", "星空银河"),
    ("crystal_orbs", "水晶球体"),
]
for style_name, desc in bubble_styles:
    try:
        request = RenderRequest(
            legend_type="bubble_chart",
            style=style_name,
            title=f"Bubble Chart - {desc}",
            width=1050, height=800,
            data={
                "points": [
                    {"x": 22.0, "y": 65.3, "size": 400, "color": "#FDB927", "label": "Jokic"},
                    {"x": 28.5, "y": 58.2, "size": 350, "color": "#06AAF4", "label": "Doncic"},
                    {"x": 18.2, "y": 72.5, "size": 500, "color": "#FF6B35", "label": "Giannis"},
                    {"x": 31.0, "y": 48.9, "size": 280, "color": "#E03C31", "label": "Curry"},
                    {"x": 24.5, "y": 63.8, "size": 320, "color": "#00B050", "label": "Embiid"},
                    {"x": 15.8, "y": 55.2, "size": 220, "color": "#9B59B6", "label": "Tatum"},
                ],
                "x_axis": {"label": "PPG", "min": 12, "max": 36},
                "y_axis": {"label": "TS%", "min": 44, "max": 76}
            }
        )
        result = registry.render(request)
        safe_style = style_name.replace("_", "-")
        path = os.path.join(output_dir, f"13_bubble_{safe_style}.png")
        with open(path, "wb") as f:
            f.write(result.content)
        size_kb = len(result.content) / 1024
        print(f"   ✅ {style_name:20s} ({desc}) | {size_kb:7.1f} KB")
        results.append((f"bubble/{style_name}", True, size_kb, time.time() - total_start))
    except Exception as e:
        print(f"   ❌ {style_name}: {e}")
        results.append((f"bubble/{style_name}", False, 0, 0))

# ─── 14. Sankey Diagram（华丽桑基图）⭐ 新增 ────────────────
print("\n" + "─" * 50)
print("1️⃣4️⃣ Sankey Diagram（华丽桑基图）⭐ 新增")
sankey_styles = [
    ("neon_streams", "霓虹流光"),
    ("energy_flow", "能量流动"),
    ("crystal_rivers", "晶体河流"),
    ("golden_paths", "黄金之路"),
]
for style_name, desc in sankey_styles:
    try:
        request = RenderRequest(
            legend_type="sankey_chart",
            style=style_name,
            title=f"Sankey Diagram - {desc}",
            width=1200, height=850,
            data={
                "nodes": [
                    {"id": "visit", "label": "访问页面", "x": 0.05, "y": 0.5},
                    {"id": "browse", "label": "浏览商品", "x": 0.30, "y": 0.28},
                    {"id": "search", "label": "搜索商品", "x": 0.30, "y": 0.72},
                    {"id": "cart", "label": "加入购物车", "x": 0.58, "y": 0.5},
                    {"id": "purchase", "label": "完成购买", "x": 0.82, "y": 0.5},
                    {"id": "exit", "label": "离开", "x": 0.95, "y": 0.5},
                ],
                "flows": [
                    {"source": "visit", "target": "browse", "value": 5000, "color": "#ff6b6b"},
                    {"source": "visit", "target": "search", "value": 3000, "color": "#4ecdc4"},
                    {"source": "browse", "target": "cart", "value": 2000, "color": "#45b7d1"},
                    {"source": "browse", "target": "exit", "value": 3000, "color": "#96ceb4"},
                    {"source": "search", "target": "cart", "value": 1800, "color": "#ffeaa7"},
                    {"source": "search", "target": "exit", "value": 1200, "color": "#dda0dd"},
                    {"source": "cart", "target": "purchase", "value": 3200, "color": "#FDB927"},
                    {"source": "cart", "target": "exit", "value": 600, "color": "#a0a0a0"},
                ]
            }
        )
        result = registry.render(request)
        safe_style = style_name.replace("_", "-")
        path = os.path.join(output_dir, f"14_sankey_{safe_style}.png")
        with open(path, "wb") as f:
            f.write(result.content)
        size_kb = len(result.content) / 1024
        print(f"   ✅ {style_name:20s} ({desc}) | {size_kb:7.1f} KB")
        results.append((f"sankey/{style_name}", True, size_kb, time.time() - total_start))
    except Exception as e:
        print(f"   ❌ {style_name}: {e}")
        results.append((f"sankey/{style_name}", False, 0, 0))

# ═══════════════════════════════════════════════════════════
# 汇总报告
# ═══════════════════════════════════════════════════════════
total_elapsed = time.time() - total_start

print("\n" + "=" * 70)
print("📊 验证结果汇总报告")
print("=" * 70)

passed = sum(1 for _, ok, _, _ in results if ok)
failed = sum(1 for _, ok, _, _ in results if not ok)
total_size_kb = sum(size for _, ok, size, _ in results if ok)

print(f"\n 总测试数:  {len(results)}")
print(f" 通过数:    {passed} {'✅' if passed == len(results) else ''}")
print(f" 失败数:    {failed} {'❌' if failed > 0 else ''}")
print(f" 通过率:    {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
print(f" 总文件大小: {total_size_kb:.1f} KB ({total_size_kb/1024:.2f} MB)")
print(f" 总耗时:     {total_elapsed:.2f}s\n")

if failed > 0:
    print("⚠️  失败的测试项:")
    for name, ok, size, _ in results:
        if not ok:
            print(f"   ❌ {name}")
else:
    print("🎉 所有图表类型全部生成成功！文档示例代码与实际运行完全一致！\n")

print("=" * 70)
print(f"📁 输出目录: {os.path.abspath(output_dir)}")
print(f"   共生成 {passed} 个图片文件，可直接打开查看效果")
print("=" * 70)

# 列出所有生成的文件
generated_files = sorted(os.listdir(output_dir))
print(f"\n📋 生成的文件列表:")
for fname in generated_files:
    fpath = os.path.join(output_dir, fname)
    fsize = os.path.getsize(fpath) / 1024
    print(f"   {fname:45s} {fsize:7.1f} KB")

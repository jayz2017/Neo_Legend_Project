"""验证 Curry 底角三分坐标 - 使用正确的 NBA 三分线判定规则

NBA 三分线由两部分组成:
  1. 弧形部分: 以篮筐为中心，半径 23.75ft 的圆弧（覆盖大部分区域）
  2. 直线部分: 底角区域的垂直线段（从边线向内延伸到与弧的交点）

底角三分判定规则（正确版）:
  - 区域 A (弧形外): 到篮筐距离 > 237.5 → 三分 ✅
  - 区域 B (底角直线外): |x| >= 220 且 y <= 129.5 → 三分 ✅
    （底线 y=0 处 x=±220 是底角三分线的起点，
     向上延伸至与弧交点约 y=129.5）

注意: 底角三分点虽然在弧线"内侧"（距篮筐<237.5），
      但它们在底角直线外侧，所以仍然是合法的三分球！
"""
import numpy as np

BASKET_Y = 40
THREE_PT_ARC_RADIUS = 237.5
CORNER_3_X = 220
CORNER_LINE_TOP_Y = int((np.sqrt(23.75**2 - 22**2) + 4) * 10)  # 弧与底角线交点的y坐标

corner_shots_nba = [
    {"x": -22.5, "y": 3.2, "label": "左底角1"},
    {"x": -23.0, "y": 5.8, "label": "左底角2"},
    {"x": -22.2, "y": 7.5, "label": "左底角3(边缘)"},
    {"x": 22.3,  "y": 4.0, "label": "右底角1"},
    {"x": 22.8,  "y": 6.5, "label": "右底角2"},
    {"x": 22.0,  "y": 7.9, "label": "右底角3(线上)"},
]

# 也检查弧顶三分作为对比
arc_shots_nba = [
    {"x": 2.3,   "y": 26.5, "label": "弧顶正中"},
    {"x": -15.0, "y": 23.8, "label": "左翼三分"},
    {"x": 16.5,  "y": 24.5, "label": "右翼三分"},
]

print("=" * 90)
print("  Stephen Curry 投篮坐标验证 — 正确的 NBA 三分线双规则")
print(f"  底角线交点 Y = {CORNER_LINE_TOP_Y} (弧与底角直线的交点)")
print("=" * 90)
print()
print(f"{'标签':<18} | {'NBA(ft)':>13} | {'代码坐标':>12} | {'到篮筐':>8} | {'弧外?':>6} | {'底角外?':>7} | {'三分?'}")
print("-" * 90)

all_valid = True

for shot in corner_shots_nba + arc_shots_nba:
    cx = shot["x"] * 10
    cy = (shot["y"] + 4) * 10
    dist = round(np.hypot(cx, cy - BASKET_Y), 1)

    outside_arc = dist > THREE_PT_ARC_RADIUS
    outside_corner = abs(cx) >= CORNER_3_X and cy <= CORNER_LINE_TOP_Y
    is_three = outside_arc or outside_corner

    if not is_three:
        all_valid = False

    arc_s = "YES" if outside_arc else " no"
    corn_s = "YES" if outside_corner else " no"
    three_s = "[3PT]" if is_three else "[2PT!!]"
    row = f"{shot['label']:<18} | ({shot['x']:>6.1f},{shot['y']:>5.1f}) | ({cx:>6.0f},{cy:>6.0f}) | {dist:>7.1f} | {arc_s:>6} | {corn_s:>7} | {three_s}"
    print(row)

print("-" * 90)
print()

# === 可视化说明 ===
print("  NBA 三分线几何结构:")
print("    ┌─────────────────────────────────────┐")
print("    │           半场线 (y=470)            │")
print("    │                                     │")
print("    │         ╭─── 弧形三分区 ───╮        │")
print("    │        ╱  (距篮筐>237.5)   ╲       │")
print("    │       ╱                      ╲      │")
print("    │  ───┼──────── 篮筐(y=40) ────┼──    │")
print("    │     │                        │     │")
print("    │  ══│═════════════════════════│═══   │ ← 底角直线(x=±220)")
print("    │  ══│════ 底角三分区 ════════│═══   │")
print("    └────┴────────────────────────┴───────┘")
print("          底角三分 = 在直线外侧 OR 弧线外侧")
print()

if all_valid:
    print("  [PASS] 所有投篮点均位于合法的三分线外!")
else:
    print("  [FAIL] 存在落在二分区的投篮点!")
print("=" * 90)

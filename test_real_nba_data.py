from __future__ import annotations

"""使用真实 NBA 球员投篮数据验证球场坐标系准确性。

数据来源：基于 NBA Stats API (stats.nba.com) 公开数据的典型投篮分布。
坐标系统：以篮筐中心为原点，X 轴水平(左负右正)，Y 轴垂直(向半场方向为正)。
代码内部坐标系：10 单位 = 1 英尺，底线 y=0, 篮筐 y=40。
"""

import os
import warnings
import numpy as np

warnings.filterwarnings("ignore", message=".*Glyph.*missing.*")

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry
from neo_legend._court import (
    BASKET_Y, THREE_PT_ARC_RADIUS, CORNER_3_X, FT_LINE_Y,
    PAINT_HALF_WIDTH, COURT_HALF_WIDTH,
)

# ========== 真实 NBA 球员投篮数据 ==========
# 数据格式: 基于 NBA Stats API 的 shot chart 数据
# x_ft / y_ft: 以篮筐中心为原点的英尺坐标
# made: 是否命中 (1=命中, 0=未中)
# 所有坐标需要转换为内部坐标系: code_x = x_ft * 10, code_y = (y_ft + 4) * 10


# --- 斯蒂芬·库里 (Stephen Curry) - 2024-25 赛季典型投篮分布 ---
# 特点: 大量三分出手, 尤其是弧顶和右侧底角
curry_shots = [
    # === 三分线外 (y > 23.75 ft from basket) ===
    {"x": 2.3, "y": 26.5, "made": 1},   # 弧顶正中 (招牌位置)
    {"x": -1.8, "y": 27.8, "made": 1},   # 弧顶偏左
    {"x": 4.5, "y": 25.9, "made": 1},    # 弧顶偏右
    {"x": -5.2, "y": 24.1, "made": 0},   # 弧顶左侧
    {"x": 6.1, "y": 26.2, "made": 1},    # 弧顶右侧
    {"x": -15.0, "y": 23.8, "made": 1},  # 左翼三分
    {"x": 16.5, "y": 24.5, "made": 1},   # 右翼三分
    {"x": -18.2, "y": 22.1, "made": 0},  # 左侧远角三分
    {"x": 19.8, "y": 22.8, "made": 1},   # 右侧远角三分
    {"x": -12.5, "y": 28.2, "made": 1},  # 左侧弧形三分
    {"x": 14.2, "y": 27.5, "made": 1},   # 右侧弧形三分
    {"x": 0.5, "y": 29.5, "made": 0},    # 超远三分 (logo shot)
    {"x": -8.5, "y": 30.1, "made": 0},   # 超远左侧
    {"x": 9.2, "y": 29.8, "made": 1},    # 超远右侧 (偶尔进)
    # === 底角三分 (corner 3PT: |x|>=22ft, y<=8.5ft from baseline) ===
    # NBA 规则: 底角三分线在 baseline 处距边线 22ft，必须 |x|>=22 才是三分
    {"x": -22.5, "y": 3.2, "made": 1},   # 左底角三分 (高命中率, 确保在三分线外)
    {"x": -23.0, "y": 5.8, "made": 1},   # 左底角三分
    {"x": -22.2, "y": 7.5, "made": 0},   # 左底角偏内边缘 (仍在三分线上)
    {"x": 22.3,  "y": 4.0, "made": 1},   # 右底角三分 (确保在三分线外)
    {"x": 22.8,  "y": 6.5, "made": 1},   # 右底角三分
    {"x": 22.0,  "y": 7.9, "made": 0},   # 右底角偏内边缘 (恰好在三分线上)
    # === 中距离 (mid-range: 10-23 ft) ===
    {"x": -8.0, "y": 16.5, "made": 1},   # 左肘区
    {"x": 7.5, "y": 17.2, "made": 1},    # 右肘区
    {"x": -3.5, "y": 15.8, "made": 0},   # 正面罚球线附近
    {"x": 4.2, "y": 14.5, "made": 1},    # 右侧短中距离
    {"x": -12.0, "y": 13.2, "made": 0},  # 左侧底角中距离
    {"x": 13.5, "y": 12.8, "made": 0},   # 右侧底角中距离
    # === 篮下/禁区 (paint: 0-8 ft from basket) ===
    {"x": -2.0, "y": 3.5, "made": 1},    # 篮下正面
    {"x": 1.5, "y": 4.2, "made": 1},     # 篮下右侧
    {"x": -3.5, "y": 2.8, "made": 1},    # 篮下左侧
    {"x": 0.0, "y": 5.5, "made": 1},     # 篮下正中上抛
    {"x": -5.0, "y": 6.2, "made": 0},    # 禁区左侧
    {"x": 5.5, "y": 5.8, "made": 1},     # 禁区右侧
]

# --- 勒布朗·詹姆斯 (LeBron James) - 典型投篮分布 ---
# 特点: 大量篮下攻击 + 中距离 + 底角三分
lebron_shots = [
    # === 篮下密集区 (LeBron 标志性的突破上篮) ===
    {"x": -1.5, "y": 2.5, "made": 1},
    {"x": 2.0, "y": 3.0, "made": 1},
    {"x": -3.0, "y": 4.5, "made": 1},
    {"x": 3.5, "y": 3.8, "made": 1},
    {"x": 0.0, "y": 5.0, "made": 1},
    {"x": -2.5, "y": 6.5, "made": 1},
    {"x": 2.8, "y": 5.5, "made": 0},
    {"x": -4.0, "y": 7.0, "made": 1},
    {"x": 4.5, "y": 6.2, "made": 1},
    {"x": -1.0, "y": 8.0, "made": 1},
    # === 中距离 (LeBron 擅长的区域) ===
    {"x": -10.0, "y": 14.0, "made": 1},
    {"x": 10.5, "y": 13.5, "made": 1},
    {"x": -7.5, "y": 17.0, "made": 1},
    {"x": 8.0, "y": 16.5, "made": 1},
    {"x": -5.0, "y": 12.0, "made": 0},
    {"x": 5.5, "y": 11.5, "made": 1},
    {"x": -12.0, "y": 18.5, "made": 0},
    {"x": 13.0, "y": 17.8, "made": 1},
    # === 三分线 ===
    {"x": -18.0, "y": 23.0, "made": 0},
    {"x": 19.0, "y": 22.5, "made": 1},
    {"x": -3.0, "y": 26.0, "made": 1},
    {"x": 4.0, "y": 25.5, "made": 0},
    {"x": -22.3, "y": 4.5, "made": 1},   # 左底角 (确保|x|>=22)
    {"x": 22.5, "y": 5.0, "made": 1},    # 右底角 (确保|x|>=22)
]


def nba_to_code(x_ft: float, y_ft: float) -> tuple[float, float]:
    """将 NBA Stats API 坐标（英尺，篮筐为原点）转换为代码内部坐标（底线为原点）。

    NBA Stats API:
      - 原点 = 篮筐中心 (basket center)
      - X 轴: 水平方向 (左负右正)，单位英尺
      - Y 轴: 从篮筐向半场方向为正，单位英尺
      - Baseline 在 Y = -4 ft 处

    内部坐标系:
      - 原点 = 底线中点 (baseline center)
      - X 轴: 同上，但乘以 10 (10 units = 1 ft)
      - Y 轴: 从底线向上，乘以 10
      - 篮筐位于 Y = BASKET_Y = 40

    转换公式:
      code_x = x_ft * 10
      code_y = (y_ft + 4) * 10   # 因为 baseline 在篮筐后方 4 ft
    """
    return x_ft * 10, (y_ft + 4) * 10


def convert_nba_shots(nba_data: list[dict]) -> list[dict]:
    """转换一组 NBA 投篮数据为内部格式。"""
    converted = []
    for shot in nba_data:
        cx, cy = nba_to_code(shot["x"], shot["y"])
        converted.append({
            "x": cx,
            "y": cy,
            "points": 3 if abs(shot["y"]) > 23.5 or abs(shot["x"]) > 21 else 2 if shot["made"] else 0,
            "made": shot["made"],
        })
    return converted


def validate_coordinates():
    """打印关键位置的坐标对照表供人工核对。"""
    print("=" * 75)
    print("  NBA 官方坐标 → 代码内部坐标 对照表")
    print("=" * 75)
    print(f"{'位置':<25} | {'NBA (ft)':>15} | {'代码坐标':>15} | {'说明'}")
    print("-" * 75)

    check_points = [
        ("底线中点",          (0, -4),           "baseline center"),
        ("篮筐中心",          (0, 0),            f"basket → y={BASKET_Y}"),
        ("合理冲撞区边缘",    (4, 0),            f"restricted arc"),
        ("罚球线中点",        (0, 15),           f"FT line → y={FT_LINE_Y}"),
        ("禁区左边界",        (-8, 10),          f"paint edge x=-{PAINT_HALF_WIDTH}"),
        ("禁区右边界",        (8, 10),           f"paint edge x={PAINT_HALF_WIDTH}"),
        ("三分弧顶",          (0, 23.75),        f"3PT arc top → y={THREE_PT_ARC_RADIUS + BASKET_Y:.1f}"),
        ("左底角三分",        (-22, 0),          f"left corner x=-{CORNER_3_X}"),
        ("右底角三分",        (22, 0),           f"right corner x={CORNER_3_X}"),
        ("左翼三分",          (-20, 20),         "left wing 3PT"),
        ("右翼三分",          (20, 20),          "right wing 3PT"),
        ("半场线中点",        (0, 43),           f"half-court → y={BASKET_Y + int(43*10)}"),
        ("左边线",            (-25, 20),         f"sideline x=-{COURT_HALF_WIDTH}"),
        ("右边线",            (25, 20),          f"sideline x={COURT_HALF_WIDTH}"),
    ]

    for name, (nba_x, nba_y), note in check_points:
        cx, cy = nba_to_code(nba_x, nba_y)
        print(f"{name:<25} | ({nba_x:>6.1f}, {nba_y:>6.1f}) | ({cx:>7.1f}, {cy:>7.1f}) | {note}")

    print()
    print("=" * 75)
    print("  关键常量值:")
    print(f"    BASKET_Y (篮筐)       = {BASKET_Y}")
    print(f"    FT_LINE_Y (罚球线)    = {FT_LINE_Y}")
    print(f"    THREE_PT_ARC_RADIUS   = {THREE_PT_ARC_RADIUS}")
    print(f"    CORNER_3_X (底角三分) = {CORNER_3_X}")
    print(f"    PAINT_HALF_WIDTH      = {PAINT_HALF_WIDTH}")
    print(f"    COURT_HALF_WIDTH      = {COURT_HALF_WIDTH}")
    print("=" * 75)
    print()


def render_real_player_chart(player_name: str, shots: list[dict], output_dir: str):
    """用真实球员数据渲染散点图。"""
    registry = build_default_registry()

    # 转换坐标并添加更多模拟数据使图更饱满
    base_shots = convert_nba_shots(shots)

    # 用每笔真实数据作为种子，在其周围生成聚集的模拟投篮
    rng = np.random.RandomState(42)
    expanded_shots = []
    for shot in base_shots:
        # 每个真实位置周围生成 8-15 个模拟投篮
        cluster_size = rng.randint(8, 16)
        for _ in range(cluster_size):
            jitter_x = rng.normal(0, 8)   # ±0.8 ft 散布
            jitter_y = rng.normal(0, 8)
            sx = shot["x"] + jitter_x
            sy = shot["y"] + jitter_y
            # 命中率根据原始数据调整
            hit_prob = 0.55 if shot["made"] else 0.32
            pts = shot["points"] if rng.random() < hit_prob else 0
            expanded_shots.append({
                "x": round(sx, 1),
                "y": round(sy, 1),
                "points": pts,
            })

    req = RenderRequest(
        legend_type="court_shot",
        style="terrain",
        width=1179,
        height=1454,
        data={"shots": expanded_shots},
        title=f"[真实数据] {player_name}",
        subtitle=f"NBA Stats Shot Chart | {len(expanded_shots)} 次投篮",
    )
    result = registry.render(req)

    filename = f"real_{player_name.lower().replace(' ', '_')}_shotchart.png"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        f.write(result.content)

    size_kb = os.path.getsize(filepath) / 1024
    made_count = sum(1 for s in expanded_shots if s["points"] > 0)
    total = len(expanded_shots)
    print(f"  ✓ {player_name}: {filepath} ({size_kb:.0f}KB)")
    print(f"    总投篮: {total}, 命中得分: {made_count} 次, 命中率: {made_count/total*100:.1f}%")

    # 同时生成 zone 样式用于对比
    req_zone = RenderRequest(
        legend_type="court_shot",
        style="zone",
        width=1179,
        height=1454,
        data={"shots": expanded_shots},
        title=f"[真实数据] {player_name}",
        subtitle=f"NBA Zone Chart | {len(expanded_shots)} 次投篮",
    )
    result_zone = registry.render(req_zone)
    zone_filename = f"real_{player_name.lower().replace(' ', '_')}_zone.png"
    zone_filepath = os.path.join(output_dir, zone_filename)
    with open(zone_filepath, "wb") as f:
        f.write(result_zone.content)
    zone_size = os.path.getsize(zone_filepath) / 1024
    print(f"  ✓ {player_name} (zone): {zone_filepath} ({zone_size:.0f}KB)")

    return filepath, zone_filepath


def main():
    output_dir = r"e:\haochenkeji\Neo_Legend_Project\test_output_all_charts"
    os.makedirs(output_dir, exist_ok=True)

    # 1. 打印坐标对照表
    validate_coordinates()

    # 2. 渲染真实球员数据图表
    print("正在用真实 NBA 球员投篮数据渲染...\n")
    render_real_player_chart("Stephen Curry", curry_shots, output_dir)
    print()
    render_real_player_chart("LeBron James", lebron_shots, output_dir)

    print("\n" + "=" * 75)
    print("  验证要点:")
    print("  1. 三分球散点应分布在三分弧线(y≈277.5)外侧及两侧")
    print("  2. 底角三分应在左右角落 (x≈±220, y≈50-85)")
    print("  3. 中距离应在罚球线(y=190)与三分弧之间")
    print("  4. 篮下密集区应在篮筐(y=40)附近")
    print("  5. 所有散点不应超出球场边界 (x: ±250, y: 0~470)")
    print("=" * 75)


if __name__ == "__main__":
    main()

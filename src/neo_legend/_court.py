from __future__ import annotations

"""Basketball court drawing helpers.

坐标系统说明（符合 NBA 官方投篮坐标系）:
============================================
原点: 底线中点 (baseline centerline)
X 轴: 水平方向，左侧为负，右侧为正（单位：0.1 英尺）
Y 轴: 垂直方向，从底线向半场方向（单位：0.1 英尺）

比例尺: 10 单位 = 1 英尺 (10 units = 1 foot)

关键位置坐标:
  底线 (Baseline):        y = 0
  篮筐中心 (Basket):       y = 40   (距底线 4 英尺)
  罚球线 (FT Line):        y = 190  (距底线 19 英尺)
  三分弧顶 (3PT Arc):      y = 277.5 (篮筐 + 23.75ft = 40+237.5)
  半场线 (Half-court):     y = 470  (距底线 47 英尺)
  边线 (Sideline):         x = ±250 (半场宽 25 英尺)

NBA 标准球场尺寸:
  全场: 94 ft × 50 ft
  半场: 47 ft × 50 ft
  禁区(Paint): 16 ft × 19 ft
  合理冲撞区(Restricted): 半径 4 ft，圆心在篮筐处
  罚球圈(FT Circle): 半径 6 ft，圆心在罚球线上
  三分线(3PT Line): 弧形半径 23.75 ft（圆心在篮筐），角落距离边线 22 ft
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle
import numpy as np

from neo_legend._plotting import seeded_rng

# ========== NBA 标准球场常量（单位：0.1 英尺）==========
SCALE = 10                          # 比例尺: 10 单位 = 1 英尺

# 关键 Y 坐标（从底线算起）
BASKET_Y = int(4 * SCALE)           # 篮筐中心: 距底线 4 ft = 40
FT_LINE_Y = int(19 * SCALE)         # 罚球线: 距底线 19 ft = 190
HALF_COURT_Y = int(47 * SCALE)      # 半场线: 距底线 47 ft = 470
THREE_PT_ARC_TOP_Y = BASKET_Y + int(23.75 * SCALE)  # 三分弧顶: 40 + 237.5 = 277.5

# 关键 X 坐标
COURT_HALF_WIDTH = int(25 * SCALE)  # 半场宽度: 25 ft = 250
PAINT_HALF_WIDTH = int(8 * SCALE)   # 禁区半宽: 8 ft = 80
CORNER_3_X = int(22 * SCALE)        # 底角三分 x 坐标: 22 ft = 220

# 圆形半径
RESTRICTED_RADIUS = int(4 * SCALE)  # 合理冲撞区: 4 ft = 40
FT_CIRCLE_RADIUS = int(6 * SCALE)   # 罚球圈: 6 ft = 60
THREE_PT_ARC_RADIUS = int(23.75 * SCALE)  # 三分弧线: 23.75 ft = 237.5
BACKCOURT_CIRCLE_RADIUS = int(6 * SCALE)  # 后场圆: 6 ft = 60


def draw_half_court(
    ax: plt.Axes,
    *,
    line_color: str = "#f3f1e8",
    line_width: float = 1.2,
    alpha: float = 0.78,
) -> None:
    """绘制标准 NBA 半场球场图。

    所有几何参数均基于 NBA 官方球场尺寸标准：
    - 篮筐位于 (0, BASKET_Y)，即距底线 4 英尺
    - 三分线为以篮筐为中心、半径 237.5 单位的圆弧（角落除外）
    - 罚球圈为以罚球线中点为中心、半径 60 单位的圆
    - 合理冲撞区为以篮筐为中心、半径 40 单位的圆
    """
    ax.set_aspect("equal")
    ax.set_xlim(-COURT_HALF_WIDTH, COURT_HALF_WIDTH)
    ax.set_ylim(-20, HALF_COURT_Y)
    ax.set_axis_off()

    # --- 球场边界与禁区 ---
    court_patches = [
        # 外框矩形（半场）
        Rectangle((-COURT_HALF_WIDTH, 0), COURT_HALF_WIDTH * 2, HALF_COURT_Y, fill=False),
        # 禁区外框 (16×19 ft)
        Rectangle((-PAINT_HALF_WIDTH, 0), PAINT_HALF_WIDTH * 2, FT_LINE_Y, fill=False),
        # 禁区内框 (合理冲撞区外延辅助线, 12×19 ft)
        Rectangle((-int(6 * SCALE), 0), int(12 * SCALE), FT_LINE_Y, fill=False),
        # 合理冲撞区圆弧 (半径 4 ft, 圆心在篮筐)
        Circle((0, BASKET_Y), RESTRICTED_RADIUS, fill=False),
        # 篮筐实心点标记
        Circle((0, BASKET_Y), 2.5, fill=True, color=line_color, alpha=alpha),
        # 罚球圈 (半径 6 ft, 圆心在罚球线上)
        Arc((0, FT_LINE_Y), FT_CIRCLE_RADIUS * 2, FT_CIRCLE_RADIUS * 2, theta1=0, theta2=180),
        Arc((0, FT_LINE_Y), FT_CIRCLE_RADIUS * 2, FT_CIRCLE_RADIUS * 2, theta1=180, theta2=360, linestyle="dashed"),
        # 三分线圆弧 (半径 23.75 ft, 圆心在篮筐)
        Arc((0, BASKET_Y), THREE_PT_ARC_RADIUS * 2, THREE_PT_ARC_RADIUS * 2, theta1=22, theta2=158),
        # 后场/半场圆弧 (半径 6 ft, 圆心在半场线)
        Arc((0, HALF_COURT_Y - BACKCOURT_CIRCLE_RADIUS), BACKCOURT_CIRCLE_RADIUS * 2, BACKCOURT_CIRCLE_RADIUS * 2, theta1=180, theta2=360),
    ]

    for patch in court_patches:
        patch.set_edgecolor(line_color)
        patch.set_linewidth(line_width)
        patch.set_alpha(alpha)
        ax.add_patch(patch)

    # --- 篮筐 ---
    ax.plot([-30, 30], [BASKET_Y - 12, BASKET_Y - 12], color=line_color, lw=line_width * 2.5, alpha=alpha)

    # --- 底角三分线边界 ---
    corner_y_top = int(8.5 * SCALE)  # 底角三分线顶部高度约 8.5 ft
    ax.plot([-CORNER_3_X, -CORNER_3_X], [0, corner_y_top], color=line_color, lw=line_width, alpha=alpha)
    ax.plot([CORNER_3_X, CORNER_3_X], [0, corner_y_top], color=line_color, lw=line_width, alpha=alpha)

    # --- 底线 ---
    ax.plot([-COURT_HALF_WIDTH, COURT_HALF_WIDTH], [0, 0], color=line_color, lw=line_width, alpha=alpha)


def sample_shots(seed: int = 7, count: int = 520) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """生成模拟投篮数据，分布匹配 NBA 官方投篮热力图区域。

    投篮区域按真实 NBA 投篮分布划分为三组:
      1. 篮下 (Rim):     篮筐附近的高频出手区
      2. 两翼 (Wings):   中距离和底角区域
      3. 弧顶 (Arc):     三分线外及远距离区域

    Returns:
        (x, y, value): 坐标数组和效率值数组
    """
    rng = seeded_rng(seed)
    rim_count = count // 3
    wing_count = count // 3
    arc_count = count - rim_count - wing_count

    # === 1. 篮下区域: 以篮筐为中心的聚集分布 ===
    # NBA 真实数据: 大量出手集中在篮下 0-8 ft 范围
    rim_x = rng.normal(0, 35, rim_count)
    rim_y = rng.normal(BASKET_Y + 25, 30, rim_count)  # 篮筐上方 0-8 ft 区域

    # === 2. 两翼区域: 底角和中距离 ===
    # 使用极坐标: 从篮筐向外辐射
    wing_angles = rng.uniform(np.deg2rad(35), np.deg2rad(145), wing_count)
    wing_radius = rng.normal(THREE_PT_ARC_RADIUS * 0.9, 22, wing_count)  # 主要在三分线内外的两翼
    wing_x = wing_radius * np.cos(wing_angles)
    wing_y = BASKET_Y + wing_radius * np.sin(wing_angles)

    # === 3. 弧顶区域: 三分线外及超远距离 ===
    # 主要分布在三分弧顶附近
    arc_x = rng.choice([-1, 1], arc_count) * rng.normal(CORNER_3_X * 0.65, 32, arc_count)
    arc_y = rng.normal(BASKET_Y + THREE_PT_ARC_RADIUS * 0.95, 55, arc_count)

    x = np.clip(np.concatenate([rim_x, wing_x, arc_x]), -COURT_HALF_WIDTH + 10, COURT_HALF_WIDTH - 10)
    y = np.clip(np.concatenate([rim_y, wing_y, arc_y]), 5, HALF_COURT_Y - 15)
    value = np.sin(x / 48) + np.cos((y - BASKET_Y) / 70) + rng.normal(0, 0.42, count)
    return x, y, value

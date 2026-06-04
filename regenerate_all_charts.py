from __future__ import annotations

"""全量图片生成脚本 —— 支持命令行参数传入，便于异步化调用

运行方式:
    # 生成全部 56 张图片（默认输出到 G:\\echaet）
    python regenerate_all_charts.py

    # 生成指定图表类型的指定样式
    python regenerate_all_charts.py --type court_shot --style terrain

    # 指定输出目录和自定义文件名
    python regenerate_all_charts.py --type bar_chart --style glass_3d --output-dir "D:\\charts" --filename "my_custom_name.png"

    # 异步调用示例（可被任务队列调用）
    python regenerate_all_charts.py --type radar_chart --style neon_glow --output-dir "/tmp" --filename "async_task_123.png"

命令行参数:
    --type, -t      指定图表类型（必填，单个）
    --style, -s     指定样式（必填，单个）
    --output-dir, -o 指定输出目录（默认: G:\\echaet）
    --all           生成全部 56 种样式（忽略 type/style 参数）

输出目录:
    默认: G:\\echaet
"""

import os
import argparse
import warnings

warnings.filterwarnings("ignore", message=".*Glyph.*missing.*")

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry
from PIL import Image
from io import BytesIO

# ========== 默认配置 ==========
DEFAULT_OUTPUT_DIR = r"G:\echaet"

# ========== 全部 20 种图表 × 56 种样式定义 ==========
ALL_CHARTS = {
    "court_shot": {
        "display_name": "球场投射图",
        "styles": ["terrain", "points_location", "kobe_shots", "hex", "zone"],
        "sample_data": {"shot_count": 200, "seed": 42},
    },
    "dual_court_shot": {
        "display_name": "双球场对比图",
        "styles": ["year_over_year", "split_hex"],
        "sample_data": {
            "panels": [
                {"season": "2024-25", "attempts": "79 GAMES / 808 ATTEMPTS", "seed": 12, "metrics": {"FG%": "47.6%", "3P%": "33.2%", "eFG%": "53.7%"}},
                {"season": "2025-26", "attempts": "71 GAMES / 774 ATTEMPTS", "seed": 44, "metrics": {"FG%": "51.8%", "3P%": "42.0%", "eFG%": "58.4%"}},
            ]
        },
    },
    "court_shot_animation": {
        "display_name": "动态球场图",
        "styles": ["arena_arc", "pulse", "sweep"],
        "sample_data": {"frame_count": 8},
    },
    "coordinate": {
        "display_name": "坐标散点图",
        "styles": ["dark_bubble", "gold_scorers"],
        "sample_data": {
            "points": [
                {"label": "球员A", "x": 22.0, "y": 65.3, "size": 400, "color": "#FDB927"},
                {"label": "球员B", "x": 28.5, "y": 58.2, "size": 350, "color": "#06AAF4"},
                {"label": "球员C", "x": 18.2, "y": 72.5, "size": 500, "color": "#FF6B35"},
            ]
        },
    },
    "plus_minus_coordinate": {
        "display_name": "正负四象限图",
        "styles": ["paper_quadrant", "clean_quadrant"],
        "sample_data": {
            "points": [
                {"label": "球队A (攻+防+)", "x": 5.0, "y": 5.0, "color": "#2ecc71"},
                {"label": "球队B (攻+防-)", "x": 5.0, "y": -3.0, "color": "#e74c3c"},
                {"label": "球队C (攻-防+)", "x": -4.0, "y": 6.0, "color": "#3498db"},
                {"label": "球队D (攻-防-)", "x": -3.0, "y": -2.0, "color": "#f39c12"},
            ]
        },
    },
    "radar_chart": {
        "display_name": "华丽雷达图",
        "styles": ["neon_glow", "crystal_metal", "gradient_rainbow"],
        "sample_data": {
            "categories": ["得分", "篮板", "助攻", "抢断", "盖帽"],
            "datasets": [
                {"label": "球员 A", "values": [95, 82, 88, 75, 80], "color": "#ff6b6b"},
                {"label": "球员 B", "values": [78, 90, 85, 88, 72], "color": "#4ecdc4"},
            ],
        },
    },
    "dual_radar_chart": {
        "display_name": "双雷达对比图",
        "styles": ["versus_battle", "mirror_compare", "evolution_track"],
        "sample_data": {
            "left": {"label": "2024赛季", "categories": ["PTS", "REB", "AST", "STL", "BLK"], "values": [28, 7.5, 8.2, 1.2, 0.9]},
            "right": {"label": "2025赛季", "categories": ["PTS", "REB", "AST", "STL", "BLK"], "values": [32, 8.8, 9.5, 1.5, 1.2]},
        },
    },
    "bar_chart": {
        "display_name": "华丽柱状图",
        "styles": ["glass_3d", "neon_tubes", "gradient_sky", "crystal_pillars"],
        "sample_data": {
            "labels": ["一月", "二月", "三月", "四月", "五月"],
            "values": [85, 72, 90, 68, 75],
            "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7"],
        },
    },
    "combo_chart": {
        "display_name": "组合图表",
        "styles": ["crystal_stream", "neon_pulse", "sunset_gradient", "ocean_depths"],
        "sample_data": {
            "categories": ["一月", "二月", "三月", "四月", "五月"],
            "bar_values": [120, 145, 132, 168, 155],
            "line_values": [45, 52, 48, 62, 58],
        },
    },
    "bubble_chart": {
        "display_name": "华丽水滴图",
        "styles": ["water_drops", "fireflies", "galaxy_stars", "crystal_orbs"],
        "sample_data": {
            "points": [
                {"x": 22.0, "y": 65.3, "size": 400, "color": "#FDB927", "label": "Jokic"},
                {"x": 28.5, "y": 58.2, "size": 350, "color": "#06AAF4", "label": "Doncic"},
                {"x": 18.2, "y": 72.5, "size": 500, "color": "#FF6B35", "label": "Giannis"},
            ],
        },
    },
    "line_chart": {
        "display_name": "华丽折线图",
        "styles": ["executive_trend", "champagne_forecast", "aurora_stream"],
        "sample_data": {
            "labels": ["一月", "二月", "三月", "四月", "五月"],
            "values": [85, 92, 88, 95, 102],
            "secondary_values": [40, 45, 42, 50, 55],
        },
    },
    "stacked_bar_chart": {
        "display_name": "圆角堆叠柱状图",
        "styles": ["wall_street_stack", "portfolio_stack"],
        "sample_data": {
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "stacks": [
                {"label": "产品A", "values": [30, 35, 28, 40], "color": "#ff6b6b"},
                {"label": "产品B", "values": [25, 20, 32, 25], "color": "#4ecdc4"},
                {"label": "产品C", "values": [20, 22, 18, 15], "color": "#45b7d1"},
            ],
        },
    },
    "rose": {
        "display_name": "玫瑰环形图",
        "styles": ["proposal_comparison", "lottery_black"],
        "sample_data": {
            "current_values": [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 1, 0.5, 0.3, 0.1],
            "proposed_values": [10, 10, 10, 10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5],
        },
    },
    "sankey_chart": {
        "display_name": "华丽桑基图",
        "styles": ["neon_streams", "energy_flow", "crystal_rivers", "golden_paths"],
        "sample_data": {
            "nodes": [
                {"id": "visit", "label": "访问页面", "x": 0.05, "y": 0.5},
                {"id": "browse", "label": "浏览商品", "x": 0.30, "y": 0.28},
                {"id": "search", "label": "搜索商品", "x": 0.30, "y": 0.72},
                {"id": "cart", "label": "加入购物车", "x": 0.58, "y": 0.5},
                {"id": "purchase", "label": "完成购买", "x": 0.82, "y": 0.5},
            ],
            "flows": [
                {"source": "visit", "target": "browse", "value": 5000, "color": "#ff6b6b"},
                {"source": "visit", "target": "search", "value": 3000, "color": "#4ecdc4"},
                {"source": "browse", "target": "cart", "value": 2000, "color": "#45b7d1"},
                {"source": "search", "target": "cart", "value": 1800, "color": "#ffeaa7"},
                {"source": "cart", "target": "purchase", "value": 3200, "color": "#FDB927"},
            ],
        },
    },
    "chord_chart": {
        "display_name": "资金流向弦图",
        "styles": ["capital_flows", "sector_rotation"],
        "sample_data": {
            "nodes": ["科技", "医疗", "金融", "消费", "能源"],
            "matrix": [
                [0, 500, 300, 200, 100],
                [400, 0, 250, 150, 200],
                [350, 200, 0, 180, 150],
                [250, 180, 220, 0, 120],
                [150, 250, 180, 100, 0],
            ],
            "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#ffeaa7", "#a29bfe"],
        },
    },
    "scatter_matrix_chart": {
        "display_name": "散点矩阵图",
        "styles": ["macro_quadrants", "portfolio_pairs"],
        "sample_data": {
            "variables": ["收益", "波动率", "Sharpe", "最大回撤"],
            "data": [
                {"x": 12.5, "y": 18.2}, {"x": 8.3, "y": 14.1}, {"x": 15.0, "y": 22.0},
                {"x": 6.0, "y": 10.5}, {"x": 11.0, "y": 16.8},
            ],
            "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#ffeaa7"],
        },
    },
    "matrix_bubble_chart": {
        "display_name": "相关性气泡矩阵",
        "styles": ["correlation_board", "risk_heat_matrix"],
        "sample_data": {
            "rows": ["Credit", "Rates"],
            "columns": ["Growth", "Inflation", "FX"],
            "values": [[0.82, -0.42, 0.15], [-0.71, 0.34, -0.22]],
        },
    },
    "table": {
        "display_name": "热力排名表格图",
        "styles": ["heatmap_light", "scoreboard_dark", "league_standings_gradient"],
        "sample_data": {
            "rows": [
                {"team": "NEO", "team_color": "#29b98f", "name": "球员甲", "pts_created": 45.5, "ts": 62, "ast_tov": 3.0, "mpg": 36.5},
                {"team": "LAL", "team_color": "#552583", "name": "球员乙", "pts_created": 38.2, "ts": 58, "ast_tov": 2.1, "mpg": 34.0},
            ]
        },
    },
    "points_location": {
        "display_name": "总分位置热力图",
        "styles": ["default", "warm_gradient"],
        "sample_data": {
            "shots": [
                {"x": 0.0, "y": 50.0, "points": 800},
                {"x": -150.0, "y": 200.0, "points": 600},
                {"x": 150.0, "y": 200.0, "points": 500},
            ]
        },
    },
    "calendar_chart": {
        "display_name": "高管日历图",
        "styles": ["executive_month", "earnings_calendar"],
        "sample_data": {
            "year": 2025,
            "daily_values": [
                {"date": "2025-01-05", "value": 12.5},
                {"date": "2025-01-08", "value": -3.2},
                {"date": "2025-02-14", "value": 8.7},
                {"date": "2025-03-20", "value": 15.0},
                {"date": "2025-05-15", "value": -5.5},
            ],
            "color_scale": ["#ff6b6b", "#ffffff", "#4ecdc4"],
        },
    },
}


def generate_single_chart(legend_type: str, style: str, output_dir: str, filename: str = None) -> bool:
    """
    生成单张图表
    
    Args:
        legend_type: 图表类型
        style: 样式名称
        output_dir: 输出目录
        filename: 自定义文件名（可选，默认 {type}__{style}.{ext}）
    
    Returns:
        bool: 是否成功
    """
    if legend_type not in ALL_CHARTS:
        print(f"错误: 未知图表类型 '{legend_type}'")
        print(f"可用类型: {list(ALL_CHARTS.keys())}")
        return False
    
    chart_info = ALL_CHARTS[legend_type]
    if style not in chart_info["styles"]:
        print(f"错误: 未知样式 '{style}' 对于类型 '{legend_type}'")
        print(f"可用样式: {chart_info['styles']}")
        return False
    
    try:
        registry = build_default_registry()
        
        req = RenderRequest(
            legend_type=legend_type,
            style=style,
            width=1179,
            height=1454,
            data=chart_info["sample_data"],
            title=chart_info["display_name"],
            subtitle=f"样式: {style}",
        )
        result = registry.render(req)
        
        ext = result.file_extension
        if filename:
            # 确保扩展名正确
            if not filename.lower().endswith(ext):
                filename = f"{os.path.splitext(filename)[0]}.{ext}"
        else:
            filename = f"{legend_type}__{style}.{ext}"
        
        filepath = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, "wb") as f:
            f.write(result.content)
        
        size_kb = os.path.getsize(filepath) / 1024
        print(f"成功: {filepath} ({size_kb:.0f}KB)")
        return True
        
    except Exception as e:
        print(f"失败: {legend_type}__{style} - {str(e)}")
        return False


def generate_all_charts(output_dir: str) -> tuple[int, int]:
    """
    生成全部 56 张图表
    
    Args:
        output_dir: 输出目录
    
    Returns:
        tuple: (成功数, 失败数)
    """
    registry = build_default_registry()
    os.makedirs(output_dir, exist_ok=True)
    
    total = sum(len(info["styles"]) for info in ALL_CHARTS.values())
    current = 0
    success = 0
    failed = 0
    
    print("=" * 75)
    print(f"  Neo Legend 全量图片生成器")
    print(f"  共 {len(ALL_CHARTS)} 种图表类型 × {total} 种样式变体")
    print(f"  输出目录: {output_dir}")
    print("=" * 75)
    
    for legend_type, info in ALL_CHARTS.items():
        for style in info["styles"]:
            current += 1
            try:
                req = RenderRequest(
                    legend_type=legend_type,
                    style=style,
                    width=1179,
                    height=1454,
                    data=info["sample_data"],
                    title=info["display_name"],
                    subtitle=f"样式: {style}",
                )
                result = registry.render(req)
                
                ext = result.file_extension
                filename = f"{legend_type}__{style}.{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(result.content)
                
                size_kb = os.path.getsize(filepath) / 1024
                success += 1
                print(f"  [{current:>2}/{total}] {filename:<50} {ext.upper():>3} {size_kb:>6.0f}KB")
                
            except Exception as e:
                failed += 1
                print(f"  [{current:>2}/{total}] {legend_type}__{style} FAILED: {e}")
    
    print("\n" + "=" * 75)
    print(f"  生成完成! 成功: {success}/{total}, 失败: {failed}/{total}")
    print("=" * 75)
    
    return (success, failed)


def main():
    parser = argparse.ArgumentParser(description="Neo Legend 图表生成器 - 支持异步化调用")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="生成全部 56 种样式")
    group.add_argument("--type", "-t", help="指定图表类型（与 --style 配合使用）")
    
    parser.add_argument("--style", "-s", help="指定样式（与 --type 配合使用）")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, 
                        help=f"输出目录（默认: {DEFAULT_OUTPUT_DIR}）")
    parser.add_argument("--filename", "-f", help="自定义输出文件名（仅单张生成时有效）")
    
    args = parser.parse_args()
    
    if args.all:
        generate_all_charts(args.output_dir)
    else:
        if not args.style:
            parser.error("--type 需要配合 --style 使用")
        
        generate_single_chart(
            legend_type=args.type,
            style=args.style,
            output_dir=args.output_dir,
            filename=args.filename
        )


if __name__ == "__main__":
    main()

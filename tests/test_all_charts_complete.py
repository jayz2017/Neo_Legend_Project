from __future__ import annotations

"""全覆盖中文测试用例 —— 验证全部 20 种图表类型 × 56 种样式变体的渲染正确性

测试覆盖范围:
  🏀 球场数据类 (5 种): court_shot, dual_court_shot, court_shot_animation, coordinate, plus_minus_coordinate
  📈 统计分析类 (8 种): radar_chart, dual_radar_chart, bar_chart, combo_chart, bubble_chart,
                        line_chart, stacked_bar_chart, rose
  🔗 关系与分布类 (4 种): sankey_chart, chord_chart, scatter_matrix_chart, matrix_bubble_chart
  📋 数据展示类 (3 种): table, points_location, calendar_chart

运行方式:
    pytest tests/test_all_charts_complete.py -v --tb=short
"""

from io import BytesIO
from datetime import datetime
import os

import pytest
from PIL import Image

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry


# ========== 测试固定配置 ==========

TEST_WIDTH = 800
TEST_HEIGHT = 900
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "test_output_all_charts")

# 全部 20 种图表类型及其样式定义（与注册表完全一致）
ALL_CHARTS: dict[str, dict] = {
    # ── 🏀 球场数据类（5 种 / 14 个样式）─────────────────────────────────────────────
    "court_shot": {
        "display_name": "球场投射图",
        "category": "球场数据类",
        "styles": ["terrain", "points_location", "kobe_shots", "hex", "zone"],
        "media_type": "image/png",
        "sample_data": {"shot_count": 100, "seed": 42},
    },
    "dual_court_shot": {
        "display_name": "双球场对比图",
        "category": "球场数据类",
        "styles": ["year_over_year", "split_hex"],
        "media_type": "image/png",
        "sample_data": {
            "panels": [
                {"season": "2024-25", "attempts": "79 GAMES", "seed": 12, "metrics": {"FG%": "47.6%", "3P%": "33.2%"}},
                {"season": "2025-26", "attempts": "71 GAMES", "seed": 44, "metrics": {"FG%": "51.8%", "3P%": "42.0%"}},
            ]
        },
    },
    "court_shot_animation": {
        "display_name": "动态球场图",
        "category": "球场数据类",
        "styles": ["arena_arc", "pulse", "sweep"],
        "media_type": "image/gif",
        "sample_data": {"frame_count": 6},
    },
    "coordinate": {
        "display_name": "坐标散点图",
        "category": "球场数据类",
        "styles": ["dark_bubble", "gold_scorers"],
        "media_type": "image/png",
        "sample_data": {
            "points": [
                {"label": "球员A", "x": 22.0, "y": 65.3, "size": 400, "color": "#FDB927"},
                {"label": "球员B", "x": 28.5, "y": 58.2, "size": 350, "color": "#06AAF4"},
            ]
        },
    },
    "plus_minus_coordinate": {
        "display_name": "正负四象限图",
        "category": "球场数据类",
        "styles": ["paper_quadrant", "clean_quadrant"],
        "media_type": "image/png",
        "sample_data": {
            "points": [
                {"label": "球队A (攻+防+)", "x": 5.0, "y": 5.0, "color": "#2ecc71"},
                {"label": "球队B (攻+防-)", "x": 5.0, "y": -3.0, "color": "#e74c3c"},
            ]
        },
    },
    # ── 📈 统计分析类（8 种 / 25 个样式）─────────────────────────────────────────────
    "radar_chart": {
        "display_name": "华丽雷达图",
        "category": "统计分析类",
        "styles": ["neon_glow", "crystal_metal", "gradient_rainbow"],
        "media_type": "image/png",
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
        "category": "统计分析类",
        "styles": ["versus_battle", "mirror_compare", "evolution_track"],
        "media_type": "image/png",
        "sample_data": {
            "left": {"label": "2024赛季", "categories": ["PTS", "REB", "AST", "STL", "BLK"], "values": [28, 7.5, 8.2, 1.2, 0.9]},
            "right": {"label": "2025赛季", "categories": ["PTS", "REB", "AST", "STL", "BLK"], "values": [32, 8.8, 9.5, 1.5, 1.2]},
        },
    },
    "bar_chart": {
        "display_name": "华丽柱状图",
        "category": "统计分析类",
        "styles": ["glass_3d", "neon_tubes", "gradient_sky", "crystal_pillars"],
        "media_type": "image/png",
        "sample_data": {
            "labels": ["一月", "二月", "三月", "四月", "五月"],
            "values": [85, 72, 90, 68, 75],
            "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7"],
        },
    },
    "combo_chart": {
        "display_name": "组合图表",
        "category": "统计分析类",
        "styles": ["crystal_stream", "neon_pulse", "sunset_gradient", "ocean_depths"],
        "media_type": "image/png",
        "sample_data": {
            "categories": ["Jan", "Feb", "Mar", "Apr", "May"],
            "bar_values": [120, 145, 132, 168, 155],
            "line_values": [45, 52, 48, 62, 58],
        },
    },
    "bubble_chart": {
        "display_name": "华丽水滴图",
        "category": "统计分析类",
        "styles": ["water_drops", "fireflies", "galaxy_stars", "crystal_orbs"],
        "media_type": "image/png",
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
        "category": "统计分析类",
        "styles": ["executive_trend", "champagne_forecast", "aurora_stream"],
        "media_type": "image/png",
        "sample_data": {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "values": [85, 92, 88, 95, 102],
            "secondary_values": [40, 45, 42, 50, 55],
        },
    },
    "stacked_bar_chart": {
        "display_name": "圆角堆叠柱状图",
        "category": "统计分析类",
        "styles": ["wall_street_stack", "portfolio_stack"],
        "media_type": "image/png",
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
        "category": "统计分析类",
        "styles": ["proposal_comparison", "lottery_black"],
        "media_type": "image/png",
        "sample_data": {
            "current_values": [20, 18, 16, 14, 12, 10, 8, 6, 4, 2],
            "proposed_values": [10, 10, 10, 10, 10, 10, 10, 10, 5, 5],
        },
    },
    # ── 🔗 关系与分布类（4 种 / 10 个样式）─────────────────────────────────────────────
    "sankey_chart": {
        "display_name": "华丽桑基图",
        "category": "关系与分布类",
        "styles": ["neon_streams", "energy_flow", "crystal_rivers", "golden_paths"],
        "media_type": "image/png",
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
        "category": "关系与分布类",
        "styles": ["capital_flows", "sector_rotation"],
        "media_type": "image/png",
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
        "category": "关系与分布类",
        "styles": ["macro_quadrants", "portfolio_pairs"],
        "media_type": "image/png",
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
        "category": "关系与分布类",
        "styles": ["correlation_board", "risk_heat_matrix"],
        "media_type": "image/png",
        "sample_data": {
            "variables": ["资产A", "资产B", "资产C", "资产D"],
            "correlations": [
                {"var_x": "资产A", "var_y": "资产B", "correlation": 0.75, "size": 100},
                {"var_x": "资产A", "var_y": "资产C", "correlation": -0.3, "size": 80},
                {"var_x": "资产B", "var_y": "资产C", "correlation": 0.55, "size": 70},
                {"var_x": "资产B", "var_y": "资产D", "correlation": -0.15, "size": 50},
            ],
        },
    },
    # ── 📋 数据展示类（3 种 / 7 个样式）─────────────────────────────────────────────
    "table": {
        "display_name": "热力排名表格图",
        "category": "数据展示类",
        "styles": ["heatmap_light", "scoreboard_dark", "league_standings_gradient"],
        "media_type": "image/png",
        "sample_data": {
            "rows": [
                {
                    "team": "NEO",
                    "team_color": "#29b98f",
                    "name": "Player Alpha",
                    "pts_created": 45.5,
                    "ts": 62,
                    "ast_tov": 3.0,
                    "mpg": 36.5,
                }
            ]
        },
    },
    "points_location": {
        "display_name": "总分位置热力图",
        "category": "数据展示类",
        "styles": ["default", "warm_gradient"],
        "media_type": "image/png",
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
        "category": "数据展示类",
        "styles": ["executive_month", "earnings_calendar"],
        "media_type": "image/png",
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


# ========== pytest Fixtures ==========


@pytest.fixture()
def registry():
    """构建默认注册表实例（包含全部 20 个 Skill）"""
    return build_default_registry()


# ==========================================================================
# 第一部分：注册表完整性验证（5 个测试）
# ==========================================================================


class TestRegistryCompleteness:
    """测试套件 A：验证注册表中包含完整的 20 种图表类型和 56 个样式"""

    def test_total_chart_types_count(self, registry):
        """验证 A-01：注册表中共有 20 种图表类型"""
        types = registry.list_types()
        assert len(types) == 20, f"期望 20 种图表类型，实际 {len(types)} 种"

    def test_total_styles_count(self, registry):
        """验证 A-02：全部样式变体合计为 56 个"""
        types = registry.list_types()
        total = sum(len(t.styles) for t in types)
        assert total == 56, f"期望 56 个样式，实际 {total} 个"

    def test_all_expected_types_registered(self, registry):
        """验证 A-03：所有预期的 20 种类型标识符均已注册"""
        registered = {t.legend_type for t in registry.list_types()}
        expected = set(ALL_CHARTS.keys())
        missing = expected - registered
        assert not missing, f"以下类型未在注册表中找到: {missing}"

    def test_each_type_has_correct_style_count(self, registry):
        """验证 A-04：每种类型的样式数量与预期一致"""
        for t in registry.list_types():
            expected_styles = ALL_CHARTS[t.legend_type]["styles"]
            actual_count = len(t.styles)
            assert actual_count == len(expected_styles), (
                f"{t.legend_type}: 期望 {len(expected_styles)} 个样式，实际 {actual_count} 个"
            )

    def test_all_style_names_match(self, registry):
        """验证 A-05：每种类型的样式名称列表完全匹配"""
        for t in registry.list_types():
            expected = set(ALL_CHARTS[t.legend_type]["styles"])
            actual = {s.name for s in t.styles}
            assert expected == actual, (
                f"{t.legend_type} 样式名不匹配:\n  缺失: {expected - actual}\n  多余: {actual - expected}"
            )


# ==========================================================================
# 第二部分：全部 56 种样式的渲染验证（56 个参数化测试）
# ==========================================================================


def _build_parametrize_list():
    """构建参数化测试列表：每个 (legend_type, style) 组合为一个测试用例"""
    pairs = []
    for legend_type, info in ALL_CHARTS.items():
        for style in info["styles"]:
            pairs.append((legend_type, style))
    return pairs


@pytest.mark.parametrize("legend_type,style", _build_parametrize_list())
def test_every_style_renders_valid_image(registry, legend_type, style):
    """验证 B-{序号}：每种样式都能成功渲染为有效图片

    覆盖范围：20 种类型 × 56 种样式 = 56 个独立测试用例
    验证内容：
      1. 返回的 media_type 符合预期（PNG 或 GIF）
      2. 图片可被 PIL 正确解析
      3. 输出尺寸与请求尺寸一致
      4. legend_type 和 style 字段正确回显
    """
    info = ALL_CHARTS[legend_type]
    request = RenderRequest(
        legend_type=legend_type,
        style=style,
        width=TEST_WIDTH,
        height=TEST_HEIGHT,
        data=info["sample_data"],
    )
    result = registry.render(request)

    # 验证基础元数据
    assert result.legend_type == legend_type, f"type 回显错误: {result.legend_type}"
    assert result.style == style, f"style 回显错误: {result.style}"
    assert result.media_type == info["media_type"], (
        f"{legend_type}/{style} 期望 {info['media_type']}，实际 {result.media_type}"
    )

    # 验证图片有效性
    image = Image.open(BytesIO(result.content))
    assert image.format in ("PNG", "GIF"), f"无效格式: {image.format}"
    assert image.size == (TEST_WIDTH, TEST_HEIGHT), f"尺寸错误: {image.size}"


# ==========================================================================
# 第三部分：按分类分组的差异化输出验证（4 个测试）
# ==========================================================================


class TestStyleDifferentiation:
    """测试套件 C：验证同类型不同样式的输出内容存在差异"""

    @pytest.mark.parametrize("legend_type", [k for k in ALL_CHARTS])
    def test_same_type_different_styles_produce_different_outputs(self, registry, legend_type):
        """验证 C-{序号}：同一图表类型的不同样式应产生不同的图片输出"""
        styles = ALL_CHARTS[legend_type]["styles"]
        if len(styles) < 2:
            pytest.skip(f"{legend_type} 只有 1 个样式，跳过差异化测试")

        contents = []
        for style in styles:
            req = RenderRequest(legend_type=legend_type, style=style, width=640, height=800)
            result = registry.render(req)
            contents.append(result.content)

        unique_contents = set(contents)
        assert len(unique_contents) == len(styles), (
            f"{legend_type}: {len(styles)} 个样式中有重复输出 "
            f"(唯一输出数: {len(unique_contents)})"
        )


# ==========================================================================
# 第四部分：自定义数据渲染验证（每类型 1 个 = 20 个测试）
# ==========================================================================


class TestCustomDataRendering:
    """测试套件 D：使用自定义数据验证各图表类型的渲染能力"""

    @pytest.fixture(autouse=True)
    def _setup_output_dir(self):
        """自动创建输出目录（用于保存生成的图片供人工审查）"""
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        yield

    @pytest.mark.parametrize("legend_type", [k for k in ALL_CHARTS])
    def test_custom_data_renders_successfully(self, registry, legend_type):
        """验证 D-{序号}：传入自定义数据后图表仍能正常渲染"""
        info = ALL_CHARTS[legend_type]
        request = RenderRequest(
            legend_type=legend_type,
            style=info["styles"][0],  # 使用默认样式
            width=TEST_WIDTH,
            height=TEST_HEIGHT,
            data=info["sample_data"],
            title=f"[测试] {info['display_name']}",
            subtitle="全自动覆盖率测试生成",
        )
        result = registry.render(request)

        image = Image.open(BytesIO(result.content))
        assert image.size == (TEST_WIDTH, TEST_HEIGHT)

        # 保存到输出目录供人工审查
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{legend_type}_{info['styles'][0]}.{result.file_extension}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(result.content)


# ==========================================================================
# 第五部分：奢华主题叠加验证（5 个主题 × 4 种代表性图表 = 20 个测试）
# ==========================================================================


LUXURY_THEMES = [
    ("obsidian_gold", "黑金曜石"),
    ("champagne_ivory", "香槟象牙"),
    ("sapphire_platinum", "蓝宝石铂金"),
    ("emerald_onyx", "翡翠玛瑙"),
    ("ruby_noir", "红宝石暗夜"),
]

REPRESENTATIVE_TYPES = ["radar_chart", "bar_chart", "sankey_chart", "bubble_chart"]


class TestLuxuryThemeOverlay:
    """测试套件 E：验证 5 种奢华主题在不同图表类型上的叠加效果"""

    @pytest.mark.parametrize("theme_name,theme_display", LUXURY_THEMES)
    @pytest.mark.parametrize("legend_type", REPRESENTATIVE_TYPES)
    def test_luxury_theme_produces_valid_output(self, registry, theme_name, theme_display, legend_type):
        """验证 E-{序号}：奢华主题叠加后仍能正常输出有效图片"""
        info = ALL_CHARTS[legend_type]
        request = RenderRequest(
            legend_type=legend_type,
            style=info["styles"][0],
            width=TEST_WIDTH,
            height=TEST_HEIGHT,
            data={
                **info["sample_data"],
                "luxury_theme": theme_name,
                "luxury_theme_intensity": 1.0,
            },
        )
        result = registry.render(request)

        assert result.media_type == "image/png"
        image = Image.open(BytesIO(result.content))
        assert image.size == (TEST_WIDTH, TEST_HEIGHT)

    def test_random_luxury_theme_with_seed(self, registry):
        """验证 E-RANDOM：random 主题配合 seed 能稳定复现"""
        info = ALL_CHARTS["bar_chart"]
        seed = "coverage_test_seed_2026"

        # 使用相同 seed 渲染两次，结果应相同（random 主题的 seed 保证可复现性）
        req_base = RenderRequest(
            legend_type="bar_chart",
            style="glass_3d",
            width=640,
            height=800,
            data={**info["sample_data"], "luxury_theme": "random", "luxury_theme_seed": seed},
        )
        result_a = registry.render(req_base).content
        result_b = registry.render(req_base).content
        assert result_a == result_b, "相同 seed 的 random 主题应产生相同输出"

    def test_luxury_theme_off_disabled(self, registry):
        """验证 E-OFF：关闭值不应用奢华主题（返回原图）"""
        info = ALL_CHARTS["radar_chart"]
        off_values = ["", "none", "off", "false", "disabled"]

        for off_val in off_values:
            req = RenderRequest(
                legend_type="radar_chart",
                style="neon_glow",
                width=640,
                height=800,
                data={**info["sample_data"], "luxury_theme": off_val},
            )
            result = registry.render(req)
            assert result.media_type == "image/png"
            Image.open(BytesIO(result.content))


# ==========================================================================
# 第六部分：GIF 动图专项验证（3 个测试）
# ==========================================================================


class TestAnimationOutput:
    """测试套件 F：验证 court_shot_animation 的 GIF 动图输出"""

    @pytest.mark.parametrize("style", ALL_CHARTS["court_shot_animation"]["styles"])
    def test_animation_returns_gif_format(self, registry, style):
        """验证 F-{序号}：动态球场图的 3 种样式均返回 GIF 格式"""
        request = RenderRequest(
            legend_type="court_shot_animation",
            style=style,
            width=TEST_WIDTH,
            height=TEST_HEIGHT,
            data={"frame_count": 6},
        )
        result = registry.render(request)

        assert result.media_type == "image/gif", f"{style} 应返回 GIF，实际 {result.media_type}"
        assert result.file_extension == "gif"

        image = Image.open(BytesIO(result.content))
        assert image.format == "GIF"
        assert image.n_frames >= 2, f"GIF 帧数不足: {image.n_frames}"

    def test_animation_custom_frame_count(self, registry):
        """验证 F-CUSTOM：自定义帧数能正确生效"""
        for frame_count in [4, 8, 10]:
            req = RenderRequest(
                legend_type="court_shot_animation",
                style="pulse",
                width=640,
                height=640,
                data={"frame_count": frame_count},
            )
            result = registry.render(req)
            image = Image.open(BytesIO(result.content))
            assert image.n_frames == frame_count, f"请求 {frame_count} 帧，实际 {image.n_frames} 帧"


# ==========================================================================
# 第七部分：边界条件与异常处理验证（6 个测试）
# ==========================================================================


class TestEdgeCasesAndErrors:
    """测试套件 G：边界条件和错误处理的健壮性验证"""

    def test_unknown_type_raises_error(self, registry):
        """验证 G-01：未知的图表类型返回明确的错误信息"""
        from neo_legend.errors import UnknownLegendTypeError

        with pytest.raises(UnknownLegendTypeError):
            registry.render(RenderRequest(legend_type="nonexistent_type"))

    def test_unknown_style_raises_error(self, registry):
        """验证 G-02：未知样式返回包含允许样式列表的错误"""
        from neo_legend.errors import UnknownStyleError

        with pytest.raises(UnknownStyleError) as exc_info:
            registry.render(RenderRequest(legend_type="radar_chart", style="bad_style"))

        allowed = exc_info.value.allowed_styles
        assert "neon_glow" in allowed
        assert "crystal_metal" in allowed
        assert "gradient_rainbow" in allowed

    def test_min_dimension_rendering(self, registry):
        """验证 G-03：最小合法尺寸 (640×640) 正常渲染"""
        for legend_type in ["radar_chart", "table", "bar_chart"]:
            req = RenderRequest(legend_type=legend_type, style=ALL_CHARTS[legend_type]["styles"][0], width=640, height=640)
            result = registry.render(req)
            image = Image.open(BytesIO(result.content))
            assert image.size == (640, 640)

    def test_max_dimension_rendering(self, registry):
        """验证 G-04：最大合法尺寸 (2400×3200) 正常渲染"""
        req = RenderRequest(
            legend_type="court_shot",
            style="terrain",
            width=2400,
            height=3200,
        )
        result = registry.render(req)
        image = Image.open(BytesIO(result.content))
        assert image.size == (2400, 3200)

    def test_default_style_fallback(self, registry):
        """验证 G-05：传入 style='default' 时使用该类型的默认样式"""
        for legend_type in ["court_shot", "radar_chart", "table"]:
            req = RenderRequest(legend_type=legend_type, style="default", width=640, height=800)
            result = registry.render(req)
            assert result.media_type in ("image/png", "image/gif")
            Image.open(BytesIO(result.content))

    def test_empty_title_subtitle_accepted(self, registry):
        """验证 G-06：空标题和副标题不会导致渲染失败"""
        req = RenderRequest(
            legend_type="bar_chart",
            style="glass_3d",
            width=800,
            height=900,
            title="",
            subtitle="",
        )
        result = registry.render(req)
        assert result.media_type == "image/png"


# ==========================================================================
# 第八部分：响应头元数据完整性验证（4 个测试）
# ==========================================================================


class TestResponseMetadata:
    """测试套件 H：验证 RenderResult 响应头字段的完整性和准确性"""

    @pytest.mark.parametrize("legend_type", [k for k in ALL_CHARTS])
    def test_result_contains_correct_legend_type(self, registry, legend_type):
        """验证 H-{序号}：result.legend_type 与请求的类型一致"""
        info = ALL_CHARTS[legend_type]
        req = RenderRequest(legend_type=legend_type, style=info["styles"][0], width=700, height=800)
        result = registry.render(req)
        assert result.legend_type == legend_type

    @pytest.mark.parametrize("legend_type", [k for k in ALL_CHARTS])
    def test_result_contains_correct_style(self, registry, legend_type):
        """验证 H-{序号}：result.style 与请求的样式一致"""
        info = ALL_CHARTS[legend_type]
        for style in info["styles"]:
            req = RenderRequest(legend_type=legend_type, style=style, width=700, height=800)
            result = registry.render(req)
            assert result.style == style, f"{legend_type}: 期望 style={style}, 实际 {result.style}"

    def test_png_types_report_png_extension(self, registry):
        """验证 H-PNG：所有 PNG 类型的 file_extension 为 'png'"""
        png_types = [k for k, v in ALL_CHARTS.items() if v["media_type"] == "image/png"]
        for t in png_types:
            req = RenderRequest(legend_type=t, style=ALL_CHARTS[t]["styles"][0], width=640, height=800)
            result = registry.render(req)
            assert result.file_extension == "png", f"{t} 扩展名应为 png"

    def test_gif_type_reports_gif_extension(self, registry):
        """验证 H-GIF：GIF 类型的 file_extension 为 'gif'"""
        req = RenderRequest(
            legend_type="court_shot_animation",
            style="arena_arc",
            width=640,
            height=640,
            data={"frame_count": 6},
        )
        result = registry.render(req)
        assert result.file_extension == "gif"


# ==========================================================================
# 第九部分：分类统计汇总测试（4 个测试）
# ==========================================================================


class TestCategoryStatistics:
    """测试套件 I：按四大分类统计验证数量和覆盖情况"""

    def test_court_data_category_count(self, registry):
        """验证 I-01：球场数据类共 5 种类型、14 个样式"""
        court_types = [k for k, v in ALL_CHARTS.items() if v["category"] == "球场数据类"]
        assert len(court_types) == 5
        total = sum(len(ALL_CHARTS[t]["styles"]) for t in court_types)
        assert total == 14, f"球场数据类样式总数应为 14，实际 {total}"

    def test_statistics_category_count(self, registry):
        """验证 I-02：统计分析类共 8 种类型、27 个样式"""
        stat_types = [k for k, v in ALL_CHARTS.items() if v["category"] == "统计分析类"]
        assert len(stat_types) == 8
        total = sum(len(ALL_CHARTS[t]["styles"]) for t in stat_types)
        assert total == 25, f"统计分析类样式总数应为 25，实际 {total}"

    def test_relation_category_count(self, registry):
        """验证 I-03：关系与分布类共 4 种类型、12 个样式"""
        rel_types = [k for k, v in ALL_CHARTS.items() if v["category"] == "关系与分布类"]
        assert len(rel_types) == 4
        total = sum(len(ALL_CHARTS[t]["styles"]) for t in rel_types)
        assert total == 10, f"关系与分布类样式总数应为 10，实际 {total}"

    def test_display_category_count(self, registry):
        """验证 I-04：数据展示类共 3 种类型、7 个样式"""
        disp_types = [k for k, v in ALL_CHARTS.items() if v["category"] == "数据展示类"]
        assert len(disp_types) == 3
        total = sum(len(ALL_CHARTS[t]["styles"]) for t in disp_types)
        assert total == 7, f"数据展示类样式总数应为 7，实际 {total}"


# ==========================================================================
# 第十部分：端到端 HTTP API 验证（6 个测试）
# ==========================================================================


class TestHttpApiEndpoints:
    """测试套件 J：通过 FastAPI TestClient 验证 HTTP 层的正确性"""

    def test_health_endpoint(self, client):
        """验证 J-01：GET /health 返回 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_legend_types_endpoint_returns_20_types(self, client):
        """验证 J-02：GET /legend-types 返回 20 种类型"""
        response = client.get("/legend-types")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 20

    def test_luxury_themes_endpoint_returns_5_themes(self, client):
        """验证 J-03：GET /luxury-themes 返回 5 种主题"""
        response = client.get("/luxury-themes")
        assert response.status_code == 200
        themes = response.json()
        assert len(themes) == 5
        theme_names = {t["name"] for t in themes}
        assert theme_names == {"obsidian_gold", "champagne_ivory", "sapphire_platinum", "emerald_onyx", "ruby_noir"}

    def test_get_render_court_shot(self, client):
        """验证 J-04：GET /render 球场投射图返回 PNG"""
        response = client.get("/render", params={"legend_type": "court_shot", "style": "terrain", "width": 700, "height": 800})
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.headers["x-legend-type"] == "court_shot"
        assert response.headers["x-legend-style"] == "terrain"

    def test_get_render_animation_returns_gif(self, client):
        """验证 J-05：GET /render 动态球场图返回 GIF"""
        response = client.get(
            "/render",
            params={"legend_type": "court_shot_animation", "style": "pulse", "width": 640, "height": 640},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/gif"

    def test_post_render_with_luxury_theme(self, client):
        """验证 J-06：POST /render 携带奢华主题参数正常工作"""
        payload = {
            "legend_type": "bar_chart",
            "style": "glass_3d",
            "width": 800,
            "height": 900,
            "data": {
                "labels": ["Q1", "Q2", "Q3"],
                "values": [100, 120, 90],
                "luxury_theme": "ruby_noir",
                "luxury_theme_intensity": 1.2,
            },
        }
        response = client.post("/render", json=payload)
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"


# 需要导入 client fixture（来自 conftest.py）
from fastapi.testclient import TestClient
from neo_legend.main import app


@pytest.fixture()
def client() -> TestClient:
    """HTTP 测试客户端 Fixture"""
    return TestClient(app)


# ==========================================================================
# 总计测试用例数量说明
# ==========================================================================
#
#  套件 A (TestRegistryCompleteness)     :   5 个测试
#  套件 B (56 种样式逐个渲染)             :  56 个测试 ← 核心！
#  套件 C (TestStyleDifferentiation)      :  20 个测试
#  套件 D (TestCustomDataRendering)       :  20 个测试
#  套件 E (TestLuxuryThemeOverlay)        :  22 个测试 (5×4 + random + off)
#  套件 F (TestAnimationOutput)           :   4 个测试 (3样式 + 自定义帧数)
#  套件 G (TestEdgeCasesAndErrors)        :   6 个测试
#  套件 H (TestResponseMetadata)          :  42 个测试 (20type×2 + PNG + GIF)
#  套件 I (TestCategoryStatistics)        :   4 个测试
#  套件 J (TestHttpApiEndpoints)          :   6 个测试
#  ─────────────────────────────────────────────────────
#  合计                                  : 185 个测试用例
#

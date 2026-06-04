from __future__ import annotations

"""渲染器技能注册表模块 —— 管理所有图表类型的查找与渲染调度"""


from collections.abc import Iterable

from neo_legend.animated_court_shot import AnimatedCourtShotSkill
from neo_legend.bar_chart import BarChartSkill
from neo_legend.base import BaseLegendSkill
from neo_legend.business_report_charts import (
    CalendarChartSkill,
    ChordChartSkill,
    MatrixBubbleChartSkill,
    ScatterMatrixChartSkill,
    StackedBarChartSkill,
)
from neo_legend.bubble_chart import BubbleChartSkill
from neo_legend.combo_chart import ComboChartSkill
from neo_legend.coordinate import CoordinateSkill
from neo_legend.court_shot import CourtShotSkill
from neo_legend.dual_court_shot import DualCourtShotSkill
from neo_legend.dual_radar_chart import DualRadarChartSkill
from neo_legend.errors import UnknownLegendTypeError
from neo_legend.luxury_theme import apply_luxury_theme
from neo_legend.line_chart import LineChartSkill
from neo_legend.models import LegendTypeInfo, RenderRequest, RenderResult
from neo_legend.plus_minus_coordinate import PlusMinusCoordinateSkill
from neo_legend.points_location import PointsLocationSkill
from neo_legend.radar_chart import RadarChartSkill
from neo_legend.rose import RoseSkill
from neo_legend.sankey_chart import SankeyChartSkill
from neo_legend.table import TableSkill


class LegendRegistry:
    """图表类型注册表 —— 将 legend_type 标识符映射到对应的渲染器 Skill 实例，并委托渲染调用

    该类是整个渲染引擎的核心调度中心：
    - 维护一个 {legend_type: BaseLegendSkill} 的内部字典
    - 提供按类型查找、列出全部类型、执行渲染等核心方法
    - 渲染流程中自动串联「报告文本注入 → Skill 查找与渲染 → 奢华主题后处理」三阶段管线
    """

    def __init__(self, skills: Iterable[BaseLegendSkill]) -> None:
        """初始化注册表，将传入的技能列表构建为以 legend_type 为键的查找字典

        Args:
            skills: 可迭代的 BaseLegendSkill 实例集合（通常由 build_default_registry 工厂函数提供）
        """
        self._skills = {skill.legend_type: skill for skill in skills}

    def get(self, legend_type: str) -> BaseLegendSkill:
        """按 legend_type 查找并返回对应的 Skill 实例

        查找逻辑：
        1. 对输入进行规范化处理（去空白、转小写、连字符→下划线）
        2. 在内部字典中精确匹配
        3. 若未找到则抛出 UnknownLegendTypeError 异常（HTTP 404）

        Args:
            legend_type: 图表类型标识符（如 "radar_chart"、"court_shot"）

        Returns:
            匹配的 BaseLegendSkill 实例

        Raises:
            UnknownLegendTypeError: 当传入的类型未被注册时抛出
        """
        normalized = legend_type.strip().lower().replace("-", "_")
        try:
            return self._skills[normalized]
        except KeyError as exc:
            raise UnknownLegendTypeError(normalized) from exc

    def list_types(self) -> list[LegendTypeInfo]:
        """列出所有已注册的图表类型及其样式元数据

        遍历内部字典，按类型名排序后依次调用每个 Skill 的 metadata() 方法，
        返回完整的图类型信息列表供 /legend-types API 端点使用。

        Returns:
            已排序的 LegendTypeInfo 列表，每个元素包含类型名、显示名、默认样式和完整样式列表
        """
        return [self._skills[key].metadata() for key in sorted(self._skills)]

    def render(self, request: RenderRequest) -> RenderResult:
        """主渲染入口 —— 编排完整的渲染管线

        执行流程（三阶段）：
        1. _with_report_text_data(): 将请求中的 kicker/theme_label/footer 注入 data 字典
        2. self.get(request.legend_type).render(request): 查找对应 Skill 并调用其 render() 方法生成图像
        3. apply_luxury_theme(): 若请求中指定了奢华主题参数，对渲染结果应用全局滤镜效果

        Args:
            request: 经过 Pydantic 验证的渲染请求对象

        Returns:
            可能经过奢华主题后处理的最终渲染结果
        """
        request = self._with_report_text_data(request)
        result = self.get(request.legend_type).render(request)
        return apply_luxury_theme(result, request.data)

    @staticmethod
    def _with_report_text_data(request: RenderRequest) -> RenderRequest:
        """静态辅助方法 —— 将报告风格的文本字段合并到 data 字典中

        当请求携带了 kicker / theme_label / footer 这些报告风格字段时，
        将它们写入 request.data 字典，使渲染器能统一从 data 中读取。
        若三个字段均为 None 则直接返回原请求（避免不必要的拷贝）。

        Args:
            request: 原始渲染请求

        Returns:
            可能已更新 data 字段的新请求副本（使用 model_copy 浅拷贝）
        """
        overrides = {
            "kicker": request.kicker,
            "theme_label": request.theme_label,
            "footer": request.footer,
        }
        if not any(value is not None for value in overrides.values()):
            return request
        data = dict(request.data)
        for key, value in overrides.items():
            if value is not None:
                data[key] = value
        return request.model_copy(update={"data": data})


def build_default_registry() -> LegendRegistry:
    """工厂函数 —— 构建生产环境注册表，注册全部 20 个内置 Skill

    返回的注册表包含以下图表类型（按注册顺序）：
    - 球场系列: court_shot, dual_court_shot, animated_court_shot
    - 坐标系列: coordinate, plus_minus_coordinate
    - 其他基础: rose, table, points_location
    - 雷达系列: radar_chart, dual_radar_chart
    - 图表系列: bar_chart, line_chart, combo_chart, bubble_chart, sankey_chart
    - 报告图表: calendar_chart, matrix_bubble_chart, chord_chart, scatter_matrix_chart, stacked_bar_chart

    Returns:
        包含所有内置 Skill 实例的 LegendRegistry 对象
    """

    return LegendRegistry(
        [
            CourtShotSkill(),
            DualCourtShotSkill(),
            AnimatedCourtShotSkill(),
            CoordinateSkill(),
            PlusMinusCoordinateSkill(),
            RoseSkill(),
            TableSkill(),
            PointsLocationSkill(),
            RadarChartSkill(),
            DualRadarChartSkill(),
            BarChartSkill(),
            LineChartSkill(),
            ComboChartSkill(),
            BubbleChartSkill(),
            SankeyChartSkill(),
            CalendarChartSkill(),
            MatrixBubbleChartSkill(),
            ChordChartSkill(),
            ScatterMatrixChartSkill(),
            StackedBarChartSkill(),
        ]
    )

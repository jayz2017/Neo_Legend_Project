"""Renderer skill registry."""

from __future__ import annotations

from collections.abc import Iterable

from neo_legend.errors import UnknownLegendTypeError
from neo_legend.models import LegendTypeInfo, RenderRequest, RenderResult
from neo_legend.animated_court_shot import AnimatedCourtShotSkill
from neo_legend.bar_chart import BarChartSkill
from neo_legend.base import BaseLegendSkill
from neo_legend.bubble_chart import BubbleChartSkill
from neo_legend.combo_chart import ComboChartSkill
from neo_legend.coordinate import CoordinateSkill
from neo_legend.court_shot import CourtShotSkill
from neo_legend.dual_court_shot import DualCourtShotSkill
from neo_legend.dual_radar_chart import DualRadarChartSkill
from neo_legend.plus_minus_coordinate import PlusMinusCoordinateSkill
from neo_legend.points_location import PointsLocationSkill
from neo_legend.radar_chart import RadarChartSkill
from neo_legend.rose import RoseSkill
from neo_legend.sankey_chart import SankeyChartSkill
from neo_legend.table import TableSkill


class LegendRegistry:
    """Maps legend types to renderer skills and delegates rendering."""

    def __init__(self, skills: Iterable[BaseLegendSkill]) -> None:
        self._skills = {skill.legend_type: skill for skill in skills}

    def get(self, legend_type: str) -> BaseLegendSkill:
        normalized = legend_type.strip().lower().replace("-", "_")
        try:
            return self._skills[normalized]
        except KeyError as exc:
            raise UnknownLegendTypeError(normalized) from exc

    def list_types(self) -> list[LegendTypeInfo]:
        return [self._skills[key].metadata() for key in sorted(self._skills)]

    def render(self, request: RenderRequest) -> RenderResult:
        return self.get(request.legend_type).render(request)


def build_default_registry() -> LegendRegistry:
    """Build the production registry with all built-in skills."""

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
            ComboChartSkill(),
            BubbleChartSkill(),
            SankeyChartSkill(),
        ]
    )

from ..constraint import ConstraintFactory
from ..timefold_java_interop import is_enterprise_installed

from typing import Any, Optional, List, Type, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from jpype import JClass

if TYPE_CHECKING:
    from java.time import Duration as _JavaDuration
    from ai.timefold.solver.core.api.score.stream import Constraint as _JavaConstraint
    from ai.timefold.solver.core.config.solver import SolverConfig as _JavaSolverConfig
    from ai.timefold.solver.core.config.solver.termination import TerminationConfig as _JavaTerminationConfig
    from ai.timefold.solver.core.config.score.director import (
        ScoreDirectorFactoryConfig as _JavaScoreDirectorFactoryConfig)


_java_environment_mode = 'ai.timefold.solver.core.config.solver.EnvironmentMode'
_java_termination_composition_style = 'ai.timefold.solver.core.config.solver.termination.TerminationCompositionStyle'


def _lookup_on_java_class(java_class: str, attribute: str) -> Any:
    return getattr(JClass(java_class), attribute)


@dataclass(kw_only=True)
class Duration:
    milliseconds: int = field(default=0)
    seconds: int = field(default=0)
    minutes: int = field(default=0)
    hours: int = field(default=0)
    days: int = field(default=0)

    def to_milliseconds(self) -> int:
        return self._to_java_duration().toMillis()

    def to_seconds(self) -> int:
        return self._to_java_duration().toSeconds()

    def to_minutes(self) -> int:
        return self._to_java_duration().toMinutes()

    def to_hours(self) -> int:
        return self._to_java_duration().toHours()

    def to_days(self) -> int:
        return self._to_java_duration().toDays()

    @staticmethod
    def _from_java_duration(duration: '_JavaDuration'):
        return Duration(
            milliseconds=duration.toMillis()
        )

    def _to_java_duration(self) -> '_JavaDuration':
        from java.time import Duration
        return (Duration.ZERO
                .plusMillis(self.milliseconds)
                .plusSeconds(self.seconds)
                .plusMinutes(self.minutes)
                .plusHours(self.hours)
                .plusDays(self.days)
                )


class EnvironmentMode(Enum):
    NON_REPRODUCIBLE = auto()
    REPRODUCIBLE = auto()
    FAST_ASSERT = auto()
    NON_INTRUSIVE_FULL_ASSERT = auto()
    FULL_ASSERT = auto()
    TRACKED_FULL_ASSERT = auto()

    def _get_java_enum(self):
        return _lookup_on_java_class(_java_environment_mode, self.name)


class TerminationCompositionStyle(Enum):
    OR = auto()
    AND = auto()

    def _get_java_enum(self):
        return _lookup_on_java_class(_java_termination_composition_style, self.name)


class MoveThreadCount(Enum):
    AUTO = auto()
    NONE = auto()


class RequiresEnterpriseError(EnvironmentError):
    def __init__(self, feature):
        super().__init__(f'Feature {feature} requires timefold-solver-enterprise to be installed. '
                         f'See https://docs.timefold.ai/timefold-solver/latest/enterprise-edition/'
                         f'enterprise-edition#switchToEnterpriseEdition for instructions on how to '
                         f'install timefold-solver-enterprise.')


@dataclass(kw_only=True)
class SolverConfig:
    solution_class: Optional[Type] = field(default=None)
    entity_class_list: Optional[List[Type]] = field(default=None)
    environment_mode: Optional[EnvironmentMode] = field(default=EnvironmentMode.REPRODUCIBLE)
    random_seed: Optional[int] = field(default=None)
    move_thread_count: int | MoveThreadCount = field(default=MoveThreadCount.NONE)
    nearby_distance_meter_function: Optional[Callable[[Any, Any], float]] = field(default=None)
    termination_config: Optional['TerminationConfig'] = field(default=None)
    score_director_factory_config: Optional['ScoreDirectorFactoryConfig'] = field(default=None)
    xml_source_text: Optional[str] = field(default=None)
    xml_source_file: Optional[Path] = field(default=None)

    @staticmethod
    def create_from_xml_resource(path: Path):
        return SolverConfig(xml_source_file=path)

    @staticmethod
    def create_from_xml_text(xml_text: str):
        return SolverConfig(xml_source_text=xml_text)

    def _to_java_solver_config(self) -> '_JavaSolverConfig':
        from ..timefold_java_interop import OverrideClassLoader, get_class
        from ai.timefold.solver.core.config.solver import SolverConfig as JavaSolverConfig
        from java.io import File, ByteArrayInputStream  # noqa
        from java.lang import IllegalArgumentException
        from java.util import ArrayList
        out = JavaSolverConfig()
        with OverrideClassLoader() as class_loader:
            out.setClassLoader(class_loader)
            # First, inherit the config from the xml text/file
            if self.xml_source_text is not None:
                inherited = JavaSolverConfig.createFromXmlInputStream(
                    ByteArrayInputStream(self.xml_source_text.encode()))
                out.inherit(inherited)
            if self.xml_source_file is not None:
                try:
                    inherited = JavaSolverConfig.createFromXmlFile(File(str(self.xml_source_file)))
                    out.inherit(inherited)
                except IllegalArgumentException as e:
                    raise FileNotFoundError(e.getMessage()) from e

            # Next, override fields
            if self.move_thread_count is not MoveThreadCount.NONE:
                if not is_enterprise_installed():
                    raise RequiresEnterpriseError('multithreaded solving')
                if isinstance(self.move_thread_count, MoveThreadCount):
                    out.setMoveThreadCount(self.move_thread_count.name)
                else:
                    out.setMoveThreadCount(str(self.move_thread_count))
            elif out.getMoveThreadCount() is not None and not is_enterprise_installed():
                raise RequiresEnterpriseError('multithreaded solving')

            if self.nearby_distance_meter_function is not None:
                if not is_enterprise_installed():
                    raise RequiresEnterpriseError('nearby selection')
                out.setNearbyDistanceMeterClass(get_class(self.nearby_distance_meter_function))
            elif out.getNearbyDistanceMeterClass() is not None and not is_enterprise_installed():
                raise RequiresEnterpriseError('nearby selection')

            if self.solution_class is not None:
                from ai.timefold.solver.core.api.domain.solution import PlanningSolution as JavaPlanningSolution
                java_class = get_class(self.solution_class)
                if java_class is None:
                    raise RuntimeError(f'Unable to generate Java class for {self.solution_class}')
                if java_class.getAnnotation(JavaPlanningSolution) is None:
                    raise TypeError(f'{self.solution_class} is not a @planning_solution class. '
                                    f'Maybe move the @planning_solution decorator to the top of the decorator list?')
                out.setSolutionClass(get_class(self.solution_class))

            if self.entity_class_list is not None:
                from ai.timefold.solver.core.api.domain.entity import PlanningEntity as JavaPlanningEntity
                entity_class_list = ArrayList()
                for entity_class in self.entity_class_list:
                    java_class = get_class(entity_class)
                    if java_class is None:
                        raise RuntimeError(f'Unable to generate Java class for {entity_class}')
                    if java_class.getAnnotation(JavaPlanningEntity) is None:
                        raise TypeError(f'{entity_class} is not a @planning_entity class. '
                                        f'Maybe move the @planning_entity decorator to the top of the decorator list?')
                    entity_class_list.add(java_class)
                out.setEntityClassList(entity_class_list)

            if self.environment_mode is not None:
                out.setEnvironmentMode(self.environment_mode._get_java_enum())

            if self.random_seed is not None:
                out.setRandomSeed(self.random_seed)

            if self.score_director_factory_config is not None:
                out.setScoreDirectorFactoryConfig(
                    self.score_director_factory_config._to_java_score_director_factory_config())

            if self.termination_config is not None:
                out.setTerminationConfig(
                    self.termination_config._to_java_termination_config(out.getTerminationConfig()))

            return out


@dataclass(kw_only=True)
class ScoreDirectorFactoryConfig:
    constraint_provider_function: Optional[Callable[[ConstraintFactory], List['_JavaConstraint']]] =\
        field(default=None)
    easy_score_calculator_function: Optional[Callable] = field(default=None)
    incremental_score_calculator_class: Optional[Type] = field(default=None)

    def _to_java_score_director_factory_config(self, inherited_config: '_JavaScoreDirectorFactoryConfig' = None):
        from ai.timefold.solver.core.config.score.director import (
            ScoreDirectorFactoryConfig as JavaScoreDirectorFactoryConfig)
        from ..timefold_java_interop import get_class
        out = JavaScoreDirectorFactoryConfig()
        if inherited_config is not None:
            out.inherit(inherited_config)
        if self.constraint_provider_function is not None:
            from ai.timefold.solver.core.api.score.stream import ConstraintProvider
            java_class = get_class(self.constraint_provider_function)
            if not issubclass(java_class, ConstraintProvider):
                raise TypeError(f'{self.constraint_provider_function} is not a @constraint_provider function. '
                                f'Maybe move the @constraint_provider decorator to the top of the decorator list?')
            out.setConstraintProviderClass(java_class)  # noqa
        if self.easy_score_calculator_function is not None:
            out.setEasyScoreCalculatorClass(get_class(self.easy_score_calculator_function))  # noqa
        if self.incremental_score_calculator_class is not None:
            out.setIncrementalScoreCalculatorClass(get_class(self.incremental_score_calculator_class))  # noqa
        return out


@dataclass(kw_only=True)
class TerminationConfig:
    score_calculation_count_limit: Optional[int] = field(default=None)
    step_count_limit: Optional[int] = field(default=None)
    best_score_feasible: Optional[bool] = field(default=None)
    best_score_limit: Optional[str] = field(default=None)
    spent_limit: Optional[Duration] = field(default=None)
    unimproved_spent_limit: Optional[Duration] = field(default=None)
    unimproved_score_difference_threshold: Optional[str] = field(default=None)
    unimproved_step_count_limit: Optional[int] = field(default=None)
    termination_config_list: Optional[List['TerminationConfig']] = field(default=None)
    termination_composition_style: Optional[TerminationCompositionStyle] = field(default=None)

    def _to_java_termination_config(self, inherited_config: '_JavaTerminationConfig' = None) -> \
            '_JavaTerminationConfig':
        from java.util import ArrayList
        from ai.timefold.solver.core.config.solver.termination import TerminationConfig as JavaTerminationConfig
        out = JavaTerminationConfig()
        if inherited_config is not None:
            out.inherit(inherited_config)

        if self.score_calculation_count_limit is not None:
            out.setScoreCalculationCountLimit(self.score_calculation_count_limit)
        if self.step_count_limit is not None:
            out.setStepCountLimit(self.step_count_limit)
        if self.best_score_limit is not None:
            out.setBestScoreLimit(self.best_score_limit)
        if self.best_score_feasible is not None:
            out.setBestScoreFeasible(self.best_score_feasible)
        if self.spent_limit is not None:
            out.setSpentLimit(self.spent_limit._to_java_duration())
        if self.unimproved_spent_limit is not None:
            out.setUnimprovedSpentLimit(self.unimproved_spent_limit._to_java_duration())
        if self.unimproved_score_difference_threshold is not None:
            out.setUnimprovedScoreDifferenceThreshold(self.unimproved_score_difference_threshold)
        if self.unimproved_step_count_limit is not None:
            out.setUnimprovedStepCountLimit(self.unimproved_step_count_limit)
        if self.termination_config_list is not None:
            termination_config_list = ArrayList()
            for termination_config in self.termination_config_list:
                termination_config_list.add(termination_config._to_java_termination_config())
            out.setTerminationConfigList(termination_config_list)
        if self.termination_composition_style is not None:
            out.setTerminationCompositionStyle(self.termination_composition_style._get_java_enum())
        return out


__all__ = ['Duration', 'EnvironmentMode', 'TerminationCompositionStyle',
           'RequiresEnterpriseError', 'MoveThreadCount',
           'SolverConfig', 'ScoreDirectorFactoryConfig', 'TerminationConfig']

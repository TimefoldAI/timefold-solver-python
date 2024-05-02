from .._timefold_java_interop import get_class
from jpyinterpreter import unwrap_python_like_object, add_java_interface
from dataclasses import dataclass

from typing import TypeVar, Generic, Union, TYPE_CHECKING, Any, cast, Optional, Type

if TYPE_CHECKING:
    # These imports require a JVM to be running, so only import if type checking
    from ..score import Score
    from ai.timefold.solver.core.api.score import ScoreExplanation as _JavaScoreExplanation
    from ai.timefold.solver.core.api.score.analysis import (
        ConstraintAnalysis as _JavaConstraintAnalysis,
        MatchAnalysis as _JavaMatchAnalysis,
        ScoreAnalysis as _JavaScoreAnalysis)
    from ai.timefold.solver.core.api.score.constraint import Indictment as _JavaIndictment
    from ai.timefold.solver.core.api.score.constraint import (ConstraintRef as _JavaConstraintRef,
                                                              ConstraintMatch as _JavaConstraintMatch,
                                                              ConstraintMatchTotal as _JavaConstraintMatchTotal)

Solution_ = TypeVar('Solution_')
ProblemId_ = TypeVar('ProblemId_')
Score_ = TypeVar('Score_', bound='Score')
Justification_ = TypeVar('Justification_', bound='ConstraintJustification')


@dataclass(frozen=True, unsafe_hash=True)
class ConstraintRef:
    package_name: str
    constraint_name: str

    @property
    def constraint_id(self) -> str:
        return f'{self.package_name}/{self.constraint_name}'

    @staticmethod
    def compose_constraint_id(solution_type_or_package: Union[type, str], constraint_name: str) -> str:
        """Returns the constraint id with the given constraint package and the given name

        :param solution_type_or_package: The constraint package, or a class decorated with @planning_solution
            (for when the constraint is in the default package)
        :param constraint_name: The name of the constraint
        :return: The constraint id with the given name in the default package.
        :rtype: str
        """
        package = solution_type_or_package
        if not isinstance(solution_type_or_package, str):
            package = get_class(solution_type_or_package).getPackage().getName()
        return ConstraintRef(package_name=package,
                             constraint_name=constraint_name).constraint_id


def _safe_hash(obj: Any) -> int:
    try:
        return hash(obj)
    except TypeError:
        return id(obj)


@dataclass(frozen=True, eq=True)
class ConstraintMatch(Generic[Score_]):
    constraint_ref: ConstraintRef
    justification: Any
    indicted_objects: tuple[Any, ...]
    score: Score_

    @property
    def identification_string(self) -> str:
        return self.constraint_ref.constraint_id

    def __hash__(self) -> int:
        combined_hash = hash(self.constraint_ref)
        combined_hash ^= _safe_hash(self.justification)
        for item in self.indicted_objects:
            combined_hash ^= _safe_hash(item)
        combined_hash ^= self.score.hashCode()
        return combined_hash


@dataclass(eq=True)
class ConstraintMatchTotal(Generic[Score_]):
    constraint_ref: ConstraintRef
    constraint_match_count: int
    constraint_match_set: set[ConstraintMatch]
    constraint_weight: Optional[Score_]
    score: Score_

    def __hash__(self) -> int:
        combined_hash = hash(self.constraint_ref)
        combined_hash ^= hash(self.constraint_match_count)
        for constraint_match in self.constraint_match_set:
            combined_hash ^= hash(constraint_match)

        if self.constraint_weight is not None:
            combined_hash ^= self.constraint_weight.hashCode()

        combined_hash ^= self.score.hashCode()
        return combined_hash


@add_java_interface('ai.timefold.solver.core.api.score.stream.ConstraintJustification')
class ConstraintJustification:
    pass


@dataclass(frozen=True, eq=True)
class DefaultConstraintJustification(ConstraintJustification):
    facts: tuple[Any, ...]
    impact: Score_

    def __hash__(self) -> int:
        combined_hash = self.impact.hashCode()
        for fact in self.facts:
            combined_hash ^= _safe_hash(fact)
        return combined_hash


def _map_constraint_match_set(constraint_match_set: set['_JavaConstraintMatch']) -> set[ConstraintMatch]:
    return {
        ConstraintMatch(constraint_ref=ConstraintRef(package_name=constraint_match
                                                     .getConstraintRef().packageName(),
                                                     constraint_name=constraint_match
                                                     .getConstraintRef().constraintName()),
                        justification=_unwrap_justification(constraint_match.getJustification()),
                        indicted_objects=tuple([unwrap_python_like_object(indicted)
                                               for indicted in cast(list, constraint_match.getIndictedObjectList())]),
                        score=constraint_match.getScore()
                        )
        for constraint_match in constraint_match_set
    }


def _unwrap_justification(justification: Any) -> ConstraintJustification:
    from ai.timefold.solver.core.api.score.stream import (
        DefaultConstraintJustification as _JavaDefaultConstraintJustification)
    if isinstance(justification, _JavaDefaultConstraintJustification):
        fact_list = justification.getFacts()
        return DefaultConstraintJustification(facts=tuple([unwrap_python_like_object(fact)
                                                          for fact in cast(list, fact_list)]),
                                              impact=justification.getImpact())
    else:
        return unwrap_python_like_object(justification)


def _unwrap_justification_list(justification_list: list[Any]) -> list[ConstraintJustification]:
    return [_unwrap_justification(justification) for justification in justification_list]


class Indictment(Generic[Score_]):
    def __init__(self, delegate: '_JavaIndictment[Score_]'):
        self._delegate = delegate

    @property
    def score(self) -> Score_:
        return self._delegate.getScore()

    @property
    def constraint_match_count(self) -> int:
        return self._delegate.getConstraintMatchCount()

    @property
    def constraint_match_set(self) -> set[ConstraintMatch[Score_]]:
        return _map_constraint_match_set(self._delegate.getConstraintMatchSet())

    @property
    def indicted_object(self) -> Any:
        return unwrap_python_like_object(self._delegate.getIndictedObject())

    def get_justification_list(self, justification_type: Type[Justification_] = None) -> list[Justification_]:
        if justification_type is None:
            justification_list = self._delegate.getJustificationList()
        else:
            justification_list = self._delegate.getJustificationList(get_class(justification_type))

        return _unwrap_justification_list(justification_list)


class ScoreExplanation(Generic[Solution_]):
    _delegate: '_JavaScoreExplanation'

    def __init__(self, delegate: '_JavaScoreExplanation'):
        self._delegate = delegate

    @property
    def constraint_match_total_map(self) -> dict[str, ConstraintMatchTotal]:
        return {
            e.getKey(): ConstraintMatchTotal(
                constraint_ref=ConstraintRef(package_name=e.getValue().getConstraintRef().packageName(),
                                             constraint_name=e.getValue().getConstraintRef().constraintName()),
                constraint_match_count=e.getValue().getConstraintMatchCount(),
                constraint_match_set=_map_constraint_match_set(e.getValue().getConstraintMatchSet()),
                constraint_weight=e.getValue().getConstraintWeight(),
                score=e.getValue().getScore()
            )
            for e in cast(set['_JavaMap.Entry[str, _JavaConstraintMatchTotal]'],
                          self._delegate.getConstraintMatchTotalMap().entrySet())
        }

    @property
    def indictment_map(self) -> dict[Any, Indictment]:
        return {
            unwrap_python_like_object(e.getKey()): Indictment(e.getValue())
            for e in cast(set['_JavaMap.Entry'], self._delegate.getIndictmentMap().entrySet())
        }

    @property
    def score(self) -> 'Score':
        return self._delegate.getScore()

    @property
    def solution(self) -> Solution_:
        from jpyinterpreter import unwrap_python_like_object
        return unwrap_python_like_object(self._delegate.getSolution())

    @property
    def summary(self) -> str:
        return self._delegate.getSummary()

    def get_justification_list(self, justification_type: Type[Justification_] = None) -> list[Justification_]:
        if justification_type is None:
            justification_list = self._delegate.getJustificationList()
        else:
            justification_list = self._delegate.getJustificationList(get_class(justification_type))

        return _unwrap_justification_list(justification_list)


class MatchAnalysis(Generic[Score_]):
    _delegate: '_JavaMatchAnalysis'

    def __init__(self, delegate: '_JavaMatchAnalysis'):
        self._delegate = delegate

    @property
    def constraint_ref(self) -> ConstraintRef:
        return ConstraintRef(package_name=self._delegate.constraintRef().packageName(),
                             constraint_name=self._delegate.constraintRef().constraintName())

    @property
    def score(self) -> Score_:
        return self._delegate.score()

    @property
    def justification(self) -> ConstraintJustification:
        return _unwrap_justification(self._delegate.justification())


class ConstraintAnalysis(Generic[Score_]):
    _delegate: '_JavaConstraintAnalysis[Score_]'

    def __init__(self, delegate: '_JavaConstraintAnalysis[Score_]'):
        self._delegate = delegate
        delegate.constraintRef()

    @property
    def constraint_ref(self) -> ConstraintRef:
        return ConstraintRef(package_name=self._delegate.constraintRef().packageName(),
                             constraint_name=self._delegate.constraintRef().constraintName())

    @property
    def constraint_package(self) -> str:
        return self._delegate.constraintPackage()

    @property
    def constraint_name(self) -> str:
        return self._delegate.constraintName()

    @property
    def weight(self) -> Optional[Score_]:
        return self._delegate.weight()

    @property
    def matches(self) -> list[MatchAnalysis[Score_]]:
        return [MatchAnalysis(match_analysis)
                for match_analysis in cast(list['_JavaMatchAnalysis[Score_]'], self._delegate.matches())]

    @property
    def score(self) -> Score_:
        return self._delegate.score()


class ScoreAnalysis:
    _delegate: '_JavaScoreAnalysis'

    def __init__(self, delegate: '_JavaScoreAnalysis'):
        self._delegate = delegate

    @property
    def score(self) -> 'Score':
        return self._delegate.score()

    @property
    def constraint_map(self) -> dict[ConstraintRef, ConstraintAnalysis]:
        return {
            ConstraintRef(package_name=e.getKey().packageName(),
                          constraint_name=e.getKey().constraintName())
            : ConstraintAnalysis(e.getValue())
            for e in cast(set['_JavaMap.Entry[_JavaConstraintRef, _JavaConstraintAnalysis]'],
                          self._delegate.constraintMap().entrySet())
        }

    @property
    def constraint_analyses(self) -> list[ConstraintAnalysis]:
        return [
            ConstraintAnalysis(analysis) for analysis in cast(
                list['_JavaConstraintAnalysis[Score]'], self._delegate.constraintAnalyses())
        ]


__all__ = ['ScoreExplanation',
           'ConstraintRef', 'ConstraintMatch', 'ConstraintMatchTotal',
           'ConstraintJustification', 'DefaultConstraintJustification', 'Indictment',
           'ScoreAnalysis', 'ConstraintAnalysis', 'MatchAnalysis']
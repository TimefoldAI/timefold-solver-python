"""
Classes and decorators used to define constraints.

Examples
--------
>>> from timefold.solver.score import ConstraintFactory, Constraint, Joiners, HardSoftScore, constraint_provider
>>> from domain import Lesson
>>>
>>> @constraint_provider
... def timetabling_constraints(cf: ConstraintFactory) -> list[Constraint]:
...     return [
...         cf.for_each_unique_pair(Lesson,
...                                 Joiners.equal(lambda lesson: lesson.teacher),
...                                 Joiners.equal(lambda lesson: lesson.timeslot))
...           .penalize(HardSoftScore.ONE_HARD)
...           .as_constraint('Overlapping Timeslots')
...     ]
"""
from ._annotations import *
from ._constraint_builder import *
from ._constraint_factory import *
from ._constraint_stream import *
from ._function_translator import *
from ._group_by import *
from ._incremental_score_calculator import *
from ._joiners import *
from ._score_analysis import *
from ._score_director import *

from typing import TYPE_CHECKING as _TYPE_CHECKING

if _TYPE_CHECKING:
    class Score:
        """
        A Score is result of the score function (AKA fitness function) on a single possible solution.
        Implementations must be immutable.

        Attributes
        ----------
        init_score : int
            The init score is the negative of the number of uninitialized genuine planning variables.
            If it's 0 (which it usually is),
            the `planning_solution` is fully initialized and the score's str does not mention it.
            For comparisons, it's even more important than the hard score:
            if you don't want this behaviour, read about overconstrained planning in the reference manual.

        is_feasible : bool
            A `planning_solution` is feasible if it has no broken hard constraints and `is_solution_initialized` is
            true. `SimpleScore` are always feasible, if their `init_score` is 0.

        is_solution_initialized : bool
            Checks if the `planning_solution` of this score was fully initialized when it was calculated.
            True if `init_score` is 0.

        See Also
        --------
        HardSoftScore
        """
        init_score: int
        is_feasible: bool
        is_solution_initialized: bool
        ...

    class SimpleScore(Score):
        """
        This Score is based on one level of `int` constraints.
        This class is immutable.

        Attributes
        ----------
        score : int
            The total of the broken negative constraints and fulfilled positive constraints.
            Their weight is included in the total.
            The score is usually a negative number because most use cases only have negative constraints.
        """
        ZERO: 'SimpleScore' = None
        ONE: 'SimpleScore' = None
        score: int

        @staticmethod
        def of(score: int, /) -> 'SimpleScore':
            ...

    class HardSoftScore(Score):
        """
        This Score is based on two levels of int constraints: hard and soft.
        Hard constraints have priority over soft constraints.
        Hard constraints determine feasibility.

        This class is immutable.

        Attributes
        ----------
        hard_score : int
           The total of the broken negative hard constraints and fulfilled positive hard constraints.
           Their weight is included in the total.
           The hard score is usually a negative number because most use cases only have negative constraints.

        soft_score : int
            The total of the broken negative soft constraints and fulfilled positive soft constraints.
            Their weight is included in the total.
            The soft score is usually a negative number because most use cases only have negative constraints.

            In a normal score comparison, the soft score is irrelevant if the two scores don't have the same hard score.
        """
        ZERO: 'HardSoftScore' = None
        ONE_HARD: 'HardSoftScore' = None
        ONE_SOFT: 'HardSoftScore' = None
        hard_score: int
        soft_score: int

        @staticmethod
        def of(hard_score: int, soft_score: int, /) -> 'HardSoftScore':
            ...


    class HardMediumSoftScore(Score):
        """
        This Score is based on three levels of int constraints: hard, medium and soft.
        Hard constraints have priority over medium constraints.
        Medium constraints have priority over soft constraints.
        Hard constraints determine feasibility.

        This class is immutable.

        Attributes
        ----------
        hard_score : int
            The total of the broken negative hard constraints and fulfilled positive hard constraints.
            Their weight is included in the total.
            The hard score is usually a negative number because most use cases only have negative constraints.

        medium_score : int
            The total of the broken negative medium constraints and fulfilled positive medium constraints.
            Their weight is included in the total.
            The medium score is usually a negative number because most use cases only have negative constraints.

            In a normal score comparison,
            the medium score is irrelevant if the two scores don't have the same hard score.

        soft_score : int
            The total of the broken negative soft constraints and fulfilled positive soft constraints.
            Their weight is included in the total.
            The soft score is usually a negative number because most use cases only have negative constraints.

            In a normal score comparison,
            the soft score is irrelevant if the two scores don't have the same hard and medium score.
        """
        ZERO: 'HardMediumSoftScore' = None
        ONE_HARD: 'HardMediumSoftScore' = None
        ONE_MEDIUM: 'HardMediumSoftScore' = None
        ONE_SOFT: 'HardMediumSoftScore' = None
        hard_score: int
        medium_score: int
        soft_score: int

        @staticmethod
        def of(self, hard_score: int, medium_score: int, soft_score: int, /) -> 'HardMediumSoftScore':
            ...

    class BendableScore(Score):
        """
        This Score is based on n levels of int constraints.
        The number of levels is bendable at configuration time.

        This class is immutable.

        Attributes
        ----------
        hard_scores : list[int]
            A list of hard scores, with earlier hard scores having higher priority than later ones.

        soft_scores : list[int]
            A list of soft scores, with earlier soft scores having higher priority than later ones
        """
        hard_scores: list[int]
        soft_scores: list[int]

        @staticmethod
        def of(hard_scores: list[int], soft_scores: list[int], /) -> 'BendableScore':
            ...


def __getattr__(name):
    from ._score import lookup_score_class
    return lookup_score_class(name)


if not _TYPE_CHECKING:
    exported = [name for name in globals().keys() if not name.startswith('_')]
    exported += ['Score', 'SimpleScore', 'HardSoftScore', 'HardMediumSoftScore', 'BendableScore']
    __all__ = exported

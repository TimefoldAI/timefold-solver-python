from ._annotations import *
from ._constraint_builder import *
from ._constraint_factory import *
from ._constraint_match_total import *
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
        ...

    class SimpleScore(Score):
        ZERO: 'SimpleScore' = None
        ONE: 'SimpleScore' = None
        init_score: int
        is_feasible: bool
        score: int

        @staticmethod
        def of(score: int, /) -> 'SimpleScore':
            ...

    class HardSoftScore(Score):
        ZERO: 'HardSoftScore' = None
        ONE_HARD: 'HardSoftScore' = None
        ONE_SOFT: 'HardSoftScore' = None
        init_score: int
        is_feasible: bool
        hard_score: int
        soft_score: int

        @staticmethod
        def of(hard_score: int, soft_score: int, /) -> 'HardSoftScore':
            ...


    class HardMediumSoftScore(Score):
        ZERO: 'HardMediumSoftScore' = None
        ONE_HARD: 'HardMediumSoftScore' = None
        ONE_MEDIUM: 'HardMediumSoftScore' = None
        ONE_SOFT: 'HardMediumSoftScore' = None
        init_score: int
        is_feasible: bool
        hard_score: int
        medium_score: int
        soft_score: int

        @staticmethod
        def of(self, hard_score: int, medium_score: int, soft_score: int, /) -> 'HardMediumSoftScore':
            ...

    class BendableScore(Score):
        init_score: int
        is_feasible: bool
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

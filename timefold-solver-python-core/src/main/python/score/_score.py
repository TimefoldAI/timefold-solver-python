from abc import ABC, abstractmethod
from typing import ClassVar
from dataclasses import dataclass, field
from jpype import JArray, JInt
from .._timefold_java_interop import _java_score_mapping_dict


@dataclass(unsafe_hash=True)
class Score(ABC):
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
    init_score: int = field(default=0, kw_only=True, compare=True)

    @property
    @abstractmethod
    def is_feasible(self) -> bool:
        ...

    @abstractmethod
    def _to_java_score(self) -> object:
        ...

    @property
    def is_solution_initialized(self) -> bool:
        return self.init_score == 0


@dataclass(unsafe_hash=True, order=True)
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
    ZERO: ClassVar['SimpleScore']
    ONE: ClassVar['SimpleScore']

    score: int = field(compare=True)

    @property
    def is_feasible(self) -> bool:
        return self.is_solution_initialized

    @staticmethod
    def of(score: int) -> 'SimpleScore':
        return SimpleScore(score, init_score=0)

    @staticmethod
    def parse(score_text: str) -> 'SimpleScore':
        if 'init' in score_text:
            init, score = score_text.split('/')
        else:
            init = '0init'
            score = score_text

        return SimpleScore(int(score), init_score=int(init.rstrip('init')))

    def _to_java_score(self):
        if self.init_score < 0:
            return _java_score_mapping_dict['SimpleScore'].ofUninitialized(self.init_score, self.score)
        else:
            return _java_score_mapping_dict['SimpleScore'].of(self.score)

    def __str__(self):
        return (f'{self.score}' if self.is_solution_initialized else
                f'{self.init_score}init/{self.score}')


SimpleScore.ZERO = SimpleScore.of(0)
SimpleScore.ONE = SimpleScore.of(1)


@dataclass(unsafe_hash=True, order=True)
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
    ZERO: ClassVar['HardSoftScore']
    ONE_HARD: ClassVar['HardSoftScore']
    ONE_SOFT: ClassVar['HardSoftScore']

    hard_score: int = field(compare=True)
    soft_score: int = field(compare=True)

    @property
    def is_feasible(self) -> bool:
        return self.is_solution_initialized and self.hard_score >= 0

    @staticmethod
    def of(hard_score: int, soft_score: int) -> 'HardSoftScore':
        return HardSoftScore(hard_score, soft_score, init_score=0)

    @staticmethod
    def parse(score_text: str) -> 'HardSoftScore':
        if 'init' in score_text:
            init, hard, soft = score_text.split('/')
        else:
            init = '0init'
            hard, soft = score_text.split('/')

        return HardSoftScore(int(hard.rstrip('hard')), int(soft.rstrip('soft')),
                             init_score=int(init.rstrip('init')))

    def _to_java_score(self):
        if self.init_score < 0:
            return _java_score_mapping_dict['HardSoftScore'].ofUninitialized(self.init_score, self.hard_score, self.soft_score)
        else:
            return _java_score_mapping_dict['HardSoftScore'].of(self.hard_score, self.soft_score)

    def __str__(self):
        return (f'{self.hard_score}hard/{self.soft_score}soft' if self.is_solution_initialized else
                f'{self.init_score}init/{self.hard_score}hard/{self.soft_score}soft')


HardSoftScore.ZERO = HardSoftScore.of(0, 0)
HardSoftScore.ONE_HARD = HardSoftScore.of(1, 0)
HardSoftScore.ONE_SOFT = HardSoftScore.of(0, 1)


@dataclass(unsafe_hash=True, order=True)
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
    ZERO: ClassVar['HardMediumSoftScore']
    ONE_HARD: ClassVar['HardMediumSoftScore']
    ONE_MEDIUM: ClassVar['HardMediumSoftScore']
    ONE_SOFT: ClassVar['HardMediumSoftScore']

    hard_score: int = field(compare=True)
    medium_score: int = field(compare=True)
    soft_score: int = field(compare=True)

    @property
    def is_feasible(self) -> bool:
        return self.is_solution_initialized and self.hard_score >= 0

    @staticmethod
    def of(hard_score: int, medium_score: int, soft_score: int) -> 'HardMediumSoftScore':
        return HardMediumSoftScore(hard_score, medium_score, soft_score, init_score=0)

    @staticmethod
    def parse(score_text: str) -> 'HardMediumSoftScore':
        if 'init' in score_text:
            init, hard, medium, soft = score_text.split('/')
        else:
            init = '0init'
            hard, medium, soft = score_text.split('/')

        return HardMediumSoftScore(int(hard.rstrip('hard')), int(medium.rstrip('medium')),
                                   int(soft.rstrip('soft')), init_score=int(init.rstrip('init')))

    def _to_java_score(self):
        if self.init_score < 0:
            return _java_score_mapping_dict['HardMediumSoftScore'].ofUninitialized(self.init_score, self.hard_score,
                                                                                   self.medium_score, self.soft_score)
        else:
            return _java_score_mapping_dict['HardMediumSoftScore'].of(self.hard_score, self.medium_score, self.soft_score)

    def __str__(self):
        return (f'{self.hard_score}hard/{self.medium_score}medium/{self.soft_score}soft'
                if self.is_solution_initialized else
                f'{self.init_score}init/{self.hard_score}hard/{self.medium_score}medium/{self.soft_score}soft')


HardMediumSoftScore.ZERO = HardMediumSoftScore.of(0, 0, 0)
HardMediumSoftScore.ONE_HARD = HardMediumSoftScore.of(1, 0, 0)
HardMediumSoftScore.ONE_MEDIUM = HardMediumSoftScore.of(0, 1, 0)
HardMediumSoftScore.ONE_SOFT = HardMediumSoftScore.of(0, 0, 1)


@dataclass(unsafe_hash=True, order=True)
class BendableScore(Score):
    """
    This Score is based on n levels of int constraints.
    The number of levels is bendable at configuration time.

    This class is immutable.

    Attributes
    ----------
    hard_scores : tuple[int, ...]
        A tuple of hard scores, with earlier hard scores having higher priority than later ones.

    soft_scores : tuple[int, ...]
        A tuple of soft scores, with earlier soft scores having higher priority than later ones
    """
    hard_scores: tuple[int, ...] = field(compare=True)
    soft_scores: tuple[int, ...] = field(compare=True)

    @property
    def is_feasible(self) -> bool:
        return self.is_solution_initialized and all(score >= 0 for score in self.hard_scores)

    @staticmethod
    def of(hard_scores: tuple[int, ...], soft_scores: tuple[int, ...]) -> 'BendableScore':
        return BendableScore(hard_scores, soft_scores, init_score=0)

    @staticmethod
    def parse(score_text: str) -> 'BendableScore':
        if 'init' in score_text:
            init, hard_score_text, soft_score_text = score_text.split('/[')
        else:
            hard_score_text, soft_score_text = score_text.split('/[')
            # Remove leading [ from hard score text,
            # since there is no init score in the text
            # (and thus the split will not consume it)
            hard_score_text = hard_score_text[1:]
            init = '0init'

        hard_scores = tuple([int(score) for score in hard_score_text[:hard_score_text.index(']')].split('/')])
        soft_scores = tuple([int(score) for score in soft_score_text[:soft_score_text.index(']')].split('/')])
        return BendableScore(hard_scores, soft_scores, init_score=int(init.rstrip('init')))

    def _to_java_score(self):
        IntArrayCls = JArray(JInt)
        hard_scores = IntArrayCls(self.hard_scores)
        soft_scores = IntArrayCls(self.soft_scores)
        if self.init_score < 0:
            return _java_score_mapping_dict['BendableScore'].ofUninitialized(self.init_score, hard_scores, soft_scores)
        else:
            return _java_score_mapping_dict['BendableScore'].of(hard_scores, soft_scores)

    def __str__(self):
        hard_text = f'{str(list(self.hard_scores)).replace(", ", "/")}hard'
        soft_text = f'{str(list(self.soft_scores)).replace(", ", "/")}soft'
        return (f'{hard_text}/{soft_text}' if self.is_solution_initialized else
                f'{self.init_score}init/{hard_text}/{soft_text}')


# Import score conversions here to register conversions (circular import)
from ._score_conversions import *

__all__ = ['Score', 'SimpleScore', 'HardSoftScore', 'HardMediumSoftScore', 'BendableScore']

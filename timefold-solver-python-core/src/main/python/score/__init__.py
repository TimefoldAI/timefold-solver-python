from .._timefold_java_interop import ensure_init
from typing import TYPE_CHECKING
from jpype import JImplementationFor, JOverride
import jpype.imports # noqa

if TYPE_CHECKING:
    from ai.timefold.solver.core.api.score import Score

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


@JImplementationFor('ai.timefold.solver.core.api.score.buildin.simple.SimpleScore')
class _SimpleScoreImpl:
    @property
    def init_score(self) -> int:
        return self.initScore()

    @property
    def is_feasible(self) -> bool:
        return self.isFeasible()

    @property
    def score(self):
        return self.toLevelNumbers()[0]  # noqa


@JImplementationFor('ai.timefold.solver.core.api.score.buildin.hardsoft.HardSoftScore')
class _HardSoftScoreImpl:
    @property
    def init_score(self) -> int:
        return self.initScore()

    @property
    def is_feasible(self) -> bool:
        return self.isFeasible()

    @property
    def hard_score(self):
        return self.hardScore()  # noqa

    @property
    def soft_score(self):
        return self.softScore()  # noqa


@JImplementationFor('ai.timefold.solver.core.api.score.buildin.hardmediumsoft.'
                    'HardMediumSoftScore')
class _HardMediumSoftScoreImpl:
    @property
    def init_score(self) -> int:
        return self.initScore()

    @property
    def is_feasible(self) -> bool:
        return self.isFeasible()

    @property
    def hard_score(self):
        return self.hardScore()  # noqa

    @property
    def medium_score(self):
        return self.mediumScore()  # noqa

    @property
    def soft_score(self):
        return self.softScore()  # noqa


@JImplementationFor('ai.timefold.solver.core.api.score.buildin.bendable.BendableScore')
class _BendableScoreImpl:
    @property
    def init_score(self) -> int:
        return self.initScore()

    @property
    def is_feasible(self) -> bool:
        return self.isFeasible()

    @property
    def hard_scores(self):
        return self.hardScores()  # noqa

    @property
    def soft_scores(self):
        return self.softScores()  # noqa


def __getattr__(name: str):
    ensure_init()
    import jpype.imports
    from ai.timefold.solver.core.api.score import Score
    from ai.timefold.solver.core.api.score.buildin.simple import SimpleScore
    from ai.timefold.solver.core.api.score.buildin.hardsoft import HardSoftScore
    from ai.timefold.solver.core.api.score.buildin.hardmediumsoft import HardMediumSoftScore
    from ai.timefold.solver.core.api.score.buildin.bendable import BendableScore
    match name:
        case 'Score':
            return Score
        case 'SimpleScore':
            return SimpleScore
        case 'HardSoftScore':
            return HardSoftScore
        case 'HardMediumSoftScore':
            return HardMediumSoftScore
        case 'BendableScore':
            return BendableScore
        case _:
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ['Score', 'SimpleScore', 'HardSoftScore', 'HardMediumSoftScore', 'BendableScore']

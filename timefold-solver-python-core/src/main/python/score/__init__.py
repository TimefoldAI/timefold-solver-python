from .._timefold_java_interop import ensure_init
from typing import TYPE_CHECKING, List
from jpype import JImplementationFor
import jpype.imports # noqa

if TYPE_CHECKING:
    from ai.timefold.solver.core.api.score import Score

    class SimpleScore(Score):
        ZERO: 'SimpleScore' = None
        ONE: 'SimpleScore' = None

        def score(self) -> int:
            ...

    class HardSoftScore(Score):
        ZERO: 'HardSoftScore' = None
        ONE_HARD: 'HardSoftScore' = None
        ONE_SOFT: 'HardSoftScore' = None

        def hard_score(self) -> int:
            ...

        def soft_score(self) -> int:
            ...

    class HardMediumSoftScore(Score):
        ZERO: 'HardMediumSoftScore' = None
        ONE_HARD: 'HardMediumSoftScore' = None
        ONE_MEDIUM: 'HardMediumSoftScore' = None
        ONE_SOFT: 'HardMediumSoftScore' = None

        def hard_score(self) -> int:
            ...

        def medium_score(self) -> int:
            ...

        def soft_score(self) -> int:
            ...

    class BendableScore(Score):
        def hard_scores(self) -> List[int]:
            ...

        def soft_scores(self) -> List[int]:
            ...


@JImplementationFor('ai.timefold.solver.core.api.score.buildin.hardsoft.HardSoftScore')
class _HardSoftScoreImpl:
    def hard_score(self):
        return self.hardScore()  # noqa

    def soft_score(self):
        return self.softScore()  # noqa


@JImplementationFor('ai.timefold.solver.core.api.score.buildin.hardmediumsoft.'
                    'HardMediumSoftScore')
class _HardMediumSoftScoreImpl:
    def hard_score(self):
        return self.hardScore()  # noqa

    def medium_score(self):
        return self.mediumScore()  # noqa

    def soft_score(self):
        return self.softScore()  # noqa


@JImplementationFor('ai.timefold.solver.core.api.score.buildin.bendable.BendableScore')
class _BendableScoreImpl:
    def hard_scores(self):
        return self.hardScores()  # noqa

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

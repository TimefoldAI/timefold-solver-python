from ..timefold_java_interop import ensure_init
from typing import TYPE_CHECKING, List
from jpype import JImplementationFor, JOverride
import jpype.imports # noqa

if TYPE_CHECKING:
    class Score:
        pass

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

else:
    ensure_init()
    from ai.timefold.solver.core.api.score.buildin.simple import SimpleScore
    from ai.timefold.solver.core.api.score.buildin.hardsoft import HardSoftScore
    from ai.timefold.solver.core.api.score.buildin.hardmediumsoft import HardMediumSoftScore
    from ai.timefold.solver.core.api.score.buildin.bendable import BendableScore

    @JImplementationFor(HardSoftScore.class_.getName())
    class _HardSoftScoreImpl:
        def hard_score(self):
            return self.hardScore()  # noqa

        def soft_score(self):
            return self.softScore()  # noqa

    @JImplementationFor(HardMediumSoftScore.class_.getName())
    class _HardMediumSoftScoreImpl:
        def hard_score(self):
            return self.hardScore()  # noqa

        def medium_score(self):
            return self.mediumScore()  # noqa

        def soft_score(self):
            return self.softScore()  # noqa

    @JImplementationFor(BendableScore.class_.getName())
    class _BendableScoreImpl:
        def hard_scores(self):
            return self.hardScores()  # noqa

        def soft_scores(self):
            return self.softScores()  # noqa

__all__ = ['Score', 'SimpleScore', 'HardSoftScore', 'HardMediumSoftScore', 'BendableScore']

from typing import TYPE_CHECKING
from jpype import JImplements, JOverride

if TYPE_CHECKING:
    from ai.timefold.solver.core.api.score.constraint import ConstraintRef, ConstraintMatch, ConstraintMatchTotal
    from ai.timefold.solver.core.api.score import Score as _Score


# Cannot import DefaultConstraintMatchTotal as it is in impl
@JImplements('ai.timefold.solver.core.api.score.constraint.ConstraintMatchTotal', deferred=True)
class DefaultConstraintMatchTotal:
    """
    A default implementation of ConstraintMatchTotal that can be used in a constraint match aware
    @incremental_score_calculator.
    """
    def __init__(self, constraint_package: str, constraint_name: str, constraint_weight: '_Score' = None):
        from ai.timefold.solver.core.api.score.constraint import ConstraintMatchTotal
        from java.util import LinkedHashSet
        self.constraint_package = constraint_package
        self.constraint_name = constraint_name
        self.constraint_id = ConstraintMatchTotal.composeConstraintId(constraint_package, constraint_name)
        self.constraint_weight = constraint_weight
        self.constraint_match_set = LinkedHashSet()
        if constraint_weight is not None:
            self.score = constraint_weight.zero()
        else:
            self.score = None

    @JOverride
    def getConstraintPackage(self):
        return self.constraint_package

    @JOverride
    def getConstraintName(self):
        return self.constraint_name

    @JOverride
    def getConstraintRef(self):
        return ConstraintRef.of(self.constraint_package, self.constraint_name)

    @JOverride
    def getConstraintWeight(self):
        return self.constraint_weight

    @JOverride
    def getConstraintMatchSet(self):
        return self.constraint_match_set

    @JOverride
    def getScore(self):
        return self.score

    @JOverride
    def getConstraintId(self):
        return self.constraint_id

    @JOverride
    def compareTo(self, other: 'DefaultConstraintMatchTotal'):
        if self.constraint_id == other.constraint_id:
            return 0
        elif self.constraint_id < other.constraint_id:
            return -1
        else:
            return 1

    def __lt__(self, other):
        return self.constraint_id < other.constraint_id

    def __gt__(self, other):
        return self.constraint_id > other.constraint_id

    @JOverride
    def equals(self, other):
        if self is other:
            return True
        elif isinstance(other, DefaultConstraintMatchTotal):
            return self.constraint_id == other.constraint_id
        else:
            return False

    def __eq__(self, other):
        return self.constraint_id == other.constraint_id

    @JOverride
    def hashCode(self):
        return hash(self.constraint_id)

    def __hash__(self):
        return hash(self.constraint_id)

    @JOverride
    def toString(self):
        return f'{self.constraint_id}={self.score}'

    def addConstraintMatch(self, justification_list: list, score: '_Score') -> 'ConstraintMatch':
        from ai.timefold.solver.core.api.score.constraint import ConstraintMatch
        from java.util import Arrays
        self.score = self.score.add(score) if self.score is not None else score
        wrapped_justification_list = Arrays.asList(justification_list)
        constraint_match = ConstraintMatch(self.constraint_package, self.constraint_name, wrapped_justification_list,
                                           score)
        self.constraint_match_set.add(constraint_match)
        return constraint_match

    def removeConstraintMatch(self, constraint_match: 'ConstraintMatch'):
        self.score = self.score.subtract(constraint_match.getScore())
        removed = self.constraint_match_set.remove(constraint_match)
        if not removed:
            raise ValueError(f'The ConstraintMatchTotal ({self}) could not remove the ConstraintMatch'
                             f'({constraint_match}) from its constraint_match_set ({self.constraint_match_set}).')


__all__ = ['DefaultConstraintMatchTotal']

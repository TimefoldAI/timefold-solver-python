from ._score_director import ScoreDirector
from jpyinterpreter import add_java_interface
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from ai.timefold.solver.core.api.domain.variable import VariableListener

Solution_ = TypeVar('Solution_')
Entity_ = TypeVar('Entity_')


@add_java_interface('ai.timefold.solver.core.api.domain.variable.VariableListener')
class VariableListener:
    def after_entity_added(self, score_director: ScoreDirector, entity) -> None:
        pass

    def after_entity_removed(self, score_director: ScoreDirector, entity) -> None:
        pass

    def before_entity_added(self, score_director: ScoreDirector, entity) -> None:
        pass

    def before_entity_removed(self, score_director: ScoreDirector, entity) -> None:
        pass

    def close(self) -> None:
        pass

    def reset_working_solution(self, score_director: ScoreDirector) -> None:
        pass

    def after_variable_changed(self, score_director: ScoreDirector, entity) -> None:
        pass

    def before_variable_changed(self, score_director: ScoreDirector, entity) -> None:
        pass

    def requires_unique_entity_events(self) -> bool:
        return False


if not TYPE_CHECKING:  # We do not want these methods to appear in the API
    def afterEntityAdded(self, java_score_director, entity) -> None:
        score_director = ScoreDirector(java_score_director)
        self.after_entity_added(score_director, entity)

    VariableListener.afterEntityAdded = afterEntityAdded

    def afterEntityRemoved(self, java_score_director, entity) -> None:
        score_director = ScoreDirector(java_score_director)
        self.after_entity_removed(score_director, entity)

    VariableListener.afterEntityRemoved = afterEntityRemoved

    def beforeEntityAdded(self, java_score_director, entity) -> None:
        score_director = ScoreDirector(java_score_director)
        self.before_entity_added(score_director, entity)

    VariableListener.beforeEntityAdded = beforeEntityAdded

    def beforeEntityRemoved(self, java_score_director, entity) -> None:
        score_director = ScoreDirector(java_score_director)
        self.before_entity_removed(score_director, entity)

    VariableListener.beforeEntityRemoved = beforeEntityRemoved

    def resetWorkingSolution(self, java_score_director) -> None:
        score_director = ScoreDirector(java_score_director)
        self.reset_working_solution(score_director)

    VariableListener.resetWorkingSolution = resetWorkingSolution

    def afterVariableChanged(self, java_score_director, entity) -> None:
        score_director = ScoreDirector(java_score_director)
        self.after_variable_changed(score_director, entity)

    VariableListener.afterVariableChanged = afterVariableChanged

    def beforeVariableChanged(self, java_score_director, entity) -> None:
        score_director = ScoreDirector(java_score_director)
        self.before_variable_changed(score_director, entity)

    VariableListener.beforeVariableChanged = beforeVariableChanged

    def requiresUniqueEntityEvents(self) -> bool:
        return self.requires_unique_entity_events()

    VariableListener.requiresUniqueEntityEvents = requiresUniqueEntityEvents


__all__ = ['VariableListener']

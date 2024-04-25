from jpyinterpreter import add_java_interface
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


@add_java_interface('ai.timefold.solver.core.api.score.calculator.IncrementalScoreCalculator')
class IncrementalScoreCalculator(ABC):
    @abstractmethod
    def after_entity_added(self, entity) -> None:
        ...

    @abstractmethod
    def after_entity_removed(self, entity) -> None:
        ...

    def after_list_variable_changed(self, entity, variable_name: str, start: int, end: int) -> None:
        ...

    def after_list_variable_element_assigned(self, variable_name: str, element) -> None:
        ...

    def after_list_variable_element_unassigned(self, variable_name: str, element) -> None:
        ...

    @abstractmethod
    def after_variable_changed(self, entity, variable_name: str) -> None:
        ...

    @abstractmethod
    def before_entity_added(self, entity) -> None:
        ...

    @abstractmethod
    def before_entity_removed(self, entity) -> None:
        ...

    def before_list_variable_changed(self, entity, variable_name: str, start: int, end: int) -> None:
        ...

    def before_list_variable_element_assigned(self, variable_name: str, element) -> None:
        ...

    def before_list_variable_element_unassigned(self, variable_name: str, element) -> None:
        ...

    @abstractmethod
    def before_variable_changed(self, entity, variable_name: str) -> None:
        ...

    @abstractmethod
    def calculate_score(self):
        ...

    @abstractmethod
    def reset_working_solution(self, solution) -> None:
        ...


@add_java_interface('ai.timefold.solver.core.api.score.calculator.ConstraintMatchAwareIncrementalScoreCalculator')
class ConstraintMatchAwareIncrementalScoreCalculator(IncrementalScoreCalculator):
    @abstractmethod
    def get_constraint_match_totals(self) -> list:
        ...

    @abstractmethod
    def get_indictment_map(self) -> dict:
        ...

    @abstractmethod
    def reset_working_solution(self, solution, constraint_match_enabled=False) -> None:
        ...


if not TYPE_CHECKING:
    # Use type(self).method(self, ...)
    # Since if the arguments are typed, they might have different signatures and
    # thus not override one another, meaning the generated interface method will
    # call the original method and not the "overridden" one!
    def afterEntityAdded(self, entity) -> None:
        type(self).after_entity_added(self, entity)

    IncrementalScoreCalculator.afterEntityAdded = afterEntityAdded

    def afterEntityRemoved(self, entity) -> None:
        type(self).after_entity_removed(self, entity)

    IncrementalScoreCalculator.afterEntityRemoved = afterEntityRemoved

    def afterListVariableChanged(self, entity, variable_name, start, end) -> None:
        type(self).after_list_variable_changed(self, entity, variable_name, start, end)

    IncrementalScoreCalculator.afterListVariableChanged = afterListVariableChanged

    def afterListVariableElementAssigned(self, variable_name, element) -> None:
        type(self).after_list_variable_element_assigned(self, variable_name, element)

    IncrementalScoreCalculator.afterListVariableElementAssigned = afterListVariableElementAssigned

    def afterListVariableElementUnassigned(self, variable_name, element) -> None:
        type(self).after_list_variable_element_unassigned(self, variable_name, element)

    IncrementalScoreCalculator.afterListVariableElementUnassigned = afterListVariableElementUnassigned

    def afterVariableChanged(self, entity, variable_name) -> None:
        type(self).after_variable_changed(self, entity, variable_name)

    IncrementalScoreCalculator.afterVariableChanged = afterVariableChanged

    def beforeEntityAdded(self, entity) -> None:
        type(self).before_entity_added(self, entity)

    IncrementalScoreCalculator.beforeEntityAdded = beforeEntityAdded

    def beforeEntityRemoved(self, entity) -> None:
        type(self).before_entity_removed(self, entity)

    IncrementalScoreCalculator.beforeEntityRemoved = beforeEntityRemoved

    def beforeListVariableChanged(self, entity, variable_name, start, end) -> None:
        type(self).before_list_variable_changed(self, entity, variable_name, start, end)

    IncrementalScoreCalculator.beforeListVariableChanged = beforeListVariableChanged

    def beforeListVariableElementAssigned(self, variable_name, element) -> None:
        type(self).before_list_variable_element_assigned(self, variable_name, element)

    IncrementalScoreCalculator.beforeListVariableElementAssigned = beforeListVariableElementAssigned

    def beforeListVariableElementUnassigned(self, variable_name, element) -> None:
        type(self).before_list_variable_element_unassigned(self, variable_name, element)

    IncrementalScoreCalculator.beforeListVariableElementUnassigned = beforeListVariableElementUnassigned

    def beforeVariableChanged(self, entity, variable_name) -> None:
        type(self).before_variable_changed(self, entity, variable_name)

    IncrementalScoreCalculator.beforeVariableChanged = beforeVariableChanged

    def calculateScore(self):
        return type(self).calculate_score(self)

    IncrementalScoreCalculator.calculateScore = calculateScore

    def resetWorkingSolution(self, solution) -> None:
        type(self).reset_working_solution(self, solution)

    IncrementalScoreCalculator.resetWorkingSolution = resetWorkingSolution

    def getConstraintMatchTotals(self) -> list:
        return type(self).get_constraint_match_totals(self)

    ConstraintMatchAwareIncrementalScoreCalculator.getConstraintMatchTotals = getConstraintMatchTotals

    def getIndictmentMap(self) -> dict:
        return type(self).get_indictment_map(self)

    ConstraintMatchAwareIncrementalScoreCalculator.getIndictmentMap = getIndictmentMap

    def resetWorkingSolution(self, solution, constraint_match_enabled=False) -> None:
        type(self).reset_working_solution(self, solution, constraint_match_enabled)

    ConstraintMatchAwareIncrementalScoreCalculator.resetWorkingSolution = resetWorkingSolution

__all__ = ['IncrementalScoreCalculator', 'ConstraintMatchAwareIncrementalScoreCalculator']

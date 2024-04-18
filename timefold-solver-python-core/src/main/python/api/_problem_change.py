from .._timefold_java_interop import get_class

from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Callable, TYPE_CHECKING, Generic
from types import FunctionType
from jpyinterpreter import (convert_to_java_python_like_object,
                            unwrap_python_like_object,
                            update_python_object_from_java,
                            translate_python_bytecode_to_java_bytecode)
from jpype import JOverride, JImplements
from traceback import print_exc

if TYPE_CHECKING:
    from ai.timefold.solver.core.api.solver.change import (ProblemChangeDirector as _ProblemChangeDirector)

Solution_ = TypeVar('Solution_')

class ProblemChangeDirector:
    _delegate: '_ProblemChangeDirector'
    _java_solution: Solution_
    _python_solution: Solution_

    Entity = TypeVar('Entity')
    ProblemFact = TypeVar('ProblemFact')
    EntityOrProblemFact = TypeVar('EntityOrProblemFact')

    def __init__(self, delegate: '_ProblemChangeDirector',
                 java_solution: Solution_,
                 python_solution: Solution_):
        self._delegate = delegate
        self._java_solution = java_solution
        self._python_solution = python_solution

    def _replace_solution_in_callable(self, callable: Callable):
        if isinstance(callable, FunctionType):
            if callable.__closure__ is not None:
                for cell in callable.__closure__:
                    if cell.cell_contents is self._python_solution:
                        cell.cell_contents = self._java_solution
        return callable

    def add_entity(self, entity: Entity, modifier: Callable[[Entity], None]) -> None:
        from java.util.function import Consumer
        converted_modifier = translate_python_bytecode_to_java_bytecode(self._replace_solution_in_callable(modifier),
                                                                        Consumer)
        self._delegate.addEntity(convert_to_java_python_like_object(entity), converted_modifier)
        update_python_object_from_java(self._java_solution)

    def add_problem_fact(self, fact: ProblemFact, modifier: Callable[[ProblemFact], None]) -> None:
        from java.util.function import Consumer
        converted_modifier = translate_python_bytecode_to_java_bytecode(self._replace_solution_in_callable(modifier),
                                                                        Consumer)
        self._delegate.addProblemFact(convert_to_java_python_like_object(fact), converted_modifier)
        update_python_object_from_java(self._java_solution)

    def change_problem_property(self, problem_fact_or_entity: EntityOrProblemFact,
                                modifier: Callable[[EntityOrProblemFact], None]) -> None:
        from java.util.function import Consumer
        converted_modifier = translate_python_bytecode_to_java_bytecode(self._replace_solution_in_callable(modifier),
                                                                        Consumer)
        self._delegate.changeProblemProperty(convert_to_java_python_like_object(problem_fact_or_entity),
                                             converted_modifier)
        update_python_object_from_java(self._java_solution)

    def change_variable(self, entity: Entity, variable: str,
                        modifier: Callable[[Entity], None]) -> None:
        from java.util.function import Consumer
        converted_modifier = translate_python_bytecode_to_java_bytecode(self._replace_solution_in_callable(modifier),
                                                                        Consumer)
        self._delegate.changeVariable(convert_to_java_python_like_object(entity), variable, converted_modifier)
        update_python_object_from_java(self._java_solution)

    def lookup_working_object(self, external_object: EntityOrProblemFact) -> Optional[EntityOrProblemFact]:
        out = self._delegate.lookUpWorkingObject(convert_to_java_python_like_object(external_object)).orElse(None)
        if out is None:
            return None
        return unwrap_python_like_object(out)

    def lookup_working_object_or_fail(self, external_object: EntityOrProblemFact) -> EntityOrProblemFact:
        return unwrap_python_like_object(self._delegate.lookUpWorkingObjectOrFail(external_object))

    def remove_entity(self, entity: Entity, modifier: Callable[[Entity], None]) -> None:
        from java.util.function import Consumer
        converted_modifier = translate_python_bytecode_to_java_bytecode(self._replace_solution_in_callable(modifier),
                                                                        Consumer)
        self._delegate.removeEntity(convert_to_java_python_like_object(entity), converted_modifier)
        update_python_object_from_java(self._java_solution)

    def remove_problem_fact(self, fact: ProblemFact, modifier: Callable[[ProblemFact], None]) -> None:
        from java.util.function import Consumer
        converted_modifier = translate_python_bytecode_to_java_bytecode(self._replace_solution_in_callable(modifier),
                                                                        Consumer)
        self._delegate.removeProblemFact(convert_to_java_python_like_object(fact), converted_modifier)
        update_python_object_from_java(self._java_solution)

    def update_shadow_variables(self) -> None:
        self._delegate.updateShadowVariables()
        update_python_object_from_java(self._java_solution)


class ProblemChange(Generic[Solution_], ABC):
    @abstractmethod
    def do_change(self, working_solution: Solution_, problem_change_director: ProblemChangeDirector) -> None:
        ...


@JImplements('ai.timefold.solver.core.api.solver.change.ProblemChange', deferred=True)
class ProblemChangeWrapper:
    _delegate: ProblemChange

    def __init__(self, delegate: ProblemChange):
        self._delegate = delegate

    @JOverride
    def doChange(self, working_solution, problem_change_director: '_ProblemChangeDirector') -> None:
        wrapped_problem_change_director = ProblemChangeDirector(problem_change_director,
                                                                working_solution,
                                                                unwrap_python_like_object(working_solution))
        self._delegate.do_change(working_solution, wrapped_problem_change_director)


__all__ = ['ProblemChange', 'ProblemChangeDirector']

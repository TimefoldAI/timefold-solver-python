from ._problem_change import ProblemChange, ProblemChangeWrapper
from typing import TypeVar, TYPE_CHECKING, Generic, Callable, List
from datetime import timedelta
from jpype import JClass, JImplements, JOverride
from dataclasses import dataclass

if TYPE_CHECKING:
    # These imports require a JVM to be running, so only import if type checking
    from ..score import Score
    from ai.timefold.solver.core.api.solver import Solver as _JavaSolver

Solution_ = TypeVar('Solution_')


@dataclass
class BestSolutionChangedEvent(Generic[Solution_]):
    new_best_score: 'Score'
    new_best_solution: Solution_
    is_every_problem_change_processed: bool
    time_spent: timedelta


class Solver(Generic[Solution_]):
    _delegate: '_JavaSolver'
    _solution_class: JClass
    _has_event_listener: bool
    _event_listener_list: List[Callable[[BestSolutionChangedEvent[Solution_]], None]]

    def __init__(self, delegate: '_JavaSolver', solution_class: JClass):
        self._delegate = delegate
        self._solution_class = solution_class
        self._has_event_listener = False
        self._event_listener_list = []

    def solve(self, problem: Solution_):
        from java.lang import Exception as JavaException
        from ai.timefold.jpyinterpreter.types.errors import PythonBaseException
        from jpyinterpreter import convert_to_java_python_like_object, unwrap_python_like_object
        java_problem = convert_to_java_python_like_object(problem)
        if not self._solution_class.isInstance(java_problem):
            raise ValueError(
                f'The problem ({problem}) is not an instance of the @planning_solution class ({self._solution_class})'
            )
        try:
            java_solution = self._delegate.solve(java_problem)
        except PythonBaseException as e:
            raise unwrap_python_like_object(e)
        except JavaException as e:
            raise RuntimeError(f'Solving failed due to an error: {e.getMessage()}.\n'
                               f'Java stack trace: {e.stacktrace()}') from e
        return unwrap_python_like_object(java_solution)

    def is_solving(self) -> bool:
        return self._delegate.isSolving()

    def terminate_early(self) -> bool:
        return self._delegate.terminateEarly()

    def is_terminate_early(self) -> bool:
        return self._delegate.isTerminateEarly()

    def add_problem_change(self, problem_change: ProblemChange[Solution_]) -> None:
        self._delegate.addProblemChange(ProblemChangeWrapper(problem_change))  # noqa

    def add_problem_changes(self, problem_changes: List[ProblemChange[Solution_]]) -> None:
        self._delegate.addProblemChanges([ProblemChangeWrapper(problem_change) for problem_change in problem_changes])  # noqa

    def is_every_problem_change_processed(self) -> bool:
        return self._delegate.isEveryProblemChangeProcessed()

    def add_event_listener(self, event_listener: Callable[[BestSolutionChangedEvent[Solution_]], None]):
        from ai.timefold.solver.core.api.solver.event import SolverEventListener
        event_listener_list = self._event_listener_list
        if not self._has_event_listener:
            @JImplements(SolverEventListener)
            class EventListener:
                @JOverride
                def bestSolutionChanged(self, event):
                    from jpyinterpreter import unwrap_python_like_object
                    nonlocal event_listener_list
                    event = BestSolutionChangedEvent(
                        new_best_score=event.getNewBestScore(),
                        new_best_solution=unwrap_python_like_object(event.getNewBestSolution()),
                        is_every_problem_change_processed=event.isEveryProblemChangeProcessed(),
                        time_spent=timedelta(milliseconds=event.getTimeMillisSpent())
                    )
                    for listener in event_listener_list:
                        listener(event)

            self._has_event_listener = True
            self._delegate.addEventListener(EventListener())  # noqa

        event_listener_list.append(event_listener)

    def remove_event_listener(self, event_listener):
        self._event_listener_list.remove(event_listener)


__all__ = ['Solver', 'BestSolutionChangedEvent']

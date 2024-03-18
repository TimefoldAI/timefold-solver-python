from typing import TypeVar, Union, TYPE_CHECKING, Generic, Callable, List
from .timefold_java_interop import get_class
from .config import SolverConfig
from datetime import timedelta
from jpype import JClass, JImplements, JOverride
from dataclasses import dataclass
from enum import Enum, auto as auto_enum

if TYPE_CHECKING:
    # These imports require a JVM to be running, so only import if type checking
    from .score import Score
    from ai.timefold.solver.core.config.solver import SolverConfig as _JavaSolverConfig
    from ai.timefold.solver.core.api.solver import (SolverFactory as _JavaSolverFactory,
                                                    SolverManager as _JavaSolverManager,
                                                    SolverJob as _JavaSolverJob,
                                                    SolverJobBuilder as _JavaSolverJobBuilder,
                                                    SolutionManager as _JavaSolutionManager,
                                                    Solver as _JavaSolver)
    from ai.timefold.solver.core.api.score import ScoreExplanation as _JavaScoreExplanation
    from ai.timefold.solver.core.api.score.analysis import ScoreAnalysis as _JavaScoreAnalysis

Solution_ = TypeVar('Solution_')
ProblemId_ = TypeVar('ProblemId_')


class SolverStatus(Enum):
    NOT_SOLVING = auto_enum()
    SOLVING_SCHEDULED = auto_enum()
    SOLVING_ACTIVE = auto_enum()

    @staticmethod
    def _from_java_enum(enum_value):
        return getattr(SolverStatus, enum_value.name())


class SolverJob:
    _delegate: '_JavaSolverJob'

    def __init__(self, delegate: '_JavaSolverJob'):
        self._delegate = delegate

    def get_problem_id(self):
        from jpyinterpreter import unwrap_python_like_object
        return unwrap_python_like_object(self._delegate.getProblemId())

    def get_solver_status(self):
        return SolverStatus._from_java_enum(self._delegate.getSolverStatus())

    def get_solving_duration(self) -> timedelta:
        return timedelta(milliseconds=self._delegate.getSolvingDuration().toMillis())

    def get_final_best_solution(self):
        from jpyinterpreter import unwrap_python_like_object
        return unwrap_python_like_object(self._delegate.getFinalBestSolution())

    def terminate_early(self):
        self._delegate.terminateEarly()

    def is_terminated_early(self) -> bool:
        return self._delegate.isTerminatedEarly()

    def add_problem_change(self, problem_change):
        # TODO
        raise NotImplementedError


class SolverJobBuilder:
    _delegate: '_JavaSolverJobBuilder'

    def __init__(self, delegate: '_JavaSolverJobBuilder'):
        self._delegate = delegate

    def with_problem_id(self, problem_id) -> 'SolverJobBuilder':
        from jpyinterpreter import convert_to_java_python_like_object
        return SolverJobBuilder(self._delegate.withProblemId(convert_to_java_python_like_object(problem_id)))

    def with_problem(self, problem) -> 'SolverJobBuilder':
        from jpyinterpreter import convert_to_java_python_like_object
        return SolverJobBuilder(self._delegate.withProblem(convert_to_java_python_like_object(problem)))

    def with_config_override(self, config_override) -> 'SolverJobBuilder':
        # TODO: Create wrapper object for config override
        raise NotImplementedError

    def with_problem_finder(self, problem_finder) -> 'SolverJobBuilder':
        from java.util.function import Function
        from jpyinterpreter import convert_to_java_python_like_object, unwrap_python_like_object
        java_finder = Function @ (lambda problem_id: convert_to_java_python_like_object(
            problem_finder(unwrap_python_like_object(problem_id))))
        return SolverJobBuilder(self._delegate.withProblemFinder(java_finder))

    def with_best_solution_consumer(self, best_solution_consumer) -> 'SolverJobBuilder':
        from java.util.function import Consumer
        from jpyinterpreter import unwrap_python_like_object

        java_consumer = Consumer @ (lambda solution: best_solution_consumer(unwrap_python_like_object(solution)))
        return SolverJobBuilder(self._delegate.withBestSolutionConsumer(java_consumer))

    def with_final_best_solution_consumer(self, final_best_solution_consumer) -> 'SolverJobBuilder':
        from java.util.function import Consumer
        from jpyinterpreter import unwrap_python_like_object

        java_consumer = Consumer @ (lambda solution: final_best_solution_consumer(unwrap_python_like_object(solution)))
        return SolverJobBuilder(
            self._delegate.withFinalBestSolutionConsumer(java_consumer))

    def with_exception_handler(self, exception_handler) -> 'SolverJobBuilder':
        from java.util.function import BiConsumer
        from jpyinterpreter import unwrap_python_like_object

        java_consumer = BiConsumer @ (lambda problem_id, error: exception_handler(unwrap_python_like_object(problem_id),
                                                                                  error))
        return SolverJobBuilder(
            self._delegate.withExceptionHandler(java_consumer))

    def run(self) -> SolverJob:
        return SolverJob(self._delegate.run())


class SolverManager:
    _delegate: '_JavaSolverManager'

    def __init__(self, delegate: '_JavaSolverManager'):
        self._delegate = delegate

    @staticmethod
    def create(solver_factory: 'SolverFactory'):
        from ai.timefold.solver.core.api.solver import SolverManager as JavaSolverManager
        return SolverManager(JavaSolverManager.create(solver_factory._delegate))  # noqa

    def solve(self, problem_id, problem, final_best_solution_listener=None):
        builder = (self.solve_builder()
                   .with_problem_id(problem_id)
                   .with_problem(problem))

        if final_best_solution_listener is not None:
            builder = builder.with_final_best_solution_consumer(final_best_solution_listener)

        return builder.run()

    def solve_and_listen(self, problem_id, problem, listener):
        return (self.solve_builder()
                .with_problem_id(problem_id)
                .with_problem(problem)
                .with_best_solution_consumer(listener)
                .run())

    def solve_builder(self) -> SolverJobBuilder:
        return SolverJobBuilder(self._delegate.solveBuilder())

    def get_solver_status(self, problem_id):
        from jpyinterpreter import convert_to_java_python_like_object
        return SolverStatus._from_java_enum(self._delegate.getSolverStatus(
            convert_to_java_python_like_object(problem_id)))

    def terminate_early(self, problem_id):
        from jpyinterpreter import convert_to_java_python_like_object
        self._delegate.terminateEarly(convert_to_java_python_like_object(problem_id))

    def add_problem_change(self, problem_id, problem_change):
        # TODO
        raise NotImplementedError

    def close(self):
        self._delegate.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._delegate.close()


class SolutionManager:
    _delegate: '_JavaSolutionManager'

    def __init__(self, delegate: '_JavaSolutionManager'):
        self._delegate = delegate

    @staticmethod
    def create(solver_factory: 'SolverFactory'):
        from ai.timefold.solver.core.api.solver import SolutionManager as JavaSolutionManager
        return SolutionManager(JavaSolutionManager.create(solver_factory._delegate))

    def update(self, solution, solution_update_policy=None) -> 'Score':
        #  TODO handle solution_update_policy
        from jpyinterpreter import convert_to_java_python_like_object, update_python_object_from_java
        java_solution = convert_to_java_python_like_object(solution)
        out = self._delegate.update(java_solution)
        update_python_object_from_java(java_solution)
        return out

    def analyze(self, solution, score_analysis_fetch_policy=None, solution_update_policy=None) -> 'ScoreAnalysis':
        #  TODO handle policies
        from jpyinterpreter import convert_to_java_python_like_object
        return ScoreAnalysis(self._delegate.analyze(convert_to_java_python_like_object(solution)))

    def explain(self, solution, solution_update_policy=None) -> 'ScoreExplanation':
        #  TODO handle policies
        from jpyinterpreter import convert_to_java_python_like_object
        return ScoreExplanation(self._delegate.explain(convert_to_java_python_like_object(solution)))

    def recommend_fit(self, solution, entity_or_element, proposition_function, score_analysis_fetch_policy=None):
        #  TODO
        raise NotImplementedError


class ScoreExplanation:
    _delegate: '_JavaScoreExplanation'

    def __init__(self, delegate: '_JavaScoreExplanation'):
        self._delegate = delegate

    def get_constraint_match_total_map(self):
        # TODO python-ify the returned map
        return self._delegate.getConstraintMatchTotalMap()

    def get_indictment_map(self):
        # TODO
        raise NotImplementedError

    def get_justification_list(self, justification_type=None):
        # TODO
        raise NotImplementedError

    def get_score(self) -> 'Score':
        return self._delegate.getScore()

    def get_solution(self):
        from jpyinterpreter import unwrap_python_like_object
        return unwrap_python_like_object(self._delegate.getSolution())

    def get_summary(self) -> str:
        return self._delegate.getSummary()


class ScoreAnalysis:
    _delegate: '_JavaScoreAnalysis'

    def __init__(self, delegate: '_JavaScoreAnalysis'):
        self._delegate = delegate

    @property
    def score(self) -> 'Score':
        return self._delegate.score()

    @property
    def constraint_map(self):
        # TODO
        raise NotImplementedError

    @property
    def constraint_analyses(self):
        # TODO
        raise NotImplementedError


class SolverFactory:
    _delegate: '_JavaSolverFactory'
    _solution_class: JClass

    def __init__(self, delegate: '_JavaSolverFactory', solution_class: JClass):
        self._delegate = delegate
        self._solution_class = solution_class

    @staticmethod
    def create(solver_config: SolverConfig):
        from ai.timefold.solver.core.api.solver import SolverFactory as JavaSolverFactory
        solver_config = solver_config._to_java_solver_config()
        delegate = JavaSolverFactory.create(solver_config)  # noqa
        return SolverFactory(delegate, solver_config.getSolutionClass())  # noqa

    def build_solver(self):
        return Solver(self._delegate.buildSolver(), self._solution_class)


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
            python_error = unwrap_python_like_object(e)
            raise RuntimeError(f'Solving failed due to an error: {e.getMessage()}.\n'
                               f'Java stack trace: {e.stacktrace()}') from python_error
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

    def add_problem_change(self, problem_change):
        pass  # TODO

    def add_problem_changes(self, problem_changes):
        pass  # TODO

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


def compose_constraint_id(solution_type_or_package: Union[type, str], constraint_name: str) -> str:
    """Returns the constraint id with the given constraint package and the given name

    :param solution_type_or_package: The constraint package, or a class decorated with @planning_solution
        (for when the constraint is in the default package)
    :param constraint_name: The name of the constraint
    :return: The constraint id with the given name in the default package.
    :rtype: str
    """
    package = solution_type_or_package
    if not isinstance(solution_type_or_package, str):
        package = get_class(solution_type_or_package).getPackage().getName()
    return f'{package}/{constraint_name}'

from .solver_factory import SolverFactory

from typing import TypeVar, TYPE_CHECKING
from datetime import timedelta
from enum import Enum, auto as auto_enum

if TYPE_CHECKING:
    # These imports require a JVM to be running, so only import if type checking
    from ai.timefold.solver.core.api.solver import (SolverManager as _JavaSolverManager,
                                                    SolverJob as _JavaSolverJob,
                                                    SolverJobBuilder as _JavaSolverJobBuilder)

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


__all__ = ['SolverManager', 'SolverJobBuilder', 'SolverJob', 'SolverStatus']

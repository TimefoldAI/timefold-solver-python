from ._solver import Solver
from .config import SolverConfig, SolverConfigOverride

from typing import TypeVar, Generic, TYPE_CHECKING
from jpype import JClass

if TYPE_CHECKING:
    # These imports require a JVM to be running, so only import if type checking
    from ai.timefold.solver.core.api.solver import SolverFactory as _JavaSolverFactory


Solution_ = TypeVar('Solution_')


class SolverFactory(Generic[Solution_]):
    _delegate: '_JavaSolverFactory'
    _solution_class: JClass

    def __init__(self, delegate: '_JavaSolverFactory', solution_class: JClass):
        self._delegate = delegate
        self._solution_class = solution_class

    @staticmethod
    def create(solver_config: SolverConfig[Solution_]) -> 'SolverFactory[Solution_]':
        from ai.timefold.solver.core.api.solver import SolverFactory as JavaSolverFactory
        solver_config = solver_config._to_java_solver_config()
        delegate = JavaSolverFactory.create(solver_config)  # noqa
        return SolverFactory(delegate, solver_config.getSolutionClass())  # noqa

    def build_solver(self, solver_config_override: SolverConfigOverride = None) -> Solver[Solution_]:
        if solver_config_override is None:
            return Solver(self._delegate.buildSolver(), self._solution_class)
        else:
            return Solver(self._delegate.buildSolver(solver_config_override._to_java_solver_config_override()),
                          self._solution_class)


__all__ = ['SolverFactory']

from ._solver_factory import SolverFactory
from ._solver_manager import SolverManager
from .score import ScoreAnalysis, ScoreExplanation

from typing import TypeVar, Generic, TYPE_CHECKING, Any

if TYPE_CHECKING:
    # These imports require a JVM to be running, so only import if type checking
    from .score import Score
    from ai.timefold.solver.core.api.solver import SolutionManager as _JavaSolutionManager

Solution_ = TypeVar('Solution_')
ProblemId_ = TypeVar('ProblemId_')
Score_ = TypeVar('Score_', bound='Score')
Justification_ = TypeVar('Justification_', bound='ConstraintJustification')


class SolutionManager(Generic[Solution_]):
    _delegate: '_JavaSolutionManager'

    def __init__(self, delegate: '_JavaSolutionManager'):
        self._delegate = delegate

    @staticmethod
    def create(solver_factory: SolverFactory[Solution_] | SolverManager[Solution_, Any]) -> \
            'SolutionManager[Solution_]':
        from ai.timefold.solver.core.api.solver import SolutionManager as JavaSolutionManager
        return SolutionManager(JavaSolutionManager.create(solver_factory._delegate))

    def update(self, solution: Solution_, solution_update_policy=None) -> 'Score':
        #  TODO handle solution_update_policy
        from jpyinterpreter import convert_to_java_python_like_object, update_python_object_from_java
        java_solution = convert_to_java_python_like_object(solution)
        out = self._delegate.update(java_solution)
        update_python_object_from_java(java_solution)
        return out

    def analyze(self, solution: Solution_, score_analysis_fetch_policy=None, solution_update_policy=None) \
            -> 'ScoreAnalysis':
        #  TODO handle policies
        from jpyinterpreter import convert_to_java_python_like_object
        return ScoreAnalysis(self._delegate.analyze(convert_to_java_python_like_object(solution)))

    def explain(self, solution: Solution_, solution_update_policy=None) -> 'ScoreExplanation':
        #  TODO handle policies
        from jpyinterpreter import convert_to_java_python_like_object
        return ScoreExplanation(self._delegate.explain(convert_to_java_python_like_object(solution)))

    def recommend_fit(self, solution: Solution_, entity_or_element, proposition_function,
                      score_analysis_fetch_policy=None):
        #  TODO
        raise NotImplementedError


__all__ = ['SolutionManager']

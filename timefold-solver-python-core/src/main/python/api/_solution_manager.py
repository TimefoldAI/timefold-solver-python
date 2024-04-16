from ._solver_factory import SolverFactory
from .._timefold_java_interop import get_class

from typing import TypeVar, Generic, Union, TYPE_CHECKING


if TYPE_CHECKING:
    # These imports require a JVM to be running, so only import if type checking
    from ..score import Score
    from ai.timefold.solver.core.api.solver import SolutionManager as _JavaSolutionManager
    from ai.timefold.solver.core.api.score import ScoreExplanation as _JavaScoreExplanation
    from ai.timefold.solver.core.api.score.analysis import ScoreAnalysis as _JavaScoreAnalysis

Solution_ = TypeVar('Solution_')
ProblemId_ = TypeVar('ProblemId_')


class SolutionManager(Generic[Solution_]):
    _delegate: '_JavaSolutionManager'

    def __init__(self, delegate: '_JavaSolutionManager'):
        self._delegate = delegate

    @staticmethod
    def create(solver_factory: 'SolverFactory[Solution_]') -> 'SolutionManager[Solution_]':
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


class ScoreExplanation(Generic[Solution_]):
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

    def get_solution(self) -> Solution_:
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


__all__ = ['SolutionManager', 'ScoreExplanation', 'ScoreAnalysis', 'compose_constraint_id']

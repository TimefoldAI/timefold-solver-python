from timefold.solver.api import *
from timefold.solver.annotation import *
from timefold.solver.config import *
from timefold.solver.score import *
from timefold.solver.constraint import *

from dataclasses import dataclass, field
from typing import Annotated, List


@planning_entity
@dataclass
class Entity:
    code: Annotated[str, PlanningId]
    value: Annotated[int, PlanningVariable] = field(default=None)


@constraint_provider
def my_constraints(constraint_factory: ConstraintFactory):
    return [
        constraint_factory.for_each(Entity)
                          .reward(SimpleScore.ONE, lambda entity: entity.value)
                          .as_constraint('Maximize Value'),
    ]


@planning_solution
@dataclass
class Solution:
    entity_list: Annotated[List[Entity], PlanningEntityCollectionProperty]
    value_range: Annotated[List[int], ValueRangeProvider]
    score: Annotated[SimpleScore, PlanningScore] = field(default=None)


solver_config = SolverConfig(
    solution_class=Solution,
    entity_class_list=[Entity],
    score_director_factory_config=ScoreDirectorFactoryConfig(
        constraint_provider_function=my_constraints
    )
)


def assert_score_manager(score_manager):
    problem: Solution = Solution([Entity('A', 1), Entity('B', 1), Entity('C', 1)], [1, 2, 3])
    assert problem.score is None
    score = score_manager.update(problem)
    assert score.score() == 3
    assert problem.score.score() == 3

    score_explanation = score_manager.explain(problem)
    assert score_explanation.get_solution() is problem
    assert score_explanation.get_score().score() == 3
    assert score_explanation.get_constraint_match_total_map() \
                            .get(compose_constraint_id(Solution, 'Maximize Value')) \
                            .getConstraintMatchCount() == 3


def test_solver_manager_score_manager():
    with SolverManager.create(SolverFactory.create(solver_config)) as solver_manager:
        assert_score_manager(SolutionManager.create(solver_manager))


def test_solver_factory_score_manager():
    assert_score_manager(SolutionManager.create(SolverFactory.create(solver_config)))

import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint

from dataclasses import dataclass, field
from typing import Annotated, List


@timefold.solver.planning_entity
@dataclass
class Entity:
    code: Annotated[str, timefold.solver.PlanningId]
    value: Annotated[int, timefold.solver.PlanningVariable] = field(default=None)


@timefold.solver.constraint_provider
def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
    return [
        constraint_factory.for_each(Entity)
            .reward('Maximize Value', timefold.solver.score.SimpleScore.ONE, lambda entity: entity.value),
    ]


@timefold.solver.planning_solution
@dataclass
class Solution:
    entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
    value_range: Annotated[List[int], timefold.solver.ValueRangeProvider]
    score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)


solver_config = timefold.solver.config.SolverConfig(
    solution_class=Solution,
    entity_class_list=[Entity],
    score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
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
                            .get(timefold.solver.compose_constraint_id(Solution, 'Maximize Value')) \
                            .getConstraintMatchCount() == 3


def test_solver_manager_score_manager():
    with timefold.solver.SolverManager.create(timefold.solver.SolverFactory.create(solver_config)) as solver_manager:
        assert_score_manager(timefold.solver.SolutionManager.create(solver_manager))


def test_solver_factory_score_manager():
    assert_score_manager(timefold.solver.SolutionManager.create(timefold.solver.SolverFactory.create(solver_config)))

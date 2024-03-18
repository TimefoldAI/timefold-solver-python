import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint

from dataclasses import dataclass, field
from typing import Annotated, List


def test_solver_events():
    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: str
        value: Annotated[int, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .reward('Maximize value', timefold.solver.score.SimpleScore.ONE, lambda entity: entity.value),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        value_range: Annotated[List[int], timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints,
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='6'
        )
    )

    problem: Solution = Solution([Entity('A'), Entity('B')], [1, 2, 3])
    score_list = []
    solution_list = []

    def on_best_solution_changed(event):
        solution_list.append(event.new_best_solution)
        score_list.append(event.new_best_score)

    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solver.add_event_listener(on_best_solution_changed)
    solution = solver.solve(problem)

    assert solution.score.score() == 6
    assert solution.entities[0].value == 3
    assert solution.entities[1].value == 3
    assert len(score_list) == len(solution_list)
    assert len(solution_list) == 1
    assert score_list[0].score() == 6
    assert solution_list[0].score.score() == 6
    assert solution_list[0].entities[0].value == 3
    assert solution_list[0].entities[1].value == 3

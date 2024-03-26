import timefold.solver
import timefold.solver.score
import timefold.solver.config

from dataclasses import dataclass, field
from typing import Annotated, List


def test_pinning_filter():
    def is_entity_pinned(_, entity):
        return entity.is_pinned

    @timefold.solver.planning_entity(pinning_filter=is_entity_pinned)
    @dataclass
    class Point:
        value: Annotated[int, timefold.solver.PlanningVariable]
        is_pinned: bool = field(default=False)

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        values: Annotated[List[int], timefold.solver.ValueRangeProvider]
        points: Annotated[List[Point], timefold.solver.PlanningEntityCollectionProperty]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory):
        return [
            constraint_factory.for_each(Point)
                              .penalize("Minimize Value", timefold.solver.score.SimpleScore.ONE, lambda point: point.value)
        ]

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Point],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            unimproved_spent_limit=timefold.solver.config.Duration(milliseconds=100)
        )
    )
    problem: Solution = Solution([0, 1, 2],
                                 [
                                     Point(0),
                                     Point(1),
                                     Point(2, is_pinned=True)
                                 ])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == -2


def test_planning_pin():
    @timefold.solver.planning_entity
    @dataclass
    class Point:
        value: Annotated[int, timefold.solver.PlanningVariable]
        is_pinned: Annotated[bool, timefold.solver.PlanningPin] = field(default=False)

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        values: Annotated[List[int], timefold.solver.ValueRangeProvider]
        points: Annotated[List[Point], timefold.solver.PlanningEntityCollectionProperty]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory):
        return [
            constraint_factory.for_each(Point)
                .penalize("Minimize Value", timefold.solver.score.SimpleScore.ONE, lambda point: point.value)
        ]

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Point],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            unimproved_spent_limit=timefold.solver.config.Duration(milliseconds=100)
        )
    )
    problem: Solution = Solution([0, 1, 2],
                                 [
                                     Point(0),
                                     Point(1),
                                     Point(2, is_pinned=True)
                                 ])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == -2

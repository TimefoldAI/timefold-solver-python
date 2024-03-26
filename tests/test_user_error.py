import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint
import pytest
import re

from typing import Annotated, List
from dataclasses import dataclass, field


@timefold.solver.planning_entity
@dataclass
class Entity:
    value: Annotated[str, timefold.solver.PlanningVariable] = field(default=None)


@timefold.solver.planning_solution
@dataclass
class Solution:
    entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
    value_list: Annotated[List[str], timefold.solver.ValueRangeProvider]
    score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)


@timefold.solver.constraint_provider
def my_constraints(constraint_factory):
    return [
        constraint_factory.for_each(timefold.solver.get_class(Entity))
            .penalize('Penalize each entity', timefold.solver.score.SimpleScore.ONE, lambda entity: 'TEN')
    ]


def test_non_planning_solution_being_passed_to_solve():
    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        )
    )
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    with pytest.raises(ValueError, match=re.escape(
            f'The problem ({10}) is not an instance of the @planning_solution class'
    )):
        solver.solve(10)


def test_none_passed_to_solve():
    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        )
    )
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    with pytest.raises(ValueError, match=re.escape(
            f'The problem ({None}) is not an instance of the @planning_solution class'
    )):
        solver.solve(None)


def test_bad_return_type():
    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            spent_limit=timefold.solver.config.Duration(milliseconds=100)
        )
    )

    problem = Solution([Entity()], ['1', '2', '3'])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    with pytest.raises(RuntimeError):
        solver.solve(problem)


def test_non_proxied_class_passed():
    class NonProxied:
        pass

    with pytest.raises(TypeError, match=re.escape(
            f'is not a @planning_solution class'
    )):
        solver_config = timefold.solver.config.SolverConfig(
            solution_class=NonProxied
        )._to_java_solver_config()


def test_non_proxied_function_passed():
    def not_proxied():
        pass

    with pytest.raises(TypeError, match=re.escape(
            f'is not a @constraint_provider function')):
        solver_config = timefold.solver.config.SolverConfig(
            score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
                constraint_provider_function=not_proxied
            )
        )._to_java_solver_config()

import pytest

from timefold.solver.domain import *
from timefold.solver.score import *
from timefold.solver.config import *
from timefold.solver.test import *

from typing import Annotated, List
from dataclasses import dataclass, field


def verifier_suite(verifier: ConstraintVerifier, same_value, is_value_one,
                   solution, e1, e2, e3, v1, v2, v3):
    verifier.verify_that(same_value) \
        .given(e1, e2) \
        .penalizes(0)

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2) \
            .rewards()

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2) \
            .penalizes()

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2) \
            .penalizes(1)

    e1.value = v1
    e2.value = v1
    e3.value = v1

    verifier.verify_that(same_value) \
        .given(e1, e2) \
        .penalizes(1)

    verifier.verify_that(same_value) \
        .given(e1, e2) \
        .penalizes()

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2) \
            .rewards(1)

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2) \
            .penalizes(0)

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2) \
            .penalizes(2)

    verifier.verify_that(same_value) \
        .given(e1, e2, e3) \
        .penalizes(3)

    verifier.verify_that(same_value) \
        .given(e1, e2, e3) \
        .penalizes()

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2, e3) \
            .rewards(3)

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2, e3) \
            .penalizes(2)

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given(e1, e2, e3) \
            .penalizes(4)

    verifier.verify_that(same_value) \
        .given_solution(solution) \
        .penalizes(3)

    verifier.verify_that(same_value) \
        .given_solution(solution) \
        .penalizes()

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given_solution(solution) \
            .rewards(3)

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given_solution(solution) \
            .penalizes(2)

    with pytest.raises(AssertionError):
        verifier.verify_that(same_value) \
            .given_solution(solution) \
            .penalizes(4)

    verifier.verify_that(is_value_one) \
        .given(e1, e2, e3) \
        .rewards(3)

    verifier.verify_that(is_value_one) \
        .given(e1, e2, e3) \
        .rewards()

    with pytest.raises(AssertionError):
        verifier.verify_that(is_value_one) \
            .given(e1, e2, e3) \
            .penalizes()

    with pytest.raises(AssertionError):
        verifier.verify_that(is_value_one) \
            .given(e1, e2, e3) \
            .penalizes(3)

    with pytest.raises(AssertionError):
        verifier.verify_that(is_value_one) \
            .given(e1, e2, e3) \
            .rewards(2)

    with pytest.raises(AssertionError):
        verifier.verify_that(is_value_one) \
            .given(e1, e2, e3) \
            .rewards(4)

    verifier.verify_that() \
        .given(e1, e2, e3) \
        .scores(SimpleScore.of(0))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given(e1, e2, e3) \
            .scores(SimpleScore.of(1))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given(e1, e2, e3) \
            .scores(SimpleScore.of(-1))

    verifier.verify_that() \
        .given_solution(solution) \
        .scores(SimpleScore.of(0))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given_solution(solution) \
            .scores(SimpleScore.of(1))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given_solution(solution) \
            .scores(SimpleScore.of(-1))

    e1.value = v1
    e2.value = v2
    e3.value = v3
    verifier.verify_that() \
        .given(e1, e2, e3) \
        .scores(SimpleScore.of(1))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given(e1, e2, e3) \
            .scores(SimpleScore.of(2))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given(e1, e2, e3) \
            .scores(SimpleScore.of(0))

    verifier.verify_that() \
        .given_solution(solution) \
        .scores(SimpleScore.of(1))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given_solution(solution) \
            .scores(SimpleScore.of(2))

    with pytest.raises(AssertionError):
        verifier.verify_that() \
            .given_solution(solution) \
            .scores(SimpleScore.of(0))


def test_constraint_verifier_create():
    @dataclass
    class Value:
        code: str

    @planning_entity
    @dataclass
    class Entity:
        code: str
        value: Annotated[Value, PlanningVariable] = field(default=None)

    def same_value(constraint_factory: ConstraintFactory):
        return (constraint_factory.for_each(Entity)
                .join(Entity, Joiners.less_than(lambda e: e.code),
                      Joiners.equal(lambda e: e.value))
                .penalize(SimpleScore.ONE)
                .as_constraint('Same Value')
                )

    def is_value_one(constraint_factory: ConstraintFactory):
        return (constraint_factory.for_each(Entity)
                .filter(lambda e: e.value.code == 'v1')
                .reward(SimpleScore.ONE)
                .as_constraint('Value 1')
                )

    @constraint_provider
    def my_constraints(constraint_factory: ConstraintFactory):
        return [
            same_value(constraint_factory),
            is_value_one(constraint_factory)
        ]

    @planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], PlanningEntityCollectionProperty]
        values: Annotated[List[Value], ProblemFactCollectionProperty, ValueRangeProvider]
        score: Annotated[SimpleScore, PlanningScore] = field(default=None)

    solver_config = SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        )
    )

    verifier = ConstraintVerifier.create(solver_config)

    e1 = Entity('e1')
    e2 = Entity('e2')
    e3 = Entity('e3')

    v1 = Value('v1')
    v2 = Value('v2')
    v3 = Value('v3')

    solution = Solution([e1, e2, e3], [v1, v2, v3])

    verifier_suite(verifier, same_value, is_value_one,
                   solution, e1, e2, e3, v1, v2, v3)

    verifier = ConstraintVerifier.build(my_constraints, Solution, Entity)

    e1 = Entity('e1')
    e2 = Entity('e2')
    e3 = Entity('e3')

    v1 = Value('v1')
    v2 = Value('v2')
    v3 = Value('v3')

    solution = Solution([e1, e2, e3], [v1, v2, v3])

    verifier_suite(verifier, same_value, is_value_one,
                   solution, e1, e2, e3, v1, v2, v3)

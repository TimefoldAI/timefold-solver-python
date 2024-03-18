import inspect
import re
from dataclasses import dataclass, field
from typing import Annotated, List
import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint
from timefold.solver.constraint import UniConstraintStream, BiConstraintStream, TriConstraintStream, QuadConstraintStream, \
    Joiners, ConstraintCollectors, ConstraintFactory
from ai.timefold.solver.core.api.score.stream import Joiners as JavaJoiners,\
    ConstraintCollectors as JavaConstraintCollectors, ConstraintFactory as JavaConstraintFactory
from ai.timefold.solver.core.api.score.stream.uni import UniConstraintStream as JavaUniConstraintStream
from ai.timefold.solver.core.api.score.stream.bi import BiConstraintStream as JavaBiConstraintStream
from ai.timefold.solver.core.api.score.stream.tri import TriConstraintStream as JavaTriConstraintStream
from ai.timefold.solver.core.api.score.stream.quad import QuadConstraintStream as JavaQuadConstraintStream

@dataclass
class Value:
    def __init__(self, number):
        self.number = number


@timefold.solver.planning_entity
@dataclass
class Entity:
    code: str
    value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)


@timefold.solver.planning_solution
@dataclass
class Solution:
    entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
    value_list: Annotated[List[Value],
                          timefold.solver.ProblemFactCollectionProperty,
                          timefold.solver.ValueRangeProvider]
    score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)


def create_score_manager(constraint_provider):
    return timefold.solver.SolutionManager.create(timefold.solver.SolverFactory.create(
        timefold.solver.config.SolverConfig(solution_class=Solution,
                                            entity_class_list=[Entity],
                                            score_director_factory_config=
                                            timefold.solver.config.ScoreDirectorFactoryConfig(
                                                constraint_provider_function=constraint_provider
                                            ))))


def test_for_each():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .reward('Count', timefold.solver.score.SimpleScore.ONE)
        ]
    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)

    problem = Solution([entity_a, entity_b], [value_1])

    assert score_manager.explain(problem).get_score().score() == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 1

    entity_b.value = value_1

    assert score_manager.explain(problem).get_score().score() == 2


def test_filter_uni():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .filter(lambda e: e.value.number == 1)
            .reward('Count', timefold.solver.score.SimpleScore.ONE)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).get_score().score() == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 1

    entity_b.value = value_2
    assert score_manager.explain(problem).get_score().score() == 1

    entity_b.value = value_1
    assert score_manager.explain(problem).get_score().score() == 2


def test_filter_bi():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity)
            .filter(lambda e1, e2: e1.value.number == 1 and e2.value.number == 2)
            .reward('Count', timefold.solver.score.SimpleScore.ONE)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).get_score().score() == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 0

    entity_b.value = value_1
    assert score_manager.explain(problem).get_score().score() == 0

    entity_b.value = value_2
    assert score_manager.explain(problem).get_score().score() == 1


def test_filter_tri():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity)
            .join(Entity)
            .filter(lambda e1, e2, e3: e1.value.number == 1 and e2.value.number == 2 and e3.value.number == 3)
            .reward('Count', timefold.solver.score.SimpleScore.ONE)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')
    entity_c: Entity = Entity('C')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)

    problem = Solution([entity_a, entity_b, entity_c], [value_1, value_2, value_3])

    assert score_manager.explain(problem).get_score().score() == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 0

    entity_b.value = value_2
    assert score_manager.explain(problem).get_score().score() == 0

    entity_c.value = value_1
    assert score_manager.explain(problem).get_score().score() == 0

    entity_c.value = value_3
    assert score_manager.explain(problem).get_score().score() == 1


def test_filter_quad():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity)
            .join(Entity)
            .join(Entity)
            .filter(lambda e1, e2, e3, e4: e1.value.number == 1 and e2.value.number == 2 and e3.value.number == 3
                                           and e4.value.number == 4)
            .reward('Count', timefold.solver.score.SimpleScore.ONE)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')
    entity_c: Entity = Entity('C')
    entity_d: Entity = Entity('D')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)
    value_4 = Value(4)

    problem = Solution([entity_a, entity_b, entity_c, entity_d], [value_1, value_2, value_3, value_4])

    assert score_manager.explain(problem).get_score().score() == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 0

    entity_b.value = value_2
    assert score_manager.explain(problem).get_score().score() == 0

    entity_c.value = value_3
    assert score_manager.explain(problem).get_score().score() == 0

    entity_d.value = value_1
    assert score_manager.explain(problem).get_score().score() == 0

    entity_d.value = value_4
    assert score_manager.explain(problem).get_score().score() == 1


def test_join_uni():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity, timefold.solver.constraint.Joiners.equal(lambda entity: entity.code))
            .filter(lambda e1, e2: e1 is not e2)
            .reward('Count', timefold.solver.score.SimpleScore.ONE, lambda e1, e2: e1.value.number * e2.value.number)
        ]
    score_manager = create_score_manager(define_constraints)
    entity_a1: Entity = Entity('A')
    entity_a2: Entity = Entity('A')
    entity_b1: Entity = Entity('B')
    entity_b2: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a1, entity_a2, entity_b1, entity_b2], [value_1, value_2])

    entity_a1.value = value_1

    assert score_manager.explain(problem).get_score().score() == 0

    entity_a1.value = value_1
    entity_a2.value = value_1

    entity_b1.value = value_2
    entity_b2.value = value_2

    # 1 * 1 + 1 * 1 + 2 * 2 + 2 * 2
    assert score_manager.explain(problem).get_score().score() == 10

    entity_a1.value = value_2
    entity_b1.value = value_1

    # 1 * 2 + 1 * 2 + 1 * 2 + 1 * 2
    assert score_manager.explain(problem).get_score().score() == 8


def test_map():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .map(lambda e: e.value.number)
            .reward('Count', timefold.solver.score.SimpleScore.ONE, lambda v: v)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).get_score().score() == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 1

    entity_b.value = value_1

    assert score_manager.explain(problem).get_score().score() == 2

    entity_b.value = value_2

    assert score_manager.explain(problem).get_score().score() == 3


def test_multi_map():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .map(lambda e: e.code, lambda e: e.value.number)
            .reward('Count', timefold.solver.score.SimpleScore.ONE, lambda c, v: len(c) + v)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('BB')

    value_1 = Value(10)
    value_2 = Value(20)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).get_score().score() == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 11

    entity_b.value = value_1

    assert score_manager.explain(problem).get_score().score() == 23

    entity_b.value = value_2

    assert score_manager.explain(problem).get_score().score() == 33


def test_expand():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .expand(lambda e: e.value.number)
            .reward('Count', timefold.solver.score.SimpleScore.ONE, lambda e, v: v)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).get_score().score() == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 1

    entity_b.value = value_1

    assert score_manager.explain(problem).get_score().score() == 2

    entity_b.value = value_2

    assert score_manager.explain(problem).get_score().score() == 3


def test_multi_expand():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .expand(lambda e: e.code, lambda e: e.value.number)
            .reward('Count', timefold.solver.score.SimpleScore.ONE, lambda e, c, v: len(c) + v)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('BB')

    value_1 = Value(10)
    value_2 = Value(20)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).get_score().score() == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 11

    entity_b.value = value_1

    assert score_manager.explain(problem).get_score().score() == 23

    entity_b.value = value_2

    assert score_manager.explain(problem).get_score().score() == 33


def test_concat():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .filter(lambda e: e.value.number == 1)
            .concat(constraint_factory.for_each(Entity).filter(lambda e: e.value.number == 2))
            .reward('Count', timefold.solver.score.SimpleScore.ONE)
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)

    problem = Solution([entity_a, entity_b], [value_1, value_2, value_3])

    assert score_manager.explain(problem).get_score().score() == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).get_score().score() == 1

    entity_b.value = value_2

    assert score_manager.explain(problem).get_score().score() == 2

    entity_b.value = value_3

    assert score_manager.explain(problem).get_score().score() == 1


ignored_python_functions = {
    '_call_comparison_java_joiner',
    '__init__',
    'from_',  # ignored since the camelcase version is from, which is a keyword in Python
}

ignored_java_functions = {
    'equals',
    'getClass',
    'hashCode',
    'notify',
    'notifyAll',
    'toString',
    'wait',
    'countLongBi',  # Python has no concept of Long (everything a BigInteger)
    'countLongQuad',
    'countLongTri',
    '_handler',  # JPype handler field should be ignored
    # These methods are deprecated
    'from_',
    'fromUnfiltered',
    'fromUniquePair',
    'forEachIncludingNullVars',
    'ifExistsIncludingNullVars',
    'ifNotExistsIncludingNullVars',
    'ifExistsOtherIncludingNullVars',
    'ifNotExistsOtherIncludingNullVars',
}


def test_has_all_methods():

    for python_type, java_type in ((UniConstraintStream, JavaUniConstraintStream),
                                   (BiConstraintStream, JavaBiConstraintStream),
                                   (TriConstraintStream, JavaTriConstraintStream),
                                   (QuadConstraintStream, JavaQuadConstraintStream),
                                   (Joiners, JavaJoiners),
                                   (ConstraintCollectors, JavaConstraintCollectors),
                                   (ConstraintFactory, JavaConstraintFactory)):
        missing = []
        for function_name, function_impl in inspect.getmembers(java_type, inspect.isfunction):
            if function_name in ignored_java_functions:
                continue
            if python_type is ConstraintCollectors and function_name.endswith(('Long', 'BigInteger', 'Duration',
                                                                               'BigDecimal', 'Period')):
                continue  # Python only has a single integer type (= BigInteger) and does not support Java Durations
                          # or Period

            snake_case_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', function_name)
            # change h_t_t_p -> http
            snake_case_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case_name).lower()
            if not hasattr(python_type, snake_case_name):
                missing.append(snake_case_name)

        assert missing == []

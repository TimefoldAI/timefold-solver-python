from timefold.solver import *
from timefold.solver.domain import *
from timefold.solver.score import *
from timefold.solver.config import *

import inspect
import re
from dataclasses import dataclass, field
from typing import Annotated, List
from ai.timefold.solver.core.api.score.stream import Joiners as JavaJoiners, \
    ConstraintCollectors as JavaConstraintCollectors, ConstraintFactory as JavaConstraintFactory
from ai.timefold.solver.core.api.score.stream.uni import (UniConstraintStream as JavaUniConstraintStream,
                                                          UniConstraintBuilder as JavaUniConstraintBuilder)
from ai.timefold.solver.core.api.score.stream.bi import (BiConstraintStream as JavaBiConstraintStream,
                                                         BiConstraintBuilder as JavaBiConstraintBuilder)
from ai.timefold.solver.core.api.score.stream.tri import (TriConstraintStream as JavaTriConstraintStream,
                                                          TriConstraintBuilder as JavaTriConstraintBuilder)
from ai.timefold.solver.core.api.score.stream.quad import (QuadConstraintStream as JavaQuadConstraintStream,
                                                           QuadConstraintBuilder as JavaQuadConstraintBuilder)


@dataclass
class Value:
    def __init__(self, number):
        self.number = number


@planning_entity
@dataclass
class Entity:
    code: str
    value: Annotated[Value, PlanningVariable] = field(default=None)


@planning_solution
@dataclass
class Solution:
    entity_list: Annotated[List[Entity], PlanningEntityCollectionProperty]
    value_list: Annotated[List[Value], ProblemFactCollectionProperty, ValueRangeProvider]
    score: Annotated[SimpleScore, PlanningScore] = field(default=None)


def create_score_manager(constraint_provider):
    return SolutionManager.create(SolverFactory.create(
        SolverConfig(solution_class=Solution,
                     entity_class_list=[Entity],
                     score_director_factory_config=ScoreDirectorFactoryConfig(
                         constraint_provider_function=constraint_provider
                     ))))


def test_for_each():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .reward(SimpleScore.ONE)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)

    problem = Solution([entity_a, entity_b], [value_1])

    assert score_manager.explain(problem).score.score == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 1

    entity_b.value = value_1

    assert score_manager.explain(problem).score.score == 2


def test_filter_uni():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .filter(lambda e: e.value.number == 1)
            .reward(SimpleScore.ONE)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).score.score == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 1

    entity_b.value = value_2
    assert score_manager.explain(problem).score.score == 1

    entity_b.value = value_1
    assert score_manager.explain(problem).score.score == 2


def test_filter_bi():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity)
            .filter(lambda e1, e2: e1.value.number == 1 and e2.value.number == 2)
            .reward(SimpleScore.ONE)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).score.score == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 0

    entity_b.value = value_1
    assert score_manager.explain(problem).score.score == 0

    entity_b.value = value_2
    assert score_manager.explain(problem).score.score == 1


def test_filter_tri():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity)
            .join(Entity)
            .filter(lambda e1, e2, e3: e1.value.number == 1 and e2.value.number == 2 and e3.value.number == 3)
            .reward(SimpleScore.ONE)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')
    entity_c: Entity = Entity('C')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)

    problem = Solution([entity_a, entity_b, entity_c], [value_1, value_2, value_3])

    assert score_manager.explain(problem).score.score == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 0

    entity_b.value = value_2
    assert score_manager.explain(problem).score.score == 0

    entity_c.value = value_1
    assert score_manager.explain(problem).score.score == 0

    entity_c.value = value_3
    assert score_manager.explain(problem).score.score == 1


def test_filter_quad():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity)
            .join(Entity)
            .join(Entity)
            .filter(lambda e1, e2, e3, e4: e1.value.number == 1 and e2.value.number == 2 and e3.value.number == 3
                    and e4.value.number == 4)
            .reward(SimpleScore.ONE)
            .as_constraint('Count')
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

    assert score_manager.explain(problem).score.score == 0
    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 0

    entity_b.value = value_2
    assert score_manager.explain(problem).score.score == 0

    entity_c.value = value_3
    assert score_manager.explain(problem).score.score == 0

    entity_d.value = value_1
    assert score_manager.explain(problem).score.score == 0

    entity_d.value = value_4
    assert score_manager.explain(problem).score.score == 1


def test_join_uni():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity, Joiners.equal(lambda entity: entity.code))
            .filter(lambda e1, e2: e1 is not e2)
            .reward(SimpleScore.ONE, lambda e1, e2: e1.value.number * e2.value.number)
            .as_constraint('Count')
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

    assert score_manager.explain(problem).score.score == 0

    entity_a1.value = value_1
    entity_a2.value = value_1

    entity_b1.value = value_2
    entity_b2.value = value_2

    # 1 * 1 + 1 * 1 + 2 * 2 + 2 * 2
    assert score_manager.explain(problem).score.score == 10

    entity_a1.value = value_2
    entity_b1.value = value_1

    # 1 * 2 + 1 * 2 + 1 * 2 + 1 * 2
    assert score_manager.explain(problem).score.score == 8


def test_map():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .map(lambda e: e.value.number)
            .reward(SimpleScore.ONE, lambda v: v)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).score.score == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 1

    entity_b.value = value_1

    assert score_manager.explain(problem).score.score == 2

    entity_b.value = value_2

    assert score_manager.explain(problem).score.score == 3


def test_multi_map():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .map(lambda e: e.code, lambda e: e.value.number)
            .reward(SimpleScore.ONE, lambda c, v: len(c) + v)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('BB')

    value_1 = Value(10)
    value_2 = Value(20)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).score.score == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 11

    entity_b.value = value_1

    assert score_manager.explain(problem).score.score == 23

    entity_b.value = value_2

    assert score_manager.explain(problem).score.score == 33


def test_expand():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .expand(lambda e: e.value.number)
            .reward(SimpleScore.ONE, lambda e, v: v)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).score.score == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 1

    entity_b.value = value_1

    assert score_manager.explain(problem).score.score == 2

    entity_b.value = value_2

    assert score_manager.explain(problem).score.score == 3


def test_multi_expand():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .expand(lambda e: e.code, lambda e: e.value.number)
            .reward(SimpleScore.ONE, lambda e, c, v: len(c) + v)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('BB')

    value_1 = Value(10)
    value_2 = Value(20)

    problem = Solution([entity_a, entity_b], [value_1, value_2])

    assert score_manager.explain(problem).score.score == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 11

    entity_b.value = value_1

    assert score_manager.explain(problem).score.score == 23

    entity_b.value = value_2

    assert score_manager.explain(problem).score.score == 33


def test_concat():
    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .filter(lambda e: e.value.number == 1)
            .concat(constraint_factory.for_each(Entity).filter(lambda e: e.value.number == 2))
            .reward(SimpleScore.ONE)
            .as_constraint('Count')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)

    problem = Solution([entity_a, entity_b], [value_1, value_2, value_3])

    assert score_manager.explain(problem).score.score == 0

    entity_a.value = value_1

    assert score_manager.explain(problem).score.score == 1

    entity_b.value = value_2

    assert score_manager.explain(problem).score.score == 2

    entity_b.value = value_3

    assert score_manager.explain(problem).score.score == 1


def test_custom_indictments():
    @dataclass(unsafe_hash=True)
    class MyIndictment:
        code: str

    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .reward(SimpleScore.ONE, lambda e: e.value.number)
            .indict_with(lambda e: [MyIndictment(e.code), e.value.number])
            .as_constraint('my_package', 'Maximize value')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)

    entity_a.value = value_1
    entity_b.value = value_1

    problem = Solution([entity_a, entity_b], [value_1, value_2, value_3])

    indictments = score_manager.explain(problem).indictment_map
    a_indictment = indictments[MyIndictment('A')]
    b_indictment = indictments[MyIndictment('B')]
    value_indictment = indictments[1]

    assert a_indictment.indicted_object == MyIndictment('A')
    assert a_indictment.score.score == 1
    assert a_indictment.constraint_match_count == 1
    assert a_indictment.constraint_match_set == {
        ConstraintMatch(constraint_ref=ConstraintRef(package_name='my_package', constraint_name='Maximize value'),
                        justification=DefaultConstraintJustification(
                            facts=(entity_a,),
                            impact=a_indictment.score
                        ),
                        indicted_objects=(MyIndictment('A'), 1),
                        score=a_indictment.score)
    }

    assert b_indictment.indicted_object == MyIndictment('B')
    assert b_indictment.score.score == 1
    assert b_indictment.constraint_match_count == 1
    assert b_indictment.constraint_match_set == {
        ConstraintMatch(constraint_ref=ConstraintRef(package_name='my_package', constraint_name='Maximize value'),
                        justification=DefaultConstraintJustification(
                            facts=(entity_b,),
                            impact=b_indictment.score
                        ),
                        indicted_objects=(MyIndictment('B'), 1),
                        score=b_indictment.score)
    }

    assert value_indictment.indicted_object == 1
    assert value_indictment.score.score == 2
    assert value_indictment.constraint_match_count == 2
    assert value_indictment.constraint_match_set == {
        ConstraintMatch(constraint_ref=ConstraintRef(package_name='my_package', constraint_name='Maximize value'),
                        justification=DefaultConstraintJustification(
                            facts=(entity_a,),
                            impact=a_indictment.score
                        ),
                        indicted_objects=(MyIndictment('A'), 1),
                        score=a_indictment.score),
        ConstraintMatch(constraint_ref=ConstraintRef(package_name='my_package', constraint_name='Maximize value'),
                        justification=DefaultConstraintJustification(
                            facts=(entity_b,),
                            impact=b_indictment.score
                        ),
                        indicted_objects=(MyIndictment('B'), 1),
                        score=b_indictment.score)
    }


def test_custom_justifications():
    @dataclass(unsafe_hash=True)
    class MyJustification(ConstraintJustification):
        code: str
        score: SimpleScore

    @constraint_provider
    def define_constraints(constraint_factory: ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .reward(SimpleScore.ONE, lambda e: e.value.number)
            .justify_with(lambda e, score: MyJustification(e.code, score))
            .as_constraint('my_package', 'Maximize value')
        ]

    score_manager = create_score_manager(define_constraints)
    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)

    entity_a.value = value_1
    entity_b.value = value_3

    problem = Solution([entity_a, entity_b], [value_1, value_2, value_3])

    justifications = score_manager.explain(problem).get_justification_list()
    assert len(justifications) == 2
    assert MyJustification('A', SimpleScore.of(1)) in justifications
    assert MyJustification('B', SimpleScore.of(3)) in justifications

    justifications = score_manager.explain(problem).get_justification_list(MyJustification)
    assert len(justifications) == 2
    assert MyJustification('A', SimpleScore.of(1)) in justifications
    assert MyJustification('B', SimpleScore.of(3)) in justifications

    justifications = score_manager.explain(problem).get_justification_list(DefaultConstraintJustification)
    assert len(justifications) == 0


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
    'impactBigDecimal',
    'impactConfigurableBigDecimal',
    'impactConfigurableLong',
    'impactLong',
    'penalizeBigDecimal',
    'penalizeConfigurableBigDecimal',
    'penalizeConfigurableLong',
    'penalizeLong',
    'rewardBigDecimal',
    'rewardConfigurableBigDecimal',
    'rewardConfigurableLong',
    'rewardLong',
    '_handler',  # JPype handler field should be ignored
    # Unimplemented
    'toConnectedRanges',
    'toConnectedTemporalRanges',
    # These methods are deprecated
    'from_',
    'fromUnfiltered',
    'fromUniquePair',
    'forEachIncludingNullVars',
    'ifExistsIncludingNullVars',
    'ifNotExistsIncludingNullVars',
    'ifExistsOtherIncludingNullVars',
    'ifNotExistsOtherIncludingNullVars',
    'toCollection',
}


def test_has_all_methods():
    for python_type, java_type in ((UniConstraintStream, JavaUniConstraintStream),
                                   (BiConstraintStream, JavaBiConstraintStream),
                                   (TriConstraintStream, JavaTriConstraintStream),
                                   (QuadConstraintStream, JavaQuadConstraintStream),
                                   (UniConstraintBuilder, JavaUniConstraintBuilder),
                                   (BiConstraintBuilder, JavaBiConstraintBuilder),
                                   (TriConstraintBuilder, JavaTriConstraintBuilder),
                                   (QuadConstraintBuilder, JavaQuadConstraintBuilder),
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

        if missing:
            raise AssertionError(f'{python_type} is missing methods ({missing}) '
                                 f'from java_type ({java_type}).)')

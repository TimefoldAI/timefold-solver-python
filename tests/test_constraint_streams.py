import inspect
import re
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

@timefold.solver.problem_fact
class Value:
    def __init__(self, number):
        self.number = number


@timefold.solver.planning_entity
class Entity:
    def __init__(self, code, value=None):
        self.code = code
        self.value = value

    @timefold.solver.planning_variable(Value, ['value_range'])
    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value


@timefold.solver.planning_solution
class Solution:
    def __init__(self, entity_list, value_list, score=None):
        self.entity_list = entity_list
        self.value_list = value_list
        self.score = score

    @timefold.solver.planning_entity_collection_property(Entity)
    def get_entity_list(self):
        return self.entity_list

    def set_entity_list(self, entity_list):
        self.entity_list = entity_list

    @timefold.solver.problem_fact_collection_property(Value)
    @timefold.solver.value_range_provider('value_range')
    def get_value_list(self):
        return self.value_list

    def set_value_list(self, value_list):
        self.value_list = value_list

    @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


def create_score_manager(constraint_provider):
    return timefold.solver.score_manager_create(timefold.solver.solver_factory_create(timefold.solver.config.solver.SolverConfig()
                                                                                      .withSolutionClass(Solution)
                                                                                      .withEntityClasses(Entity)
                                                                                      .withConstraintProviderClass(constraint_provider)))


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

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 1

    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 2


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

    assert score_manager.explainScore(problem).getScore().score() == 0
    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 1

    entity_b.set_value(value_2)
    assert score_manager.explainScore(problem).getScore().score() == 1

    entity_b.set_value(value_1)
    assert score_manager.explainScore(problem).getScore().score() == 2


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

    assert score_manager.explainScore(problem).getScore().score() == 0
    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_b.set_value(value_1)
    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_b.set_value(value_2)
    assert score_manager.explainScore(problem).getScore().score() == 1


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

    assert score_manager.explainScore(problem).getScore().score() == 0
    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_b.set_value(value_2)
    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_c.set_value(value_1)
    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_c.set_value(value_3)
    assert score_manager.explainScore(problem).getScore().score() == 1


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

    assert score_manager.explainScore(problem).getScore().score() == 0
    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_b.set_value(value_2)
    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_c.set_value(value_3)
    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_d.set_value(value_1)
    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_d.set_value(value_4)
    assert score_manager.explainScore(problem).getScore().score() == 1


def test_join_uni():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .join(Entity, timefold.solver.constraint.Joiners.equal(lambda entity: entity.code))
            .filter(lambda e1, e2: e1 != e2)
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

    entity_a1.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_a1.set_value(value_1)
    entity_a2.set_value(value_1)

    entity_b1.set_value(value_2)
    entity_b2.set_value(value_2)

    # 1 * 1 + 1 * 1 + 2 * 2 + 2 * 2
    assert score_manager.explainScore(problem).getScore().score() == 10

    entity_a1.set_value(value_2)
    entity_b1.set_value(value_1)

    # 1 * 2 + 1 * 2 + 1 * 2 + 1 * 2
    assert score_manager.explainScore(problem).getScore().score() == 8


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

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 1

    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 2

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore().score() == 3


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

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 11

    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 23

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore().score() == 33


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

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 1

    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 2

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore().score() == 3


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

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 11

    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 23

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore().score() == 33


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

    assert score_manager.explainScore(problem).getScore().score() == 0

    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore().score() == 1

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore().score() == 2

    entity_b.set_value(value_3)

    assert score_manager.explainScore(problem).getScore().score() == 1


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
}

def test_camel_case_for_all_snake_case_methods():
    for class_type in (UniConstraintStream, BiConstraintStream, TriConstraintStream, QuadConstraintStream, Joiners,
                       ConstraintCollectors, ConstraintFactory):
        missing = []
        incorrect = []
        for function in inspect.getmembers(class_type, inspect.isfunction):
            # split underscore using split
            function_name = function[0]
            if function_name in ignored_python_functions:
                continue
            function_name_parts = function_name.split('_')

            # joining result
            camel_case_name = function_name_parts[0] + ''.join(ele.title() for ele in function_name_parts[1:])
            if not hasattr(class_type, camel_case_name):
                missing.append(camel_case_name)
            if getattr(class_type, camel_case_name) is not function[1]:
                incorrect.append(function)

        assert len(missing) == 0
        assert len(incorrect) == 0


def test_snake_case_for_all_camel_case_methods():
    for class_type in (UniConstraintStream, BiConstraintStream, TriConstraintStream, QuadConstraintStream, Joiners,
                       ConstraintCollectors, ConstraintFactory):
        missing = []
        incorrect = []
        for function in inspect.getmembers(class_type, inspect.isfunction):
            # split underscore using split
            function_name = function[0]
            if function_name in ignored_python_functions:
                continue
            snake_case_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', function_name)
            # change h_t_t_p -> http
            snake_case_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case_name).lower()

            if not hasattr(class_type, snake_case_name):
                missing.append(snake_case_name)
            if getattr(class_type, snake_case_name) is not function[1]:
                incorrect.append(function)

        assert len(missing) == 0
        assert len(incorrect) == 0


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
            if not hasattr(python_type, function_name):
                missing.append(function_name)

        assert len(missing) == 0

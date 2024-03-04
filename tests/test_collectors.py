import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint


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


def test_min():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .group_by(timefold.solver.constraint.ConstraintCollectors.min(lambda entity: entity.value.number))
                .reward('Min value', timefold.solver.score.SimpleScore.ONE, lambda min_value: min_value)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)


def test_max():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.max(lambda entity: entity.value.number))
            .reward('Max value', timefold.solver.score.SimpleScore.ONE, lambda max_value: max_value)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)


def test_sum():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.sum(lambda entity: entity.value.number))
            .reward('Sum value', timefold.solver.score.SimpleScore.ONE, lambda sum_value: sum_value)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(3)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(4)


def test_average():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.average(lambda entity: entity.value.number))
            .reward('Average value', timefold.solver.score.SimpleScore.ONE, lambda average_value: int(10 * average_value))
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(10)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(15)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(20)


def test_count():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .filter(lambda entity: entity.code[0] == 'A')
                .group_by(timefold.solver.constraint.ConstraintCollectors.count())
                .reward('Count value', timefold.solver.score.SimpleScore.ONE, lambda count: count)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a1: Entity = Entity('A1')
    entity_a2: Entity = Entity('A2')
    entity_b: Entity = Entity('B1')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a1, entity_a2, entity_b], [value_1, value_2])
    entity_a1.set_value(value_1)
    entity_a2.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)


def test_count_distinct():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.count_distinct(lambda entity: entity.value))
            .reward('Count distinct value', timefold.solver.score.SimpleScore.ONE, lambda count: count)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)


def test_to_consecutive_sequences():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.to_consecutive_sequences(
                lambda entity: entity.value.number))
            .flatten_last(lambda sequences: sequences.getConsecutiveSequences())
            .reward('squared sequence length', timefold.solver.score.SimpleScore.ONE,
                    lambda sequence: sequence.getCount() ** 2)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')
    entity_c: Entity = Entity('C')
    entity_d: Entity = Entity('D')
    entity_e: Entity = Entity('E')

    value_1 = Value(1)
    value_2 = Value(2)
    value_3 = Value(3)
    value_4 = Value(4)
    value_5 = Value(5)
    value_6 = Value(6)
    value_7 = Value(7)
    value_8 = Value(8)
    value_9 = Value(9)

    problem = Solution([entity_a, entity_b, entity_c, entity_d, entity_e],
                       [value_1, value_2, value_3, value_4, value_5,
                        value_6, value_7, value_8, value_9])

    entity_a.set_value(value_1)
    entity_b.set_value(value_3)
    entity_c.set_value(value_5)
    entity_d.set_value(value_7)
    entity_e.set_value(value_9)

    assert score_manager.explainScore(problem).getScore().score() == 5

    entity_a.set_value(value_1)
    entity_b.set_value(value_2)
    entity_c.set_value(value_3)
    entity_d.set_value(value_4)
    entity_e.set_value(value_5)

    assert score_manager.explainScore(problem).getScore().score() == 25

    entity_a.set_value(value_1)
    entity_b.set_value(value_2)
    entity_c.set_value(value_3)
    entity_d.set_value(value_5)
    entity_e.set_value(value_6)

    assert score_manager.explainScore(problem).getScore().score() == 13


def test_to_list():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.to_list(lambda entity: entity.value))
            .reward('list size', timefold.solver.score.SimpleScore.ONE, lambda values: len(values))
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)


def test_to_set():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.to_set(lambda entity: entity.value))
            .reward('set size', timefold.solver.score.SimpleScore.ONE, lambda values: len(values))
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)


def test_to_map():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.to_map(lambda entity: entity.code, lambda entity: entity.value.number))
            .filter(lambda entity_map: next(iter(entity_map['A'])) == 1)
            .reward('map at B', timefold.solver.score.SimpleScore.ONE, lambda entity_map: next(iter(entity_map['B'])))
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(0)


def test_to_sorted_set():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.to_sorted_set(lambda entity: entity.value.number))
            .reward('min', timefold.solver.score.SimpleScore.ONE, lambda values: next(iter(values)))
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)


def test_to_sorted_map():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.to_sorted_map(lambda entity: entity.code, lambda entity: entity.value.number))
            .filter(lambda entity_map: next(iter(entity_map['B'])) == 1)
            .reward('map at A', timefold.solver.score.SimpleScore.ONE, lambda entity_map: next(iter(entity_map['A'])))
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(1)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(0)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(0)

    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)


def test_conditionally():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.conditionally(lambda entity: entity.code[0] == 'A',
                                                                          timefold.solver.constraint.ConstraintCollectors.count()))
            .reward('Conditionally count value', timefold.solver.score.SimpleScore.ONE, lambda count: count)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a1: Entity = Entity('A1')
    entity_a2: Entity = Entity('A2')
    entity_b: Entity = Entity('B1')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a1, entity_a2, entity_b], [value_1, value_2])
    entity_a1.set_value(value_1)
    entity_a2.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)


def test_compose():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.compose(
                timefold.solver.constraint.ConstraintCollectors.min(lambda entity: entity.value.number),
                timefold.solver.constraint.ConstraintCollectors.max(lambda entity: entity.value.number),
                lambda a,b: (a,b)
            ))
            .reward('Max value', timefold.solver.score.SimpleScore.ONE, lambda min_max: min_max[0] + min_max[1] * 10)
            # min is in lower digit; max in upper digit
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(11)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(21)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(22)

def test_collect_and_then():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .group_by(timefold.solver.constraint.ConstraintCollectors.collect_and_then(
                timefold.solver.constraint.ConstraintCollectors.min(lambda entity: entity.value.number),
                lambda a: 2 * a
            ))
            .reward('Double min value', timefold.solver.score.SimpleScore.ONE, lambda twice_min: twice_min)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')
    entity_b: Entity = Entity('B')

    value_1 = Value(1)
    value_2 = Value(2)

    problem = Solution([entity_a, entity_b], [value_1, value_2])
    entity_a.set_value(value_1)
    entity_b.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_a.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(2)

    entity_b.set_value(value_2)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(4)


def test_flatten_last():
    @timefold.solver.constraint_provider
    def define_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            .map(lambda entity: (1, 2, 3))
            .flatten_last(lambda the_tuple: the_tuple)
            .reward('Count', timefold.solver.score.SimpleScore.ONE)
        ]

    score_manager = create_score_manager(define_constraints)

    entity_a: Entity = Entity('A')

    value_1 = Value(1)

    problem = Solution([entity_a], [value_1])
    entity_a.set_value(value_1)

    assert score_manager.explainScore(problem).getScore() == timefold.solver.score.SimpleScore.of(3)

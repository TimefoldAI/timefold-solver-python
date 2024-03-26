import timefold.solver
import timefold.solver.types
import timefold.solver.score
import timefold.solver.valuerange
import timefold.solver.config
import timefold.solver.constraint

from dataclasses import dataclass, field
from typing import Annotated, Optional, List


def test_solve_partial():
    @dataclass
    class Code:
        value: str

    @dataclass
    class Value:
        code: Code

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Code
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    def is_value_one(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return (constraint_factory.for_each(Entity)
                .filter(lambda e: e.value.code.value == 'v1')
                .reward('Value 1', timefold.solver.score.SimpleScore.ONE)
                )

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            is_value_one(constraint_factory)
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        values: Annotated[List[Value],
                          timefold.solver.ProblemFactCollectionProperty,
                          timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='3'
        )
    )

    e1 = Entity(Code('e1'))
    e2 = Entity(Code('e2'))
    e3 = Entity(Code('e3'))

    v1 = Value(Code('v1'))
    v2 = Value(Code('v2'))
    v3 = Value(Code('v3'))

    e1.value = v1
    e2.value = v2
    e3.value = v3

    problem = Solution([e1, e2, e3], [v1, v2, v3])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)

    assert solution.score.score() == 3
    assert solution.entities[0].value == v1
    assert solution.entities[1].value == v1
    assert solution.entities[2].value == v1


def test_solve_nullable():
    @dataclass
    class Code:
        value: str

    @dataclass
    class Value:
        code: Code

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Code
        value: Annotated[Optional[Value],
                         timefold.solver.PlanningVariable(allows_unassigned=True,
                                                          value_range_provider_refs=['value_range'])] = (
            field(default=None))

    def at_least_one_null(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return (constraint_factory.for_each_including_unassigned(Entity)
                                  .filter(lambda e: e.value is None)
                                  .group_by(timefold.solver.constraint.ConstraintCollectors.count())
                                  .filter(lambda count: count >= 1)
                                  .reward('At least one null variable', timefold.solver.score.HardSoftScore.ONE_SOFT)
                )

    def assign_to_v1(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return (constraint_factory.for_each_including_unassigned(Entity)
                                  .filter(lambda e: e.value is not None and e.value.code.value == 'v1')
                                  .group_by(timefold.solver.constraint.ConstraintCollectors.count())
                                  .filter(lambda count: count >= 1)
                                  .reward('At least one v1', timefold.solver.score.HardSoftScore.ONE_HARD)
                )

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            at_least_one_null(constraint_factory),
            assign_to_v1(constraint_factory)
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        values: Annotated[List[Value],
                          timefold.solver.ProblemFactCollectionProperty,
                          timefold.solver.ValueRangeProvider(id='value_range')]
        score: Annotated[timefold.solver.score.HardSoftScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='1hard/1soft'
        )
    )

    e1 = Entity(Code('e1'))
    e2 = Entity(Code('e2'))

    v1 = Value(Code('v1'))
    v2 = Value(Code('v2'))

    problem = Solution([e1, e2], [v1, v2])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)

    assert solution.score.hard_score() == 1
    assert solution.score.soft_score() == 1
    assert solution.entities[0].value == v1 or solution.entities[0].value is None
    assert solution.entities[1].value == v1 or solution.entities[1].value is None


def test_solve_typed():
    @dataclass
    class Code:
        value: str

    @dataclass
    class Value:
        code: Code

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Code
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    def assign_to_v1(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return (constraint_factory.for_each(Entity)
                .filter(lambda e: e.value.code.value == 'v1')
                .reward('assign to v1', timefold.solver.score.SimpleScore.ONE)
                )

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            assign_to_v1(constraint_factory)
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        values: Annotated[List[Value],
                          timefold.solver.ProblemFactCollectionProperty,
                          timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='2'
        )
    )

    e1 = Entity(Code('e1'))
    e2 = Entity(Code('e2'))

    v1 = Value(Code('v1'))
    v2 = Value(Code('v2'))

    problem = Solution([e1, e2], [v1, v2])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)

    assert solution.score.score() == 2
    assert solution.entities[0].value == v1
    assert solution.entities[1].value == v1


def test_solve_complex_problem_facts():
    from abc import abstractmethod

    class BaseValue:
        @abstractmethod
        def get_id(self) -> str:
            raise NotImplementedError('Calling function on abstract base class')

        @abstractmethod
        def __str__(self) -> str:
            raise NotImplementedError('Calling function on abstract base class')

    @dataclass
    class ExpiringValue(BaseValue):
        name: str
        id: Annotated[str, timefold.solver.PlanningId]
        expiration_date: float

        def get_id(self) -> str:
            return self.id

        def __str__(self) -> str:
            return f'ExpiringValue(id={self.id}, name={self.name})'

    @dataclass
    class SimpleValue(BaseValue):
        name: str
        id: Annotated[str, timefold.solver.PlanningId]

        def get_id(self) -> str:
            return self.id

        def __str__(self) -> str:
            return f'SimpleValue(id={str(self.id)}, name={str(self.name)})'

    class NullValue(BaseValue):
        name: str
        id: Annotated[str, timefold.solver.PlanningId]

        def get_id(self) -> str:
            return self.id

        def __str__(self) -> str:
            return f'NullValue(id={str(self.id)}, name={str(self.name)})'

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        id: Annotated[str, timefold.solver.PlanningId]
        list_of_suitable_values: List[BaseValue]
        start_time: int
        end_time: int
        value: Annotated[Optional[BaseValue],
                         timefold.solver.PlanningVariable(value_range_provider_refs=['value_range'])] = (
            field(default=None))

        def get_allowable_values(self) -> Annotated[List[BaseValue],
                                                    timefold.solver.ValueRangeProvider(id='value_range')]:
            return self.list_of_suitable_values

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        score: Annotated[timefold.solver.score.HardSoftScore, timefold.solver.PlanningScore] = field(default=None)

    def is_present(r: Optional[BaseValue]) -> bool:
        if isinstance(r, NullValue):
            return False
        elif isinstance(r, BaseValue):
            return True
        else:
            return False

    def simultaneous_values(constraint_factory):
        return (
            constraint_factory.for_each_unique_pair(
                Entity,
                # ... if they support overlapping times
                (timefold.solver.constraint.Joiners.overlapping(lambda entity: entity.start_time,
                                                                lambda entity: entity.end_time)),
            )
            .filter(
                lambda entity_1, entity_2: (is_present(entity_1.value)
                                            and is_present(entity_2.value)
                                            and entity_1.value.get_id() == entity_2.value.get_id())
            )
            # Then penalize it!
            .penalize("Simultaneous values", timefold.solver.score.HardSoftScore.ONE_HARD)
        )

    def empty_value(constraint_factory):
        return (
            constraint_factory.for_each(Entity)
            .filter(lambda entity: not is_present(entity.value))
            .penalize("Prefer present value", timefold.solver.score.HardSoftScore.ONE_SOFT)
        )

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            simultaneous_values(constraint_factory),
            empty_value(constraint_factory)
        ]

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0hard/0soft'
        )
    )

    v1 = ExpiringValue('expiring', '0', 2.0)
    v2 = SimpleValue('simple', '1')
    v3 = NullValue()

    e1 = Entity('e1', [v1, v2], 0, 2)
    e2 = Entity('e2', [v1, v3], 1, 3)

    problem = Solution([e1, e2])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)

    assert solution.score.getHardScore() == 0
    assert solution.score.getSoftScore() == 0
    assert solution.entity_list[0].value == v2
    assert solution.entity_list[1].value == v1


def test_single_property():
    @dataclass
    class Value:
        code: str

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: str
        value: Annotated[str, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                              .join(Value,
                                    timefold.solver.constraint.Joiners.equal(lambda entity: entity.value,
                                                                    lambda value: value.code))
                              .reward('Same as value', timefold.solver.score.SimpleScore.ONE),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity: Annotated[Entity, timefold.solver.PlanningEntityProperty]
        value: Annotated[Value, timefold.solver.ProblemFactProperty]
        value_range: Annotated[List[str], timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='1'
        )
    )

    problem: Solution = Solution(Entity('A'), Value('1'), ['1', '2', '3'])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == 1
    assert solution.entity.value == '1'


def test_constraint_stream_in_join():
    @dataclass
    class Value:
        code: int

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: str
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .filter(lambda e: e.code == 'A')
                .join(constraint_factory.for_each(Entity).filter(lambda e: e.code == 'B'))
                .join(constraint_factory.for_each(Entity).filter(lambda e: e.code == 'C'))
                .join(constraint_factory.for_each(Entity).filter(lambda e: e.code == 'D'))
                .group_by(timefold.solver.constraint.ConstraintCollectors.sum(lambda a, b, c, d: a.value.code + b.value.code +
                                                                                        c.value.code + d.value.code))
                .reward('First Four Entities', timefold.solver.score.SimpleScore.ONE, lambda the_sum: the_sum),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        value_list: Annotated[List[Value],
                              timefold.solver.ProblemFactCollectionProperty,
                              timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        )
    )

    entity_1, entity_2, entity_3, entity_4, entity_5 = Entity('A'), Entity('B'), Entity('C'), Entity('D'), Entity('E')
    value_1, value_2, value_3 = Value(1), Value(2), Value(3)
    problem = Solution([entity_1, entity_2, entity_3, entity_4, entity_5], [value_1, value_2, value_3])
    score_manager = timefold.solver.SolutionManager.create(timefold.solver.SolverFactory.create(solver_config))

    entity_1.value = value_1
    entity_2.value = value_1
    entity_3.value = value_1
    entity_4.value = value_1
    entity_5.value = value_1

    assert score_manager.update(problem).score() == 4

    entity_5.value = value_2

    assert score_manager.update(problem).score() == 4

    entity_1.value = value_2
    assert score_manager.update(problem).score() == 5

    entity_2.value = value_2
    assert score_manager.update(problem).score() == 6

    entity_3.value = value_2
    assert score_manager.update(problem).score() == 7

    entity_4.value = value_2
    assert score_manager.update(problem).score() == 8

    entity_1.value = value_3
    assert score_manager.update(problem).score() == 9


def test_tuple_group_by_key():
    @dataclass(eq=False)
    class Value:
        code: str

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: str
        value: Annotated[str, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .join(Value,
                      timefold.solver.constraint.Joiners.equal(lambda entity: entity.value,
                                                      lambda value: value.code))
                .group_by(lambda entity, value: (0, value), timefold.solver.constraint.ConstraintCollectors.count_bi())
                .reward('Same as value', timefold.solver.score.SimpleScore.ONE, lambda _, count: count),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        value_list: Annotated[List[Value], timefold.solver.ProblemFactCollectionProperty]
        value_range: Annotated[List[str], timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    entity_list = [Entity('A0'), Entity('B0'), Entity('C0'),
                   Entity('A1'), Entity('B1'), Entity('C1'),
                   Entity('A2'), Entity('B2'), Entity('C2'),
                   Entity('A3'), Entity('B3'), Entity('C3'),
                   Entity('A4'), Entity('B4'), Entity('C4'),
                   Entity('A5'), Entity('B5'), Entity('C5'),
                   Entity('A6'), Entity('B6'), Entity('C6'),
                   Entity('A7'), Entity('B7'), Entity('C7'),
                   Entity('A8'), Entity('B8'), Entity('C8'),
                   Entity('A9'), Entity('B9'), Entity('C9')]

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit=str(len(entity_list))
        )
    )

    problem: Solution = Solution(entity_list,
                                 [Value('1')],
                                 ['1', '2', '3'])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == len(entity_list)
    for entity in solution.entity_list:
        assert entity.value == '1'


def test_python_object():
    import ctypes
    pointer1 = ctypes.c_void_p(1)
    pointer2 = ctypes.c_void_p(2)
    pointer3 = ctypes.c_void_p(3)

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: str
        value: Annotated[ctypes.c_void_p, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .filter(lambda entity: entity.value == pointer1)
                .reward('Same as value', timefold.solver.score.SimpleScore.ONE),
            constraint_factory.for_each(Entity)
                .group_by(lambda entity: entity.value.value, timefold.solver.constraint.ConstraintCollectors.count())
                .reward('Entity have same value', timefold.solver.score.SimpleScore.ONE, lambda value, count: count * count),
            constraint_factory.for_each(Entity)
                .group_by(lambda entity: (entity.code, entity.value.value))
                .join(Entity,
                      timefold.solver.constraint.Joiners.equal(lambda pair: pair[0], lambda entity: entity.code),
                      timefold.solver.constraint.Joiners.equal(lambda pair: pair[1], lambda entity: entity.value.value))
                .reward('Entity for pair', timefold.solver.score.SimpleScore.ONE),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity: Annotated[Entity, timefold.solver.PlanningEntityProperty]
        value_range: Annotated[List[ctypes.c_void_p], timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='3'
        )
    )
    problem: Solution = Solution(Entity('A'), [pointer1, pointer2, pointer3])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == 3
    assert solution.entity.value is pointer1


def test_custom_planning_id():
    from uuid import UUID, uuid4
    id_1 = uuid4()
    id_2 = uuid4()
    id_3 = uuid4()

    @dataclass(unsafe_hash=True)
    class Value:
        code: str

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Annotated[UUID, timefold.solver.PlanningId]
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each_unique_pair(Entity,
                                                    timefold.solver.constraint.Joiners.equal(lambda entity: entity.value))
                .penalize('Same value', timefold.solver.score.SimpleScore.ONE),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        values: Annotated[List[Value],
                          timefold.solver.ProblemFactCollectionProperty,
                          timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0'
        )
    )

    entity_1 = Entity(id_1)
    entity_2 = Entity(id_2)
    entity_3 = Entity(id_3)

    value_1 = Value('A')
    value_2 = Value('B')
    value_3 = Value('C')
    problem: Solution = Solution([
        entity_1,
        entity_2,
        entity_3
    ], [
        value_1,
        value_2,
        value_3
    ])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == 0

    encountered = set()
    for entity in solution.entities:
        assert entity.value not in encountered
        encountered.add(entity.value)


def test_custom_comparator():
    @dataclass(order=True, unsafe_hash=True)
    class Value:
        code: str

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Annotated[int, timefold.solver.PlanningId]
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
            # use less_than_or_equal and greater_than_or_equal since they require Comparable instances
            .if_exists_other(Entity, timefold.solver.constraint.Joiners.less_than_or_equal(lambda entity: entity.value),
                             timefold.solver.constraint.Joiners.greater_than_or_equal(lambda entity: entity.value))
            .penalize('Same value', timefold.solver.score.SimpleScore.ONE),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        values: Annotated[List[Value],
                          timefold.solver.ProblemFactCollectionProperty,
                          timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0'
        )
    )

    entity_1 = Entity(0)
    entity_2 = Entity(1)
    entity_3 = Entity(2)

    value_1 = Value('A')
    value_2 = Value('B')
    value_3 = Value('C')
    problem: Solution = Solution([
        entity_1,
        entity_2,
        entity_3
    ], [
        value_1,
        value_2,
        value_3
    ])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == 0

    encountered = set()
    for entity in solution.entities:
        assert entity.value not in encountered
        encountered.add(entity.value)


def test_custom_equals():
    @dataclass(eq=True, unsafe_hash=True)
    class Code:
        code: str

    @dataclass
    class Value:
        code: Code

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Annotated[int, timefold.solver.PlanningId]
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each_unique_pair(Entity,
                                                    timefold.solver.constraint.Joiners.equal(lambda entity: entity.value.code))
            .penalize('Same value', timefold.solver.score.SimpleScore.ONE)
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        values: Annotated[List[Value],
                          timefold.solver.ProblemFactCollectionProperty,
                          timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='-1'
        )
    )

    value_1a = Value(Code('A'))
    value_1b = Value(Code('A'))
    value_2a = Value(Code('B'))

    entity_1 = Entity(0, value_1a)
    entity_2 = Entity(1, value_1b)
    entity_3 = Entity(2, value_2a)
    problem: Solution = Solution([
        entity_1,
        entity_2,
        entity_3
    ], [
        value_1a,
        value_1b,
        value_2a,
    ])
    score_manager = timefold.solver.SolutionManager.create(timefold.solver.SolverFactory.create(solver_config))
    score = score_manager.update(problem)
    assert score.score() == -1


def test_entity_value_range_provider():
    @dataclass(unsafe_hash=True)
    class Value:
        code: str

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Annotated[str, timefold.solver.PlanningId]
        possible_values: List[Value]
        value: Annotated[Value, timefold.solver.PlanningVariable(value_range_provider_refs=['value_range'])] = (
            field(default=None))

        def get_possible_values(self) -> Annotated[List[Value], timefold.solver.ValueRangeProvider(id='value_range')]:
            return self.possible_values

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each_unique_pair(Entity,
                                                    timefold.solver.constraint.Joiners.equal(lambda entity: entity.value))
            .reward('Same value', timefold.solver.score.SimpleScore.ONE),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0'
        )
    )

    value_1 = Value('A')
    value_2 = Value('B')
    value_3 = Value('C')

    entity_1 = Entity('1', [value_1])
    entity_2 = Entity('2', [value_2])
    entity_3 = Entity('3', [value_3])


    problem: Solution = Solution([
        entity_1,
        entity_2,
        entity_3
    ])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == 0

    encountered = set()
    for entity in solution.entities:
        assert entity.value not in encountered
        encountered.add(entity.value)


def test_int_value_range_provider():
    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Annotated[str, timefold.solver.PlanningId]
        actual_value: int
        value: Annotated[int, timefold.solver.PlanningVariable(value_range_provider_refs=['value_range'])]\
            = field(default=None)
        possible_values: Annotated[timefold.solver.valuerange.CountableValueRange,
        timefold.solver.ValueRangeProvider(id='value_range')] = field(init=False)

        def __post_init__(self):
            self.possible_values = timefold.solver.valuerange.ValueRangeFactory.create_int_value_range(self.actual_value,
                                                                                                       self.actual_value + 1)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each_unique_pair(Entity,
                                                    timefold.solver.constraint.Joiners.equal(lambda entity: entity.value))
            .reward('Same value', timefold.solver.score.SimpleScore.ONE),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entities: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0'
        )
    )

    entity_1 = Entity('1', 1)
    entity_2 = Entity('2', 2)
    entity_3 = Entity('3', 3)


    problem: Solution = Solution([
        entity_1,
        entity_2,
        entity_3
    ])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == 0

    encountered = set()
    for entity in solution.entities:
        assert entity.value not in encountered
        encountered.add(entity.value)


def test_list_variable():
    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: str
        value: Annotated[List[int], timefold.solver.PlanningListVariable] = field(default_factory=list)

    def count_mismatches(entity):
        mismatches = 0
        for index in range(len(entity.value)):
            if entity.value[index] != index + 1:
                mismatches += 1
        return mismatches

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .filter(lambda entity: any(entity.value[index] != index + 1 for index in range(len(entity.value))))
                .penalize('Value is not the same as index', timefold.solver.score.SimpleScore.ONE, count_mismatches),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity: Annotated[Entity, timefold.solver.PlanningEntityProperty]
        value_range: Annotated[List[int], timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0'
        )
    )
    problem: Solution = Solution(Entity('A'), [1, 2, 3])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.score() == 0
    assert solution.entity.value == [1, 2, 3]

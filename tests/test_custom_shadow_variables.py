from typing import Annotated, Optional, List
from dataclasses import dataclass, field

import timefold.solver
from timefold.solver.annotations import *
import timefold.solver.constraint
import timefold.solver.score
import timefold.solver.config
# from timefold.solver import ScoreDirector


def test_custom_shadow_variable():
    @timefold.solver.variable_listener
    class MyVariableListener:
        def afterVariableChanged(self, score_director, entity):
            score_director.beforeVariableChanged(entity, 'value_squared')
            if entity.value is None:
                entity.value_squared = None
            else:
                entity.value_squared = entity.value ** 2
            score_director.afterVariableChanged(entity, 'value_squared')

        def beforeVariableChanged(self, score_director, entity):
            pass

        def beforeEntityAdded(self, score_director, entity):
            pass

        def afterEntityAdded(self, score_director, entity):
            pass

        def beforeEntityRemoved(self, score_director, entity):
            pass

        def afterEntityRemoved(self, score_director, entity):
            pass

    @timefold.solver.planning_entity
    @dataclass
    class MyPlanningEntity:
        value: Annotated[Optional[int], timefold.solver.PlanningVariable]\
            = field(default=None)
        value_squared: Annotated[Optional[int],
                        timefold.solver.ShadowVariable(variable_listener_class=MyVariableListener,
                                                       source_variable_name='value')] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(MyPlanningEntity)
                .filter(lambda entity: entity.value is None)
                .penalize('Unassigned value', timefold.solver.score.HardSoftScore.ONE_HARD),
            constraint_factory.for_each(MyPlanningEntity)
                .filter(lambda entity: entity.value is not None and entity.value * 2 == entity.value_squared)
                .reward('Double value is value squared', timefold.solver.score.HardSoftScore.ONE_SOFT)
        ]

    @timefold.solver.planning_solution
    @dataclass
    class MySolution:
        entity_list: Annotated[List[MyPlanningEntity], timefold.solver.PlanningEntityCollectionProperty]
        value_list: Annotated[List[int], timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.HardSoftScore, timefold.solver.PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=MySolution,
        entity_class_list=[MyPlanningEntity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0hard/1soft'
        )
    )

    solver_factory = timefold.solver.SolverFactory.create(solver_config)
    solver = solver_factory.build_solver()
    problem = MySolution([MyPlanningEntity()], [1, 2, 3])
    solution: MySolution = solver.solve(problem)
    assert solution.score.hard_score() == 0
    assert solution.score.soft_score() == 1
    assert solution.entity_list[0].value == 2
    assert solution.entity_list[0].value_squared == 4


def test_custom_shadow_variable_with_variable_listener_ref():
    @timefold.solver.variable_listener
    class MyVariableListener:
        def afterVariableChanged(self, score_director, entity):
            score_director.beforeVariableChanged(entity, 'twice_value')
            score_director.beforeVariableChanged(entity, 'value_squared')
            if entity.value is None:
                entity.twice_value = None
                entity.value_squared = None
            else:
                entity.twice_value = 2 * entity.value
                entity.value_squared = entity.value ** 2
            score_director.afterVariableChanged(entity, 'value_squared')
            score_director.afterVariableChanged(entity, 'twice_value')

        def beforeVariableChanged(self, score_director, entity):
            pass

        def beforeEntityAdded(self, score_director, entity):
            pass

        def afterEntityAdded(self, score_director, entity):
            pass

        def beforeEntityRemoved(self, score_director, entity):
            pass

        def afterEntityRemoved(self, score_director, entity):
            pass

    @timefold.solver.planning_entity
    @dataclass
    class MyPlanningEntity:
        value: Annotated[Optional[int], timefold.solver.PlanningVariable] = \
               field(default=None)
        value_squared: Annotated[Optional[int], timefold.solver.ShadowVariable(
            variable_listener_class=MyVariableListener, source_variable_name='value')] = field(default=None)
        # TODO: Use PiggyBackShadowVariable
        twice_value: Annotated[Optional[int], timefold.solver.ShadowVariable(
            variable_listener_class=MyVariableListener, source_variable_name='value')] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(MyPlanningEntity)
            .filter(lambda entity: entity.value is None)
            .penalize('Unassigned value', timefold.solver.score.HardSoftScore.ONE_HARD),
            constraint_factory.for_each(MyPlanningEntity)
            .filter(lambda entity: entity.twice_value == entity.value_squared)
            .reward('Double value is value squared', timefold.solver.score.HardSoftScore.ONE_SOFT)
        ]

    @timefold.solver.planning_solution
    @dataclass
    class MySolution:
        entity_list: Annotated[List[MyPlanningEntity], PlanningEntityCollectionProperty]
        value_list: Annotated[List[int], ValueRangeProvider]
        score: Annotated[timefold.solver.score.HardSoftScore, PlanningScore] = field(default=None)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=MySolution,
        entity_class_list=[MyPlanningEntity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0hard/1soft'
        )
    )

    solver_factory = timefold.solver.SolverFactory.create(solver_config)
    solver = solver_factory.build_solver()
    problem = MySolution([MyPlanningEntity()], [1, 2, 3])
    solution: MySolution = solver.solve(problem)
    assert solution.score.hard_score() == 0
    assert solution.score.soft_score() == 1
    assert solution.entity_list[0].value == 2
    assert solution.entity_list[0].value_squared == 4

import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint

from dataclasses import dataclass, field
from typing import Annotated, List


class BaseClass:
    pass


@timefold.solver.planning_entity
@dataclass
class InverseRelationEntity:
    code: str
    value: Annotated[BaseClass, timefold.solver.PlanningVariable(value_range_provider_refs=['value_range'])] = \
        field(default=None)

    def __hash__(self):
        return hash(self.code)


@timefold.solver.planning_entity
@dataclass
class InverseRelationValue(BaseClass):
    code: str
    entities: Annotated[List[InverseRelationEntity],
                        timefold.solver.InverseRelationShadowVariable(source_variable_name='value')] = \
        field(default_factory=list)


@timefold.solver.planning_solution
@dataclass
class InverseRelationSolution:
    values: Annotated[List[InverseRelationValue],
                      timefold.solver.PlanningEntityCollectionProperty,
                      timefold.solver.ValueRangeProvider(id='value_range')]
    entities: Annotated[List[InverseRelationEntity],
                        timefold.solver.PlanningEntityCollectionProperty]
    score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)


@timefold.solver.constraint_provider
def inverse_relation_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
    return [
        constraint_factory.for_each(InverseRelationValue)
                          .filter(lambda value: len(value.entities) > 1)
                          .penalize('Only one entity per value', timefold.solver.score.SimpleScore.ONE)
    ]


def test_inverse_relation():
    solver_config = timefold.solver.config.SolverConfig(
        solution_class=InverseRelationSolution,
        entity_class_list=[InverseRelationEntity, InverseRelationValue],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=inverse_relation_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0'
        )
    )
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(InverseRelationSolution(
        [
            InverseRelationValue('A'),
            InverseRelationValue('B'),
            InverseRelationValue('C')
        ],
        [
            InverseRelationEntity('1'),
            InverseRelationEntity('2'),
            InverseRelationEntity('3'),
        ]
    ))
    assert solution.score.score() == 0
    visited_set = set()
    for value in solution.values:
        assert len(value.entities) == 1
        assert value.entities[0] is not None
        assert value.entities[0] not in visited_set
        visited_set.add(value.entities[0])

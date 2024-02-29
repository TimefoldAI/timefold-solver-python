import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint


@timefold.solver.planning_entity
class InverseRelationEntity:
    def __init__(self, code, value=None):
        self.code = code
        self.value = value

    @timefold.solver.planning_variable(object, ['value_range'])
    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value


@timefold.solver.planning_entity
class InverseRelationValue:
    def __init__(self, code, entities=None):
        self.code = code
        if entities is None:
            self.entities = []
        else:
            self.entities = entities

    @timefold.solver.inverse_relation_shadow_variable(InverseRelationEntity, source_variable_name='value')
    def get_entities(self):
        return self.entities

    def set_entities(self, entities):
        self.entities = entities


@timefold.solver.planning_solution
class InverseRelationSolution:
    def __init__(self, values, entities, score=None):
        self.values = values
        self.entities = entities
        self.score = score

    @timefold.solver.planning_entity_collection_property(InverseRelationEntity)
    def get_entities(self):
        return self.entities

    @timefold.solver.planning_entity_collection_property(InverseRelationValue)
    @timefold.solver.value_range_provider('value_range')
    def get_values(self):
        return self.values

    @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


@timefold.solver.constraint_provider
def inverse_relation_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
    return [
        constraint_factory.for_each(InverseRelationValue)
                          .filter(lambda value: len(value.entities) > 1)
                          .penalize('Only one entity per value', timefold.solver.score.SimpleScore.ONE)
    ]


def test_inverse_relation():
    termination = timefold.solver.config.solver.termination.TerminationConfig()
    termination.setBestScoreLimit('0')
    solver_config = timefold.solver.config.solver.SolverConfig() \
        .withSolutionClass(InverseRelationSolution) \
        .withEntityClasses(InverseRelationEntity, InverseRelationValue) \
        .withConstraintProviderClass(inverse_relation_constraints) \
        .withTerminationConfig(termination)
    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
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
    assert solution.score.getScore() == 0
    visited_set = set()
    for value in solution.values:
        assert len(value.entities) == 1
        assert value.entities[0] is not None
        assert value.entities[0] not in visited_set
        visited_set.add(value.entities[0])

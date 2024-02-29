import pathlib
import pytest
import re
import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint


@timefold.solver.planning_entity
class Entity:
    def __init__(self, code, value=None):
        self.code = code
        self.value = value

    @timefold.solver.planning_variable(str, value_range_provider_refs=['value_range'])
    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value


@timefold.solver.problem_fact
class Value:
    def __init__(self, code):
        self.code = code


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
class Solution:
    def __init__(self, entity, value, value_range, score=None):
        self.entity = entity
        self.value = value
        self.value_range = value_range
        self.score = score

    @timefold.solver.planning_entity_property(Entity)
    def get_entity(self):
        return self.entity

    @timefold.solver.problem_fact_property(Value)
    def get_value(self):
        return self.value

    @timefold.solver.problem_fact_collection_property(str)
    @timefold.solver.value_range_provider(range_id='value_range')
    def get_value_range(self):
        return self.value_range

    @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
    def get_score(self) -> timefold.solver.score.SimpleScore:
        return self.score

    def set_score(self, score):
        self.score = score


def test_load_from_solver_config_file():
    solver_config = timefold.solver.solver_config_create_from_xml_file(pathlib.Path('tests', 'solverConfig-simple.xml'))
    assert solver_config.getSolutionClass() == timefold.solver.get_class(Solution)
    entity_class_list = solver_config.getEntityClassList()
    assert entity_class_list.size() == 1
    assert entity_class_list.get(0) == timefold.solver.get_class(Entity)
    assert solver_config.getScoreDirectorFactoryConfig().getConstraintProviderClass() == \
           timefold.solver.get_class(my_constraints)
    assert solver_config.getTerminationConfig().getBestScoreLimit() == '0hard/0soft'


def test_reload_from_solver_config_file():
    @timefold.solver.planning_solution
    class RedefinedSolution:
        ...

    RedefinedSolution1 = RedefinedSolution
    solver_config_1 = timefold.solver.solver_config_create_from_xml_file(pathlib.Path('tests', 'solverConfig-redefined.xml'))

    @timefold.solver.planning_solution
    class RedefinedSolution:
        ...

    RedefinedSolution2 = RedefinedSolution
    solver_config_2 = timefold.solver.solver_config_create_from_xml_file(pathlib.Path('tests', 'solverConfig-redefined.xml'))

    assert solver_config_1.getSolutionClass() == timefold.solver.get_class(RedefinedSolution1)
    assert solver_config_2.getSolutionClass() == timefold.solver.get_class(RedefinedSolution2)


def test_cannot_find_solver_config_file():
    from java.lang import Thread
    current_thread = Thread.currentThread()
    thread_class_loader = current_thread.getContextClassLoader()
    with pytest.raises(FileNotFoundError, match=re.escape("Unable to find SolverConfig file (does-not-exist.xml).")):
        timefold.solver.solver_config_create_from_xml_file(pathlib.Path('does-not-exist.xml'))
    assert current_thread.getContextClassLoader() == thread_class_loader

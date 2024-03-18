import pathlib
import pytest
import re
import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint

from dataclasses import dataclass, field
from typing import Annotated, List


class Value:
    def __init__(self, code):
        self.code = code


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
class Solution:
    entity: Annotated[Entity, timefold.solver.PlanningEntityProperty]
    value: Annotated[Value, timefold.solver.ProblemFactProperty]
    value_range: Annotated[List[str], timefold.solver.ValueRangeProvider]
    score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore]


def get_java_solver_config(path: pathlib.Path):
    return timefold.solver.SolverConfig.create_from_xml_resource(path)._to_java_solver_config()


def test_load_from_solver_config_file():
    solver_config = get_java_solver_config(pathlib.Path('tests', 'solverConfig-simple.xml'))
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
    solver_config_1 = get_java_solver_config(pathlib.Path('tests', 'solverConfig-redefined.xml'))

    @timefold.solver.planning_solution
    class RedefinedSolution:
        ...

    RedefinedSolution2 = RedefinedSolution
    solver_config_2 = get_java_solver_config(pathlib.Path('tests', 'solverConfig-redefined.xml'))

    assert solver_config_1.getSolutionClass() == timefold.solver.get_class(RedefinedSolution1)
    assert solver_config_2.getSolutionClass() == timefold.solver.get_class(RedefinedSolution2)


def test_cannot_find_solver_config_file():
    from java.lang import Thread
    current_thread = Thread.currentThread()
    thread_class_loader = current_thread.getContextClassLoader()
    with pytest.raises(FileNotFoundError, match=re.escape("The solverConfigFile (does-not-exist.xml) was not found.")):
        get_java_solver_config(pathlib.Path('does-not-exist.xml'))
    assert current_thread.getContextClassLoader() == thread_class_loader

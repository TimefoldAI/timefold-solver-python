import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint
from timefold.solver.types import Duration
import pytest
import re


@timefold.solver.planning_entity
class Entity:
    def __init__(self, value=None):
        self.value = value

    @timefold.solver.planning_variable(str, value_range_provider_refs=['value_range'])
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

    @timefold.solver.problem_fact_collection_property(str)
    @timefold.solver.value_range_provider(range_id='value_range')
    def get_value_list(self):
        return self.value_list

    @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


@timefold.solver.constraint_provider
def my_constraints(constraint_factory):
    return [
        constraint_factory.forEach(timefold.solver.get_class(Entity))
            .penalize('Penalize each entity', timefold.solver.score.SimpleScore.ONE, lambda entity: 'TEN')
    ]


def test_non_planning_solution_being_passed_to_solve():
    solver_config = timefold.solver.config.solver.SolverConfig()
    solver_config.withSolutionClass(Solution).withEntityClasses(Entity) \
        .withConstraintProviderClass(my_constraints)
    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
    with pytest.raises(ValueError, match=re.escape(
            f'A problem was not passed to solve (parameter problem was ({None})). Maybe '
            f'pass an instance of a class annotated with @planning_solution to solve?'
    )):
        solver.solve(None)


def test_non_problem_fact_being_passed_to_problem_fact_collection():
    with pytest.raises(ValueError, match=f"<class '.*MyClass'> is not a @problem_fact. Maybe decorate "
                                         f"<class '.*MyClass'> with @problem_fact?"):
        class MyClass:
            pass

        class MySolution:
            def __init__(self, my_class_list):
                self.my_class_list = my_class_list

            @timefold.solver.problem_fact_collection_property(MyClass)
            def get_my_class_list(self):
                return self.my_class_list


def test_none_passed_to_solve():
    solver_config = timefold.solver.config.solver.SolverConfig()
    solver_config.withSolutionClass(timefold.solver.get_class(Solution)).withEntityClasses(timefold.solver.get_class(Entity)) \
        .withConstraintProviderClass(my_constraints)
    problem = 10
    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
    with pytest.raises(ValueError, match=re.escape(
            f'The problem ({problem}) is not an instance of a @planning_solution class. '
            f'Maybe decorate the problem class ({type(problem)}) with @planning_solution?'
    )):
        solver.solve(10)


def test_bad_return_type():
    solver_config = timefold.solver.config.solver.SolverConfig()
    solver_config.withSolutionClass(timefold.solver.get_class(Solution)) \
        .withEntityClasses(Entity) \
        .withConstraintProviderClass(my_constraints) \
        .withTerminationSpentLimit(timefold.solver.types.Duration.ofSeconds(1))

    problem = Solution([Entity()], ['1', '2', '3'])
    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
    with pytest.raises(RuntimeError, match=r'An error occurred during solving. This can occur when.*'):
        solver.solve(problem)


def test_non_proxied_class_passed():
    class NonProxied:
        pass

    solver_config = timefold.solver.config.solver.SolverConfig()
    with pytest.raises(ValueError, match=re.escape(
            f'Type {NonProxied} does not have a Java class proxy. Maybe annotate it with '
            f'@problem_fact, @planning_entity, or @planning_solution?'
    )):
        solver_config.withSolutionClass(NonProxied)


def test_non_proxied_function_passed():
    def not_proxied():
        pass

    solver_config = timefold.solver.config.solver.SolverConfig()
    with pytest.raises(ValueError, match=re.escape(
            f'Function {not_proxied} does not have a Java class proxy. Maybe annotate it with '
            f'@constraint_provider?')):
        solver_config.withConstraintProviderClass(not_proxied)

import pytest
import timefold.solver
import timefold.solver.types
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint

from dataclasses import dataclass, field
from typing import Annotated, List


def test_solve():
    from threading import Lock, Semaphore
    from timefold.solver import SolverStatus
    lock = Lock()

    def get_lock(entity):
        lock.acquire()
        lock.release()
        return False

    @dataclass
    class Value:
        value: Annotated[int, timefold.solver.PlanningId]

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Annotated[str, timefold.solver.PlanningId]
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .filter(get_lock)
                .reward('Wait for lock', timefold.solver.score.SimpleScore.ONE),
            constraint_factory.for_each(Entity)
                .reward('Maximize Value', timefold.solver.score.SimpleScore.ONE, lambda entity: entity.value.value),
            constraint_factory.for_each_unique_pair(Entity,
                                                    timefold.solver.constraint.Joiners.equal(lambda entity: entity.value.value))
                .penalize('Same Value', timefold.solver.score.SimpleScore.of(12)),
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        value_list: Annotated[List[Value],
                              timefold.solver.DeepPlanningClone,
                              timefold.solver.ProblemFactCollectionProperty,
                              timefold.solver.ValueRangeProvider]
        score: Annotated[timefold.solver.score.SimpleScore, timefold.solver.PlanningScore] = field(default=None)

    # TODO: Support problem changes
    # @timefold.solver.problem_change
    # class UseOnlyEntityAndValueProblemChange:
    #     def __init__(self, entity, value):
    #         self.entity = entity
    #         self.value = value
    #
    #     def doChange(self, solution: Solution, problem_change_director: timefold.solver.types.ProblemChangeDirector):
    #         problem_facts_to_remove = solution.value_list.copy()
    #         entities_to_remove = solution.entity_list.copy()
    #         for problem_fact in problem_facts_to_remove:
    #             problem_change_director.removeProblemFact(problem_fact,
    #                                                       lambda value: solution.value_list.remove(problem_fact))
    #         for removed_entity in entities_to_remove:
    #             problem_change_director.removeEntity(removed_entity,
    #                                                  lambda entity: solution.entity_list.remove(removed_entity))
    #         problem_change_director.addEntity(self.entity, lambda entity: solution.entity_list.append(entity))
    #         problem_change_director.addProblemFact(self.value, lambda value: solution.value_list.append(value))

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Entity],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            constraint_provider_function=my_constraints
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='6'
        )
    )
    problem: Solution = Solution([Entity('A'), Entity('B'), Entity('C')], [Value(1), Value(2), Value(3)],
                                 timefold.solver.score.SimpleScore.ONE)

    def assert_solver_run(solver_manager, solver_job):
        assert solver_manager.get_solver_status(1) != SolverStatus.NOT_SOLVING
        lock.release()
        solution = solver_job.get_final_best_solution()
        assert solution.score.score() == 6
        value_list = [entity.value.value for entity in solution.entity_list]
        assert 1 in value_list
        assert 2 in value_list
        assert 3 in value_list
        assert solver_manager.get_solver_status(1) == SolverStatus.NOT_SOLVING

    # def assert_problem_change_solver_run(solver_manager, solver_job):
    #     assert solver_manager.get_solver_status(1) != SolverStatus.NOT_SOLVING
    #     solver_manager.addProblemChange(1, UseOnlyEntityAndValueProblemChange(Entity('D'), Value(6)))
    #     lock.release()
    #     solution = solver_job.get_final_best_solution()
    #     assert solution.score.score() == 6
    #     assert len(solution.entity_list) == 1
    #     assert len(solution.value_range) == 1
    #     assert solution.entity_list[0].code == 'D'
    #     assert solution.entity_list[0].value.value == 6
    #     assert solution.value_range[0].value == 6
    #     assert solver_manager.get_solver_status(1) == SolverStatus.NOT_SOLVING

    with timefold.solver.SolverManager.create(timefold.solver.SolverFactory.create(solver_config)) as solver_manager:
        lock.acquire()
        solver_job = solver_manager.solve(1, problem)
        assert_solver_run(solver_manager, solver_job)

        # lock.acquire()
        # solver_job = solver_manager.solve(1, problem)
        # assert_problem_change_solver_run(solver_manager, solver_job)

        def get_problem(problem_id):
            assert problem_id == 1
            return problem

        lock.acquire()
        solver_job = (solver_manager.solve_builder()
                      .with_problem_id(1)
                      .with_problem_finder(get_problem)).run()
        assert_solver_run(solver_manager, solver_job)

        # lock.acquire()
        #solver_job = solver_manager.solve(1, get_problem)
        #assert_problem_change_solver_run(solver_manager, solver_job)

        solution_list = []
        semaphore = Semaphore(0)

        def on_best_solution_changed(solution):
            solution_list.append(solution)
            semaphore.release()

        lock.acquire()
        solver_job = (solver_manager.solve_builder()
                      .with_problem_id(1)
                      .with_problem_finder(get_problem)
                      .with_best_solution_consumer(on_best_solution_changed)
                      ).run()
        assert_solver_run(solver_manager, solver_job)
        assert semaphore.acquire(timeout=1)
        assert len(solution_list) == 1

        # solution_list = []
        # lock.acquire()
        # solver_job = (solver_manager.solve_builder()
        #               .with_problem_id(1)
        #               .with_problem_finder(get_problem)
        #               .with_best_solution_consumer(on_best_solution_changed)
        #               ).run()
        #assert_problem_change_solver_run(solver_manager, solver_job)
        # assert len(solution_list) == 1

        solution_list = []
        lock.acquire()
        solver_job = (solver_manager.solve_builder()
                      .with_problem_id(1)
                      .with_problem_finder(get_problem)
                      .with_best_solution_consumer(on_best_solution_changed)
                      .with_final_best_solution_consumer(on_best_solution_changed)
                      ).run()
        assert_solver_run(solver_manager, solver_job)
        # Wait for 2 acquires, one for best solution consumer,
        # another for final best solution consumer
        assert semaphore.acquire(timeout=1)
        assert semaphore.acquire(timeout=1)
        assert len(solution_list) == 2

        # solution_list = []
        # lock.acquire()
        # solver_job = (solver_manager.solve_builder()
        #               .with_problem_id(1)
        #               .with_problem_finder(get_problem)
        #               .with_best_solution_consumer(on_best_solution_changed)
        #               .with_final_best_solution_consumer(on_best_solution_changed)
        #               ).run()
        # assert_problem_change_solver_run(solver_manager, solver_job)
        # assert len(solution_list) == 2


@pytest.mark.filterwarnings("ignore:.*Exception in thread.*:pytest.PytestUnhandledThreadExceptionWarning")
def test_error():
    @dataclass
    class Value:
        value: Annotated[int, timefold.solver.PlanningId]

    @timefold.solver.planning_entity
    @dataclass
    class Entity:
        code: Annotated[str, timefold.solver.PlanningId]
        value: Annotated[Value, timefold.solver.PlanningVariable] = field(default=None)

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                              .filter(lambda e: e.missing_attribute == 1)
                              .reward('Maximize Value', timefold.solver.score.SimpleScore.ONE, lambda entity: entity.value.value)
        ]

    @timefold.solver.planning_solution
    @dataclass
    class Solution:
        entity_list: Annotated[List[Entity], timefold.solver.PlanningEntityCollectionProperty]
        value_list: Annotated[List[Value],
                              timefold.solver.DeepPlanningClone,
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
            best_score_limit='6'
        )
    )
    problem: Solution = Solution([Entity('A'), Entity('B'), Entity('C')], [Value(1), Value(2), Value(3)],
                                 timefold.solver.score.SimpleScore.ONE)
    with timefold.solver.SolverManager.create(timefold.solver.SolverFactory.create(solver_config)) as solver_manager:
        the_problem_id = None
        the_exception = None

        def my_exception_handler(problem_id, exception):
            nonlocal the_problem_id
            nonlocal the_exception
            the_problem_id = problem_id
            the_exception = exception

        try:
            (solver_manager.solve_builder()
             .with_problem_id(1)
             .with_problem(problem)
             .with_exception_handler(my_exception_handler)
             .run().get_final_best_solution())
        except:
            pass

        assert the_problem_id == 1
        assert the_exception is not None

        the_problem_id = None
        the_exception = None

        try:
            (solver_manager.solve_builder()
             .with_problem_id(1)
             .with_problem(problem)
             .with_best_solution_consumer(lambda solution: None)
             .with_exception_handler(my_exception_handler)
             .run().get_final_best_solution())
        except:
            pass

        assert the_problem_id == 1
        assert the_exception is not None

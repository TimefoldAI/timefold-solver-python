import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint


def test_solver_events():
    @timefold.solver.planning_entity
    class Entity:
        def __init__(self, code, value=None):
            self.code = code
            self.value = value

        @timefold.solver.planning_variable(int, value_range_provider_refs=['value_range'])
        def get_value(self):
            return self.value

        def set_value(self, value):
            self.value = value

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory: timefold.solver.constraint.ConstraintFactory):
        return [
            constraint_factory.for_each(Entity)
                .reward('Maximize value', timefold.solver.score.SimpleScore.ONE, lambda entity: entity.value),
        ]

    @timefold.solver.planning_solution
    class Solution:
        def __init__(self, entity, value_range, score=None):
            self.entity = entity
            self.value_range = value_range
            self.score = score

        @timefold.solver.planning_entity_collection_property(Entity)
        def get_entity(self):
            return self.entity

        @timefold.solver.problem_fact_collection_property(int)
        @timefold.solver.value_range_provider(range_id='value_range')
        def get_value_range(self):
            return self.value_range

        @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
        def get_score(self) -> timefold.solver.score.SimpleScore:
            return self.score

        def set_score(self, score):
            self.score = score


    solver_config = timefold.solver.config.solver.SolverConfig()
    termination_config = timefold.solver.config.solver.termination.TerminationConfig()
    termination_config.setBestScoreLimit('6')
    solver_config.withSolutionClass(Solution) \
        .withEntityClasses(Entity) \
        .withConstraintProviderClass(my_constraints) \
        .withTerminationConfig(termination_config)

    problem: Solution = Solution([Entity('A'), Entity('B')], [1, 2, 3])
    score_list = []
    solution_list = []

    def on_best_solution_changed(event):
        solution_list.append(event.getNewBestSolution())
        score_list.append(event.getNewBestScore())

    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
    solver.addEventListener(on_best_solution_changed)
    solution = solver.solve(problem)


    assert solution.get_score().getScore() == 6
    assert solution.entity[0].value == 3
    assert solution.entity[1].value == 3
    assert len(score_list) == len(solution_list)
    assert len(solution_list) == 1
    assert score_list[0].getScore() == 6
    assert solution_list[0].get_score().getScore() == 6
    assert solution_list[0].entity[0].value == 3
    assert solution_list[0].entity[1].value == 3

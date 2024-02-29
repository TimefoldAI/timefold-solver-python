import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint


def test_easy_score_calculator():
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

    @timefold.solver.planning_solution
    class Solution:
        def __init__(self, entity_list, value_range, score=None):
            self.entity_list = entity_list
            self.value_range = value_range
            self.score = score

        @timefold.solver.planning_entity_collection_property(Entity)
        def get_entity_list(self):
            return self.entity_list

        @timefold.solver.problem_fact_collection_property(int)
        @timefold.solver.value_range_provider(range_id='value_range')
        def get_value_range(self):
            return self.value_range

        @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
        def get_score(self) -> timefold.solver.score.SimpleScore:
            return self.score

        def set_score(self, score):
            self.score = score

    @timefold.solver.easy_score_calculator
    def my_score_calculator(solution: Solution):
        total_score = 0
        for entity in solution.entity_list:
            total_score += 0 if entity.value is None else entity.value
        return timefold.solver.score.SimpleScore.of(total_score)

    solver_config = timefold.solver.config.solver.SolverConfig()
    termination_config = timefold.solver.config.solver.termination.TerminationConfig()
    termination_config.setBestScoreLimit('9')
    solver_config.withSolutionClass(timefold.solver.get_class(Solution)) \
        .withEntityClasses(Entity) \
        .withEasyScoreCalculatorClass(my_score_calculator) \
        .withTerminationConfig(termination_config)
    problem: Solution = Solution([Entity('A'), Entity('B'), Entity('C')], [1, 2, 3])
    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
    solution = solver.solve(problem)
    assert solution.get_score().getScore() == 9
    assert solution.entity_list[0].value == 3
    assert solution.entity_list[1].value == 3
    assert solution.entity_list[2].value == 3

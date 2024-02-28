import timefold.solver
import timefold.solver.score
import timefold.solver.config


def test_pinning_filter():
    def is_entity_pinned(_, entity):
        return entity.is_pinned()

    @timefold.solver.planning_entity(pinning_filter=is_entity_pinned)
    class Point:
        def __init__(self, value, is_pinned=False):
            self.value = value
            self.pinned = is_pinned

        def is_pinned(self):
            return self.pinned

        @timefold.solver.planning_variable(int, value_range_provider_refs=['value_range'])
        def get_value(self):
            return self.value

        def set_value(self, value):
            self.value = value

    @timefold.solver.planning_solution
    class Solution:
        def __init__(self, values, points):
            self.values = values
            self.points = points
            self.score = None

        @timefold.solver.problem_fact_collection_property(int)
        @timefold.solver.value_range_provider('value_range')
        def get_value_range(self):
            return self.values

        @timefold.solver.planning_entity_collection_property(Point)
        def get_points(self):
            return self.points

        @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
        def get_score(self) -> timefold.solver.score.SimpleScore:
            return self.score

        def set_score(self, score):
            self.score = score

    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory):
        return [
            constraint_factory.forEach(Point)
                              .penalize("Minimize Value", timefold.solver.score.SimpleScore.ONE, lambda point: point.value)
        ]

    termination_config = timefold.solver.config.solver.termination.TerminationConfig()
    termination_config.setUnimprovedSecondsSpentLimit(1)
    solver_config = timefold.solver.config.solver.SolverConfig() \
        .withSolutionClass(Solution) \
        .withEntityClasses(Point) \
        .withConstraintProviderClass(my_constraints) \
        .withTerminationConfig(termination_config)
    problem: Solution = Solution([0, 1, 2],
                                 [
                                     Point(0),
                                     Point(1),
                                     Point(2, is_pinned=True)
                                 ])
    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
    solution = solver.solve(problem)
    assert solution.get_score().getScore() == -2


def test_planning_pin():
    @timefold.solver.planning_entity
    class Point:
        def __init__(self, value, is_pinned=False):
            self.value = value
            self.pinned = is_pinned

        @timefold.solver.planning_pin
        def is_pinned(self):
            return self.pinned

        @timefold.solver.planning_variable(int, value_range_provider_refs=['value_range'])
        def get_value(self):
            return self.value

        def set_value(self, value):
            self.value = value

    @timefold.solver.planning_solution
    class Solution:
        def __init__(self, values, points):
            self.values = values
            self.points = points
            self.score = None

        @timefold.solver.problem_fact_collection_property(int)
        @timefold.solver.value_range_provider('value_range')
        def get_value_range(self):
            return self.values

        @timefold.solver.planning_entity_collection_property(Point)
        def get_points(self):
            return self.points

        @timefold.solver.planning_score(timefold.solver.score.SimpleScore)
        def get_score(self) -> timefold.solver.score.SimpleScore:
            return self.score

        def set_score(self, score):
            self.score = score


    @timefold.solver.constraint_provider
    def my_constraints(constraint_factory):
        return [
            constraint_factory.for_each(Point)
                .penalize("Minimize Value", timefold.solver.score.SimpleScore.ONE, lambda point: point.value)
        ]

    termination_config = timefold.solver.config.solver.termination.TerminationConfig()
    termination_config.setUnimprovedSecondsSpentLimit(1)
    solver_config = timefold.solver.config.solver.SolverConfig() \
        .withSolutionClass(Solution) \
        .withEntityClasses(Point) \
        .withConstraintProviderClass(my_constraints) \
        .withTerminationConfig(termination_config)
    problem: Solution = Solution([0, 1, 2],
                                 [
                                     Point(0),
                                     Point(1),
                                     Point(2, is_pinned=True)
                                 ])
    solver = timefold.solver.solver_factory_create(solver_config).buildSolver()
    solution = solver.solve(problem)
    assert solution.get_score().getScore() == -2

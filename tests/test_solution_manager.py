from timefold.solver import *
from timefold.solver.domain import *
from timefold.solver.config import *
from timefold.solver.score import *

from dataclasses import dataclass, field
from typing import Annotated, List


@planning_entity
@dataclass(eq=True, unsafe_hash=True)
class Entity:
    code: Annotated[str, PlanningId] = field(hash=True)
    value: Annotated[int, PlanningVariable] = field(default=None, hash=False, compare=False)


@constraint_provider
def my_constraints(constraint_factory: ConstraintFactory):
    return [
        constraint_factory.for_each(Entity)
                          .reward(SimpleScore.ONE, lambda entity: entity.value)
                          .as_constraint('package', 'Maximize Value'),
    ]


@planning_solution
@dataclass
class Solution:
    entity_list: Annotated[List[Entity], PlanningEntityCollectionProperty]
    value_range: Annotated[List[int], ValueRangeProvider]
    score: Annotated[SimpleScore, PlanningScore] = field(default=None)


solver_config = SolverConfig(
    solution_class=Solution,
    entity_class_list=[Entity],
    score_director_factory_config=ScoreDirectorFactoryConfig(
        constraint_provider_function=my_constraints
    )
)


def assert_score_explanation(problem: Solution,
                             score_explanation: ScoreExplanation[Solution]):
    assert score_explanation.solution is problem
    assert score_explanation.score.score == 3

    constraint_ref = ConstraintRef(package_name='package', constraint_name='Maximize Value')
    constraint_match_total_map = score_explanation.constraint_match_total_map
    assert constraint_match_total_map == {
        constraint_ref.constraint_id: ConstraintMatchTotal(
            constraint_ref=constraint_ref,
            constraint_match_count=3,
            constraint_weight=SimpleScore.ONE,
            score=SimpleScore.of(3),
            constraint_match_set={
                ConstraintMatch(
                    constraint_ref=constraint_ref,
                    justification=DefaultConstraintJustification(
                        facts=(entity,),
                        impact=SimpleScore.ONE
                    ),
                    indicted_objects=(entity,),
                    score=SimpleScore.ONE
                ) for entity in problem.entity_list
            }
        )
    }

    indictment_map = score_explanation.indictment_map
    for entity in problem.entity_list:
        indictment = indictment_map[entity]
        assert indictment.indicted_object is entity
        assert indictment.score == SimpleScore.ONE
        assert indictment.constraint_match_count == 1
        assert indictment.constraint_match_set == {
            ConstraintMatch(
                constraint_ref=constraint_ref,
                justification=DefaultConstraintJustification(
                    facts=(entity,),
                    impact=SimpleScore.ONE
                ),
                indicted_objects=(entity,),
                score=SimpleScore.ONE
            )
        }

    assert constraint_ref.constraint_name in score_explanation.summary
    assert 'Entity' in score_explanation.summary


def assert_constraint_analysis(problem: Solution, constraint_analysis: ConstraintAnalysis):
    constraint_ref = ConstraintRef(package_name='package', constraint_name='Maximize Value')
    assert constraint_analysis.score.score == 3
    assert constraint_analysis.weight.score == 1
    assert constraint_analysis.constraint_name == constraint_ref.constraint_name
    assert constraint_analysis.constraint_package == constraint_ref.package_name
    assert constraint_analysis.constraint_ref == constraint_ref

    matches = constraint_analysis.matches
    assert len(matches) == 3
    for entity in problem.entity_list:
        for match in constraint_analysis.matches:
            if match.justification.facts[0] is entity:
                assert match.score == SimpleScore.ONE
                assert match.constraint_ref == constraint_ref
                assert match.justification.facts == (entity,)
                assert match.justification.impact == SimpleScore.ONE
                break
        else:
            raise AssertionError(f'Entity {entity} does not have a match')


def assert_score_analysis(problem: Solution, score_analysis: ScoreAnalysis):
    constraint_ref = ConstraintRef(package_name='package', constraint_name='Maximize Value')
    assert score_analysis.score.score == 3

    constraint_map = score_analysis.constraint_map
    assert len(constraint_map) == 1

    constraint_analysis = score_analysis.constraint_map[constraint_ref]
    assert_constraint_analysis(problem, constraint_analysis)

    constraint_analyses = score_analysis.constraint_analyses
    assert len(constraint_analyses) == 1
    constraint_analysis = constraint_analyses[0]
    assert_constraint_analysis(problem, constraint_analysis)


def assert_solution_manager(solution_manager: SolutionManager[Solution]):
    problem: Solution = Solution([Entity('A', 1), Entity('B', 1), Entity('C', 1)], [1, 2, 3])
    assert problem.score is None
    score = solution_manager.update(problem)
    assert score.score == 3
    assert problem.score.score == 3

    score_explanation = solution_manager.explain(problem)
    assert_score_explanation(problem, score_explanation)

    score_analysis = solution_manager.analyze(problem)
    assert_score_analysis(problem, score_analysis)


def test_solver_manager_score_manager():
    with SolverManager.create(SolverFactory.create(solver_config)) as solver_manager:
        assert_solution_manager(SolutionManager.create(solver_manager))


def test_solver_factory_score_manager():
    assert_solution_manager(SolutionManager.create(SolverFactory.create(solver_config)))

import timefold.solver
import timefold.solver.score
import timefold.solver.config
import timefold.solver.constraint
import pytest

from dataclasses import dataclass, field
from typing import Annotated, List, Optional


@timefold.solver.planning_entity
@dataclass
class Queen:
    code: str
    column: int
    row: Annotated[Optional[int], timefold.solver.PlanningVariable] = field(default=None)

    def getColumnIndex(self):
        return self.column

    def getRowIndex(self):
        if self.row is None:
            return -1
        return self.row

    def getAscendingDiagonalIndex(self):
        return self.getColumnIndex() + self.getRowIndex()

    def getDescendingDiagonalIndex(self):
        return self.getColumnIndex() - self.getRowIndex()

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


@timefold.solver.planning_solution
@dataclass
class Solution:
    n: int
    queen_list: Annotated[List[Queen], timefold.solver.PlanningEntityCollectionProperty]
    column_list: List[int]
    row_list: Annotated[List[int], timefold.solver.ValueRangeProvider]
    score: Annotated[timefold.solver.score.HardSoftScore, timefold.solver.PlanningScore] = field(default=None)

def test_constraint_match_disabled_incremental_score_calculator():
    @timefold.solver.incremental_score_calculator
    class IncrementalScoreCalculator:
        uninit_score: int  # Workaround, since None is considered initialized
        score: int
        row_index_map: dict
        ascending_diagonal_index_map: dict
        descending_diagonal_index_map: dict

        def resetWorkingSolution(self, working_solution: Solution):
            n = working_solution.n
            self.row_index_map = dict()
            self.ascending_diagonal_index_map = dict()
            self.descending_diagonal_index_map = dict()
            for i in range(n):
                self.row_index_map[i] = list()
                self.ascending_diagonal_index_map[i] = list()
                self.descending_diagonal_index_map[i] = list()
                if i != 0:
                    self.ascending_diagonal_index_map[n - 1 + i] = list()
                    self.descending_diagonal_index_map[-i] = list()
            self.score = 0
            self.uninit_score = 0
            for queen in working_solution.queen_list:
                self.insert(queen)

        def beforeEntityAdded(self, entity: any):
            pass

        def afterEntityAdded(self, entity: any):
            self.insert(entity)

        def beforeVariableChanged(self, entity: any, variableName: str):
            self.retract(entity)

        def afterVariableChanged(self, entity: any, variableName: str):
            self.insert(entity)

        def beforeEntityRemoved(self, entity: any):
            self.retract(entity)

        def afterEntityRemoved(self, entity: any):
            pass

        def insert(self, queen: Queen):
            if queen.row is not None:
                row_index = queen.row
                row_index_list = self.row_index_map[row_index]
                self.score -= len(row_index_list)
                row_index_list.append(queen)
                ascending_diagonal_index_list = self.ascending_diagonal_index_map[queen.getAscendingDiagonalIndex()]
                self.score -= len(ascending_diagonal_index_list)
                ascending_diagonal_index_list.append(queen)
                descending_diagonal_index_list = self.descending_diagonal_index_map[queen.getDescendingDiagonalIndex()]
                self.score -= len(descending_diagonal_index_list)
                descending_diagonal_index_list.append(queen)
            else:
                self.uninit_score -= 1

        def retract(self, queen: Queen):
            if queen.row is not None:
                row_index = queen.row
                row_index_list = self.row_index_map[row_index]
                row_index_list.remove(queen)
                self.score += len(row_index_list)
                ascending_diagonal_index_list = self.ascending_diagonal_index_map[queen.getAscendingDiagonalIndex()]
                ascending_diagonal_index_list.remove(queen)
                self.score += len(ascending_diagonal_index_list)
                descending_diagonal_index_list = self.descending_diagonal_index_map[queen.getDescendingDiagonalIndex()]
                descending_diagonal_index_list.remove(queen)
                self.score += len(descending_diagonal_index_list)
            else:
                self.uninit_score += 1

        def calculateScore(self) -> timefold.solver.score.HardSoftScore:
            return timefold.solver.score.HardSoftScore.of(self.uninit_score, self.score)

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Queen],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            incremental_score_calculator_class=IncrementalScoreCalculator
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0hard/0soft'
        )
    )
    problem: Solution = Solution(4,
                                 [Queen('A', 0), Queen('B', 1), Queen('C', 2), Queen('D', 3)],
                                 [0, 1, 2, 3],
                                 [0, 1, 2, 3])
    solver = timefold.solver.SolverFactory.create(solver_config).build_solver()
    solution = solver.solve(problem)
    assert solution.score.hard_score() == 0
    assert solution.score.soft_score() == 0
    for i in range(4):
        for j in range(i + 1, 4):
            left_queen = solution.queen_list[i]
            right_queen = solution.queen_list[j]
            assert left_queen.row is not None and right_queen.row is not None
            assert left_queen.row != right_queen.row
            assert left_queen.getAscendingDiagonalIndex() != right_queen.getAscendingDiagonalIndex()
            assert left_queen.getDescendingDiagonalIndex() != right_queen.getDescendingDiagonalIndex()


@pytest.mark.skip(reason="Special case where you want to convert all items of the list before returning."
                         "Doing this for all conversions would be expensive."
                         "This feature is not that important, so skipping for now.")
def test_constraint_match_enabled_incremental_score_calculator():
    @timefold.solver.incremental_score_calculator
    class IncrementalScoreCalculator:
        score: int
        uninit_score: int
        row_index_map: dict
        ascending_diagonal_index_map: dict
        descending_diagonal_index_map: dict

        def resetWorkingSolution(self, working_solution: Solution, constraint_match_enabled=False):
            n = working_solution.n
            self.row_index_map = dict()
            self.ascending_diagonal_index_map = dict()
            self.descending_diagonal_index_map = dict()
            for i in range(n):
                self.row_index_map[i] = list()
                self.ascending_diagonal_index_map[i] = list()
                self.descending_diagonal_index_map[i] = list()
                if i != 0:
                    self.ascending_diagonal_index_map[n - 1 + i] = list()
                    self.descending_diagonal_index_map[-i] = list()
            self.score = 0
            self.uninit_score = 0
            for queen in working_solution.queen_list:
                self.insert(queen)

        def beforeEntityAdded(self, entity: any):
            pass

        def afterEntityAdded(self, entity: any):
            self.insert(entity)

        def beforeVariableChanged(self, entity: any, variableName: str):
            self.retract(entity)

        def afterVariableChanged(self, entity: any, variableName: str):
            self.insert(entity)

        def beforeEntityRemoved(self, entity: any):
            self.retract(entity)

        def afterEntityRemoved(self, entity: any):
            pass

        def insert(self, queen: Queen):
            row = queen.row
            if row is not None:
                row_index = queen.row
                row_index_list = self.row_index_map[row_index]
                self.score -= len(row_index_list)
                row_index_list.append(queen)
                ascending_diagonal_index_list = self.ascending_diagonal_index_map[queen.getAscendingDiagonalIndex()]
                self.score -= len(ascending_diagonal_index_list)
                ascending_diagonal_index_list.append(queen)
                descending_diagonal_index_list = self.descending_diagonal_index_map[queen.getDescendingDiagonalIndex()]
                self.score -= len(descending_diagonal_index_list)
                descending_diagonal_index_list.append(queen)
            else:
                self.uninit_score -= 1

        def retract(self, queen: Queen):
            row = queen.row
            if row is not None:
                row_index = queen.row
                row_index_list = self.row_index_map[row_index]
                row_index_list.remove(queen)
                self.score += len(row_index_list)
                ascending_diagonal_index_list = self.ascending_diagonal_index_map[queen.getAscendingDiagonalIndex()]
                ascending_diagonal_index_list.remove(queen)
                self.score += len(ascending_diagonal_index_list)
                descending_diagonal_index_list = self.descending_diagonal_index_map[queen.getDescendingDiagonalIndex()]
                descending_diagonal_index_list.remove(queen)
                self.score += len(descending_diagonal_index_list)
            else:
                self.uninit_score += 1

        def calculateScore(self) -> timefold.solver.score.HardSoftScore:
            return timefold.solver.score.HardSoftScore.of(self.uninit_score, self.score)

        def getConstraintMatchTotals(self):
            row_conflict_constraint_match_total = timefold.solver.constraint.DefaultConstraintMatchTotal(
                'NQueens',
                'Row Conflict',
                timefold.solver.score.SimpleScore.ONE)
            ascending_diagonal_constraint_match_total = timefold.solver.constraint.DefaultConstraintMatchTotal(
                'NQueens',
                'Ascending Diagonal Conflict',
                timefold.solver.score.SimpleScore.ONE)
            descending_diagonal_constraint_match_total = timefold.solver.constraint.DefaultConstraintMatchTotal(
                'NQueens',
                'Descending Diagonal Conflict',
                timefold.solver.score.SimpleScore.ONE)
            for row, queens in self.row_index_map.items():
                if len(queens) > 1:
                    row_conflict_constraint_match_total.addConstraintMatch(queens,
                                                                           timefold.solver.score.SimpleScore.of(
                                                                               -len(queens) + 1))
            for row, queens in self.ascending_diagonal_index_map.items():
                if len(queens) > 1:
                    ascending_diagonal_constraint_match_total.addConstraintMatch(queens,
                                                                                 timefold.solver.score.SimpleScore.of(
                                                                                     -len(queens) + 1))
            for row, queens in self.descending_diagonal_index_map.items():
                if len(queens) > 1:
                    descending_diagonal_constraint_match_total.addConstraintMatch(queens,
                                                                                  timefold.solver.score.SimpleScore.of(
                                                                                      -len(queens) + 1))
            return [
                row_conflict_constraint_match_total,
                ascending_diagonal_constraint_match_total,
                descending_diagonal_constraint_match_total
            ]

        def getIndictmentMap(self):
            return None

    solver_config = timefold.solver.config.SolverConfig(
        solution_class=Solution,
        entity_class_list=[Queen],
        score_director_factory_config=timefold.solver.config.ScoreDirectorFactoryConfig(
            incremental_score_calculator_class=IncrementalScoreCalculator
        ),
        termination_config=timefold.solver.config.TerminationConfig(
            best_score_limit='0hard/0soft'
        )
    )
    problem: Solution = Solution(4,
                                 [Queen('A', 0), Queen('B', 1), Queen('C', 2), Queen('D', 3)],
                                 [0, 1, 2, 3],
                                 [0, 1, 2, 3])
    solver_factory = timefold.solver.SolverFactory.create(solver_config)
    solver = solver_factory.build_solver()
    solution = solver.solve(problem)
    assert solution.score.hard_score() == 0
    assert solution.score.soft_score() == 0
    for i in range(4):
        for j in range(i + 1, 4):
            left_queen = solution.queen_list[i]
            right_queen = solution.queen_list[j]
            assert left_queen.row is not None and right_queen.row is not None
            assert left_queen.row != right_queen.row
            assert left_queen.getAscendingDiagonalIndex() != right_queen.getAscendingDiagonalIndex()
            assert left_queen.getDescendingDiagonalIndex() != right_queen.getDescendingDiagonalIndex()

    score_manager = timefold.solver.SolutionManager.create(solver_factory)
    constraint_match_total_map = score_manager.explain(solution).get_constraint_match_total_map()
    row_conflict = constraint_match_total_map.get('NQueens/Row Conflict')
    ascending_diagonal_conflict = constraint_match_total_map.get('NQueens/Ascending Diagonal Conflict')
    descending_diagonal_conflict = constraint_match_total_map.get('NQueens/Descending Diagonal Conflict')
    assert row_conflict.score().soft_score() == 0
    assert ascending_diagonal_conflict.score().soft_score() == 0
    assert descending_diagonal_conflict.score().soft_score() == 0

    bad_solution = Solution(4,
                            [Queen('A', 0, 0), Queen('B', 1, 1), Queen('C', 2, 0), Queen('D', 3, 1)],
                            [0, 1, 2, 3],
                            [0, 1, 2, 3])
    score_explanation = score_manager.explain(bad_solution)
    assert score_explanation.get_score().soft_score() == -5
    constraint_match_total_map = score_explanation.getConstraintMatchTotalMap()
    row_conflict = constraint_match_total_map.get('NQueens/Row Conflict')
    ascending_diagonal_conflict = constraint_match_total_map.get('NQueens/Ascending Diagonal Conflict')
    descending_diagonal_conflict = constraint_match_total_map.get('NQueens/Descending Diagonal Conflict')
    assert row_conflict.score().soft_score() == -2  # (A, C), (B, D)
    assert ascending_diagonal_conflict.score().soft_score() == -1  # (B, C)
    assert descending_diagonal_conflict.score().soft_score() == -2  # (A, B), (C, D)
    indictment_map = score_explanation.getIndictmentMap()
    assert indictment_map.get(bad_solution.queen_list[0]).getConstraintMatchCount() == 2
    assert indictment_map.get(bad_solution.queen_list[1]).getConstraintMatchCount() == 3
    assert indictment_map.get(bad_solution.queen_list[2]).getConstraintMatchCount() == 3
    assert indictment_map.get(bad_solution.queen_list[3]).getConstraintMatchCount() == 2


def test_error_message_for_missing_methods():
    with pytest.raises(ValueError, match=(
            f"The following required methods are missing from @incremental_score_calculator class "
            f".*IncrementalScoreCalculatorMissingMethods.*: "
            f"\\['resetWorkingSolution', 'beforeEntityRemoved', 'afterEntityRemoved', 'calculateScore'\\]"
    )):
        @timefold.solver.incremental_score_calculator
        class IncrementalScoreCalculatorMissingMethods:
            def beforeEntityAdded(self, entity: any):
                pass

            def afterEntityAdded(self, entity: any):
                pass

            def beforeVariableChanged(self, entity: any, variableName: str):
                pass

            def afterVariableChanged(self, entity: any, variableName: str):
                pass

from timefold.solver import SolverStatus
from timefold.solver.domain import *
from timefold.solver.score import HardSoftDecimalScore
from datetime import datetime, date
from typing import Annotated
from pydantic import Field

from .json_serialization import *


class Employee(JsonDomainBase):
    name: Annotated[str, PlanningId]
    skills: Annotated[set[str], Field(default_factory=set)]
    unavailable_dates: Annotated[set[date], Field(default_factory=set)]
    undesired_dates: Annotated[set[date], Field(default_factory=set)]
    desired_dates: Annotated[set[date], Field(default_factory=set)]


@planning_entity
class Shift(JsonDomainBase):
    id: Annotated[str, PlanningId]
    start: datetime
    end: datetime
    location: str
    required_skill: str
    employee: Annotated[Employee | None,
                        PlanningVariable,
                        Field(default=None)]


@planning_solution
class EmployeeSchedule(JsonDomainBase):
    employees: Annotated[list[Employee], ProblemFactCollectionProperty, ValueRangeProvider]
    shifts: Annotated[list[Shift], PlanningEntityCollectionProperty]
    score: Annotated[HardSoftDecimalScore | None,
                     PlanningScore, ScoreSerializer, ScoreValidator, Field(default=None)]
    solver_status: Annotated[SolverStatus | None, Field(default=None)]

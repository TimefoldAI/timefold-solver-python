from timefold.solver import SolverStatus
from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver.score import HardSoftScore
from datetime import time

from .json_serialization import *


class Timeslot(JsonDomainBase):
    id: Annotated[str, PlanningId]
    day_of_week: str
    start_time: time
    end_time: time


class Room(JsonDomainBase):
    id: Annotated[str, PlanningId]
    name: str


@planning_entity
class Lesson(JsonDomainBase):
    id: Annotated[str, PlanningId]
    subject: str
    teacher: str
    student_group: str
    timeslot: Annotated[Timeslot | None,
                        PlanningVariable,
                        IdSerializer,
                        TimeslotDeserializer,
                        Field(default=None)]
    room: Annotated[Room | None,
                    PlanningVariable,
                    IdSerializer,
                    RoomDeserializer,
                    Field(default=None)]


@planning_solution
class Timetable(JsonDomainBase):
    id: str
    timeslots: Annotated[list[Timeslot],
                         ProblemFactCollectionProperty,
                         ValueRangeProvider]
    rooms: Annotated[list[Room],
                     ProblemFactCollectionProperty,
                     ValueRangeProvider]
    lessons: Annotated[list[Lesson],
                       PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore | None,
                     PlanningScore,
                     ScoreSerializer,
                     ScoreValidator,
                     Field(default=None)]
    solver_status: Annotated[SolverStatus, Field(default=SolverStatus.NOT_SOLVING)]

from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver.score import HardSoftScore
from dataclasses import dataclass, field
from datetime import time
from typing import Annotated


@dataclass
class Timeslot:
    day_of_week: str
    start_time: time
    end_time: time

    def __str__(self):
        return f'{self.day_of_week} {self.start_time.strftime("%H:%M")}'


@dataclass
class Room:
    name: str

    def __str__(self):
        return f'{self.name}'


@planning_entity
@dataclass
class Lesson:
    id: Annotated[str, PlanningId]
    subject: str
    teacher: str
    student_group: str
    timeslot: Annotated[Timeslot | None, PlanningVariable] = field(default=None)
    room: Annotated[Room | None, PlanningVariable] = field(default=None)


@planning_solution
@dataclass
class Timetable:
    id: str
    timeslots: Annotated[list[Timeslot],
                         ProblemFactCollectionProperty,
                         ValueRangeProvider]
    rooms: Annotated[list[Room],
                     ProblemFactCollectionProperty,
                     ValueRangeProvider]
    lessons: Annotated[list[Lesson],
                       PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)

from timefold.solver.score import (constraint_provider, HardSoftScore, Joiners,
                                   ConstraintFactory, Constraint)
from datetime import time

from .domain import Lesson

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        room_conflict(constraint_factory),
        teacher_conflict(constraint_factory),
        student_group_conflict(constraint_factory),

        # Soft constraints
        teacher_room_stability(constraint_factory),
        teacher_time_efficiency(constraint_factory),
        student_group_subject_variety(constraint_factory),
    ]


def room_conflict(constraint_factory: ConstraintFactory) -> Constraint:
    # A room can accommodate at most one lesson at the same time.
    return (constraint_factory
            # Select each pair of 2 different lessons ...
            .for_each_unique_pair(Lesson,
                                  # ... in the same timeslot ...
                                  Joiners.equal(lambda lesson: lesson.timeslot),
                                  # ... in the same room ...
                                  Joiners.equal(lambda lesson: lesson.room))
            # ... and penalize each pair with a hard weight.
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Room conflict"))


def teacher_conflict(constraint_factory: ConstraintFactory) -> Constraint:
    # A teacher can teach at most one lesson at the same time.
    return (constraint_factory
            .for_each_unique_pair(Lesson,
                                  Joiners.equal(lambda lesson: lesson.timeslot),
                                  Joiners.equal(lambda lesson: lesson.teacher))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Teacher conflict"))


def student_group_conflict(constraint_factory: ConstraintFactory) -> Constraint:
    # A student can attend at most one lesson at the same time.
    return (constraint_factory
            .for_each_unique_pair(Lesson,
                                  Joiners.equal(lambda lesson: lesson.timeslot),
                                  Joiners.equal(lambda lesson: lesson.student_group))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Student group conflict"))


def teacher_room_stability(constraint_factory: ConstraintFactory) -> Constraint:
    # A teacher prefers to teach in a single room.
    return (constraint_factory
            .for_each_unique_pair(Lesson,
                                  Joiners.equal(lambda lesson: lesson.teacher))
            .filter(lambda lesson1, lesson2: lesson1.room != lesson2.room)
            .penalize(HardSoftScore.ONE_SOFT)
            .as_constraint("Teacher room stability"))


def to_minutes(moment: time) -> int:
    return moment.hour * 60 + moment.minute


def is_between(lesson1: Lesson, lesson2: Lesson) -> bool:
    difference = to_minutes(lesson1.timeslot.end_time) - to_minutes(lesson2.timeslot.start_time)
    return 0 <= difference <= 30


def teacher_time_efficiency(constraint_factory: ConstraintFactory) -> Constraint:
    # A teacher prefers to teach sequential lessons and dislikes gaps between lessons.
    return (constraint_factory.for_each(Lesson)
            .join(Lesson,
                  Joiners.equal(lambda lesson: lesson.teacher),
                  Joiners.equal(lambda lesson: lesson.timeslot.day_of_week))
            .filter(is_between)
            .reward(HardSoftScore.ONE_SOFT)
            .as_constraint("Teacher time efficiency"))


def student_group_subject_variety(constraint_factory: ConstraintFactory) -> Constraint:
    # A student group dislikes sequential lessons on the same subject.
    return (((constraint_factory.for_each(Lesson)
            .join(Lesson,
                  Joiners.equal(lambda lesson: lesson.subject),
                  Joiners.equal(lambda lesson: lesson.student_group),
                  Joiners.equal(lambda lesson: lesson.timeslot.day_of_week))
            .filter(is_between))
            .penalize(HardSoftScore.ONE_SOFT))
            .as_constraint("Student group subject variety"))

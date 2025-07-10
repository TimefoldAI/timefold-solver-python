from timefold.solver.test import ConstraintVerifier
from datetime import time

from school_timetabling.domain import *
from school_timetabling.constraints import *


ROOM1 = Room(id="1", name="Room1")
ROOM2 = Room(id="2", name="Room2")

TIMESLOT1 = Timeslot(id="1", day_of_week="MONDAY", start_time=time(12, 0), end_time=time(13, 0))
TIMESLOT2 = Timeslot(id="2", day_of_week="TUESDAY", start_time=time(12, 0), end_time=time(13, 0))
TIMESLOT3 = Timeslot(id="3", day_of_week="TUESDAY", start_time=time(13, 0), end_time=time(14, 0))
TIMESLOT4 = Timeslot(id="4", day_of_week="TUESDAY", start_time=time(15, 0), end_time=time(16, 0))

constraint_verifier = ConstraintVerifier.build(define_constraints, Timetable, Lesson)


def test_room_conflict():
    first_lesson = Lesson(id="1", subject="Subject1", teacher="Teacher1", student_group="Group1",
                          timeslot=TIMESLOT1, room=ROOM1)
    conflicting_lesson = Lesson(id="2", subject="Subject2", teacher="Teacher2", student_group="Group2",
                                timeslot=TIMESLOT1, room=ROOM1)
    non_conflicting_lesson = Lesson(id="3", subject="Subject3", teacher="Teacher3", student_group="Group3",
                                    timeslot=TIMESLOT2, room=ROOM1)
    (constraint_verifier.verify_that(room_conflict)
        .given(first_lesson, conflicting_lesson, non_conflicting_lesson)
        .penalizes_by(1))


def test_teacher_conflict():
    conflicting_teacher = "Teacher1"
    first_lesson = Lesson(id="1", subject="Subject1", teacher=conflicting_teacher, student_group="Group1",
                          timeslot=TIMESLOT1, room=ROOM1)
    conflicting_lesson = Lesson(id="2", subject="Subject2", teacher=conflicting_teacher, student_group="Group2",
                                timeslot=TIMESLOT1, room=ROOM2)
    non_conflicting_lesson = Lesson(id="3", subject="Subject3", teacher="Teacher2", student_group="Group3",
                                    timeslot=TIMESLOT2, room=ROOM1)
    (constraint_verifier.verify_that(teacher_conflict)
        .given(first_lesson, conflicting_lesson, non_conflicting_lesson)
        .penalizes_by(1))


def test_student_group_conflict():
    conflicting_group = "Group1"
    first_lesson = Lesson(id="1", subject="Subject1", teacher="Teacher1", student_group=conflicting_group,
                          timeslot=TIMESLOT1, room=ROOM1)
    conflicting_lesson = Lesson(id="2", subject="Subject2", teacher="Teacher2", student_group=conflicting_group,
                                timeslot=TIMESLOT1, room=ROOM2)
    non_conflicting_lesson = Lesson(id="3", subject="Subject3", teacher="Teacher3", student_group="Group3",
                                    timeslot=TIMESLOT2, room=ROOM1)
    (constraint_verifier.verify_that(student_group_conflict)
        .given(first_lesson, conflicting_lesson, non_conflicting_lesson)
        .penalizes_by(1))


def test_teacher_room_stability():
    teacher = "Teacher1"
    lesson_in_first_room = Lesson(id="1", subject="Subject1", teacher=teacher, student_group="Group1",
                                  timeslot=TIMESLOT1, room=ROOM1)
    lesson_in_same_room = Lesson(id="2", subject="Subject2", teacher=teacher, student_group="Group2",
                                 timeslot=TIMESLOT1, room=ROOM1)
    lesson_in_different_room = Lesson(id="3", subject="Subject3", teacher=teacher, student_group="Group3",
                                      timeslot=TIMESLOT1, room=ROOM2)
    (constraint_verifier.verify_that(teacher_room_stability)
        .given(lesson_in_first_room, lesson_in_different_room, lesson_in_same_room)
        .penalizes_by(2))


def test_teacher_time_efficiency():
    teacher = "Teacher1"
    single_lesson_on_monday = Lesson(id="1", subject="Subject1", teacher=teacher, student_group="Group1",
                                     timeslot=TIMESLOT1, room=ROOM1)
    first_tuesday_lesson = Lesson(id="2", subject="Subject2", teacher=teacher, student_group="Group2",
                                  timeslot=TIMESLOT2, room=ROOM1)
    second_tuesday_lesson = Lesson(id="3", subject="Subject3", teacher=teacher, student_group="Group3",
                                   timeslot=TIMESLOT3, room=ROOM1)
    third_tuesday_lesson_with_gap = Lesson(id="4", subject="Subject4", teacher=teacher, student_group="Group4",
                                           timeslot=TIMESLOT4, room=ROOM1)
    (constraint_verifier.verify_that(teacher_time_efficiency)
        .given(single_lesson_on_monday, first_tuesday_lesson, second_tuesday_lesson, third_tuesday_lesson_with_gap)
        .rewards_with(1))  # Second tuesday lesson immediately follows the first.

    # Reverse ID order
    alt_second_tuesday_lesson = Lesson(id="2", subject="Subject2", teacher=teacher, student_group="Group3",
                                       timeslot=TIMESLOT3, room=ROOM1)
    alt_first_tuesday_lesson = Lesson(id="3", subject="Subject3", teacher=teacher, student_group="Group2",
                                      timeslot=TIMESLOT2, room=ROOM1)
    (constraint_verifier.verify_that(teacher_time_efficiency)
        .given(alt_second_tuesday_lesson, alt_first_tuesday_lesson)
        .rewards_with(1))  # Second tuesday lesson immediately follows the first.


def test_student_group_subject_variety():
    student_group = "Group1"
    repeated_subject = "Subject1"
    monday_lesson = Lesson(id="1", subject=repeated_subject, teacher="Teacher1", student_group=student_group,
                           timeslot=TIMESLOT1, room=ROOM1)
    first_tuesday_lesson = Lesson(id="2", subject=repeated_subject, teacher="Teacher2", student_group=student_group,
                                  timeslot=TIMESLOT2, room=ROOM1)
    second_tuesday_lesson = Lesson(id="3", subject=repeated_subject, teacher="Teacher3", student_group=student_group,
                                   timeslot=TIMESLOT3, room=ROOM1)
    third_tuesday_lesson_with_different_subject = Lesson(id="4", subject="Subject2", teacher="Teacher4",
                                                         student_group=student_group, timeslot=TIMESLOT4, room=ROOM1)
    lesson_in_another_group = Lesson(id="5", subject=repeated_subject, teacher="Teacher5", student_group="Group2",
                                     timeslot=TIMESLOT1, room=ROOM1)
    (constraint_verifier.verify_that(student_group_subject_variety)
        .given(monday_lesson, first_tuesday_lesson, second_tuesday_lesson, third_tuesday_lesson_with_different_subject,
               lesson_in_another_group)
        .penalizes_by(1))  # Second tuesday lesson immediately follows the first.

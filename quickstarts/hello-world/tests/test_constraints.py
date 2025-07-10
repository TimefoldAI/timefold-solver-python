from timefold.solver.test import ConstraintVerifier
from datetime import time

from hello_world.domain import *
from hello_world.constraints import *

ROOM1 = Room("Room1")
ROOM2 = Room("Room2")
TIMESLOT1 = Timeslot("MONDAY", time(12, 0), time(13, 0))
TIMESLOT2 = Timeslot("TUESDAY", time(12, 0), time(13, 0))
TIMESLOT3 = Timeslot("TUESDAY", time(13, 0), time(14, 0))
TIMESLOT4 = Timeslot("TUESDAY", time(15, 0), time(16, 0))

constraint_verifier = ConstraintVerifier.build(define_constraints, Timetable, Lesson)

def test_room_conflict():
    first_lesson = Lesson("1", "Subject1", "Teacher1", "Group1", TIMESLOT1, ROOM1)
    conflicting_lesson = Lesson("2", "Subject2", "Teacher2", "Group2", TIMESLOT1, ROOM1)
    non_conflicting_lesson = Lesson("3", "Subject3", "Teacher3", "Group3", TIMESLOT2, ROOM1)
    (constraint_verifier.verify_that(room_conflict)
        .given(first_lesson, conflicting_lesson, non_conflicting_lesson)
        .penalizes_by(1))


def test_teacher_conflict():
    conflicting_teacher = "Teacher1"
    first_lesson = Lesson("1", "Subject1", conflicting_teacher, "Group1", TIMESLOT1, ROOM1)
    conflicting_lesson = Lesson("2", "Subject2", conflicting_teacher, "Group2", TIMESLOT1, ROOM2)
    non_conflicting_lesson = Lesson("3", "Subject3", "Teacher2", "Group3", TIMESLOT2, ROOM1)
    (constraint_verifier.verify_that(teacher_conflict)
        .given(first_lesson, conflicting_lesson, non_conflicting_lesson)
        .penalizes_by(1))


def test_student_group_conflict():
    conflicting_group = "Group1"
    first_lesson = Lesson("1", "Subject1", "Teacher1", conflicting_group, TIMESLOT1, ROOM1)
    conflicting_lesson = Lesson("2", "Subject2", "Teacher2", conflicting_group, TIMESLOT1, ROOM2)
    non_conflicting_lesson = Lesson("3", "Subject3", "Teacher3", "Group3", TIMESLOT2, ROOM1)
    (constraint_verifier.verify_that(student_group_conflict)
        .given(first_lesson, conflicting_lesson, non_conflicting_lesson)
        .penalizes_by(1))


def test_teacher_room_stability():
    teacher = "Teacher1"
    lesson_in_first_room = Lesson("1", "Subject1", teacher, "Group1", TIMESLOT1, ROOM1)
    lesson_in_same_room = Lesson("2", "Subject2", teacher, "Group2", TIMESLOT1, ROOM1)
    lesson_in_different_room = Lesson("3", "Subject3", teacher, "Group3", TIMESLOT1, ROOM2)
    (constraint_verifier.verify_that(teacher_room_stability)
        .given(lesson_in_first_room, lesson_in_different_room, lesson_in_same_room)
        .penalizes_by(2))


def test_teacher_time_efficiency():
    teacher = "Teacher1"
    single_lesson_on_monday = Lesson("1", "Subject1", teacher, "Group1", TIMESLOT1, ROOM1)
    first_tuesday_lesson = Lesson("2", "Subject2", teacher, "Group2", TIMESLOT2, ROOM1)
    second_tuesday_lesson = Lesson("3", "Subject3", teacher, "Group3", TIMESLOT3, ROOM1)
    third_tuesday_lesson_with_gap = Lesson("4", "Subject4", teacher, "Group4", TIMESLOT4, ROOM1)
    (constraint_verifier.verify_that(teacher_time_efficiency)
         .given(single_lesson_on_monday, first_tuesday_lesson, second_tuesday_lesson, third_tuesday_lesson_with_gap)
         .rewards_with(1)) # Second tuesday lesson immediately follows the first.

    # Reverse ID order
    alt_second_tuesday_lesson = Lesson("2", "Subject2", teacher, "Group3", TIMESLOT3, ROOM1)
    alt_first_tuesday_lesson = Lesson("3", "Subject3", teacher, "Group2", TIMESLOT2, ROOM1)
    (constraint_verifier.verify_that(teacher_time_efficiency)
        .given(alt_second_tuesday_lesson, alt_first_tuesday_lesson)
        .rewards_with(1))  # Second tuesday lesson immediately follows the first.


def test_student_group_subject_variety():
    student_group = "Group1"
    repeated_subject = "Subject1"
    monday_lesson = Lesson("1", repeated_subject, "Teacher1", student_group, TIMESLOT1, ROOM1)
    first_tuesday_lesson = Lesson("2", repeated_subject, "Teacher2", student_group, TIMESLOT2, ROOM1)
    second_tuesday_lesson = Lesson("3", repeated_subject, "Teacher3", student_group, TIMESLOT3, ROOM1)
    third_tuesday_lesson_with_different_subject = Lesson("4", "Subject2", "Teacher4", student_group, TIMESLOT4, ROOM1)
    lesson_in_another_group = Lesson("5", repeated_subject, "Teacher5", "Group2", TIMESLOT1, ROOM1)
    (constraint_verifier.verify_that(student_group_subject_variety)
        .given(monday_lesson, first_tuesday_lesson, second_tuesday_lesson, third_tuesday_lesson_with_different_subject,
               lesson_in_another_group)
        .penalizes_by(1))  # Second tuesday lesson immediately follows the first.

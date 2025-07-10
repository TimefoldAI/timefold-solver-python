from timefold.solver.test import ConstraintVerifier

from employee_scheduling.domain import *
from employee_scheduling.constraints import *

from datetime import date, datetime, time, timedelta

DAY_1 = date(2021, 2, 1)
DAY_3 = date(2021, 2, 3)
DAY_START_TIME = datetime.combine(DAY_1, time(9, 0))
DAY_END_TIME = datetime.combine(DAY_1, time(17, 0))
AFTERNOON_START_TIME = datetime.combine(DAY_1, time(13, 0))
AFTERNOON_END_TIME = datetime.combine(DAY_1, time(21, 0))

constraint_verifier = ConstraintVerifier.build(define_constraints, EmployeeSchedule, Shift)


def test_required_skill():
    employee = Employee(name="Amy")
    (constraint_verifier.verify_that(required_skill)
    .given(employee,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee))
    .penalizes(1))
    
    employee = Employee(name="Beth", skills={"Skill"})
    (constraint_verifier.verify_that(required_skill)
    .given(employee,
           Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee))
    .penalizes(0))


def test_overlapping_shifts():
    employee1 = Employee(name="Amy")
    employee2 = Employee(name="Beth")
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes_by(timedelta(hours=8) // timedelta(minutes=1)))
    
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location 2", required_skill="Skill", employee=employee2))
    .penalizes(0))
    
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=AFTERNOON_START_TIME, end=AFTERNOON_END_TIME, location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes_by(timedelta(hours=4) // timedelta(minutes=1)))


def test_one_shift_per_day():
    employee1 = Employee(name="Amy")
    employee2 = Employee(name="Beth")
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes(1))
    
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location 2", required_skill="Skill", employee=employee2))
    .penalizes(0))
    
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=AFTERNOON_START_TIME, end=AFTERNOON_END_TIME, location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes(1))
    
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_START_TIME + timedelta(days=1), end=DAY_END_TIME + timedelta(days=1), location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes(0))


def test_at_least_10_hours_between_shifts():
    employee1 = Employee(name="Amy")
    employee2 = Employee(name="Beth")
    
    (constraint_verifier.verify_that(at_least_10_hours_between_two_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=AFTERNOON_END_TIME, end=DAY_START_TIME + timedelta(days=1), location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes_by(360))
    
    (constraint_verifier.verify_that(at_least_10_hours_between_two_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_END_TIME, end=DAY_START_TIME + timedelta(days=1), location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes_by(600))

    (constraint_verifier.verify_that(at_least_10_hours_between_two_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_END_TIME, end=DAY_START_TIME + timedelta(days=1), location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes_by(600))
    
    (constraint_verifier.verify_that(at_least_10_hours_between_two_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_END_TIME + timedelta(hours=10), end=DAY_START_TIME + timedelta(days=1), location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes(0))
    
    (constraint_verifier.verify_that(at_least_10_hours_between_two_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=AFTERNOON_END_TIME, end=DAY_START_TIME + timedelta(days=1), location="Location 2", required_skill="Skill", employee=employee2))
    .penalizes(0))
    
    (constraint_verifier.verify_that(no_overlapping_shifts)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
           Shift(id="2", start=DAY_START_TIME + timedelta(days=1), end=DAY_END_TIME + timedelta(days=1), location="Location 2", required_skill="Skill", employee=employee1))
    .penalizes(0))


def test_unavailable_employee():
    employee1 = Employee(name="Amy", unavailable_dates={DAY_1, DAY_3})
    employee2 = Employee(name="Beth")

    (constraint_verifier.verify_that(unavailable_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1))
    .penalizes_by(timedelta(hours=8) // timedelta(minutes=1)))
    
    (constraint_verifier.verify_that(unavailable_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME - timedelta(days=1), end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1))
    .penalizes_by(timedelta(hours=17) // timedelta(minutes=1)))
    
    (constraint_verifier.verify_that(unavailable_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME + timedelta(days=1), end=DAY_END_TIME + timedelta(days=1), location="Location", required_skill="Skill", employee=employee1))
    .penalizes(0))
    
    (constraint_verifier.verify_that(unavailable_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee2))
    .penalizes(0))


def test_undesired_day_for_employee():
    employee1 = Employee(name="Amy", undesired_dates={DAY_1, DAY_3})
    employee2 = Employee(name="Beth")

    (constraint_verifier.verify_that(undesired_day_for_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1))
    .penalizes_by(timedelta(hours=8) // timedelta(minutes=1)))

    (constraint_verifier.verify_that(undesired_day_for_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME - timedelta(days=1), end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1))
    .penalizes_by(timedelta(hours=17) // timedelta(minutes=1)))

    (constraint_verifier.verify_that(undesired_day_for_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME + timedelta(days=1), end=DAY_END_TIME + timedelta(days=1), location="Location", required_skill="Skill", employee=employee1))
    .penalizes(0))

    (constraint_verifier.verify_that(undesired_day_for_employee)
    .given(employee1, employee2,
           Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee2))
    .penalizes(0))


def test_desired_day_for_employee():
    employee1 = Employee(name="Amy", desired_dates={DAY_1, DAY_3})
    employee2 = Employee(name="Beth")

    (constraint_verifier.verify_that(desired_day_for_employee)
     .given(employee1, employee2,
            Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1))
     .rewards_with(timedelta(hours=8) // timedelta(minutes=1)))

    (constraint_verifier.verify_that(desired_day_for_employee)
     .given(employee1, employee2,
            Shift(id="1", start=DAY_START_TIME - timedelta(days=1), end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1))
     .rewards_with(timedelta(hours=17) // timedelta(minutes=1)))

    (constraint_verifier.verify_that(desired_day_for_employee)
     .given(employee1, employee2,
            Shift(id="1", start=DAY_START_TIME + timedelta(days=1), end=DAY_END_TIME + timedelta(days=1), location="Location", required_skill="Skill", employee=employee1))
     .rewards(0))

    (constraint_verifier.verify_that(desired_day_for_employee)
     .given(employee1, employee2,
            Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee2))
     .rewards(0))

def test_balance_employee_shift_assignments():
    employee1 = Employee(name="Amy", desired_dates={DAY_1, DAY_3})
    employee2 = Employee(name="Beth")

    # No employees have shifts assigned; the schedule is perfectly balanced.
    (constraint_verifier.verify_that(balance_employee_shift_assignments)
     .given(employee1, employee2)
     .penalizes_by(0))

    # Only one employee has shifts assigned; the schedule is less balanced.
    (constraint_verifier.verify_that(balance_employee_shift_assignments)
     .given(employee1, employee2,
            Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1))
     .penalizes_by_more_than(0))

    # Every employee has a shift assigned; the schedule is once again perfectly balanced.
    (constraint_verifier.verify_that(balance_employee_shift_assignments)
     .given(employee1, employee2,
            Shift(id="1", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee1),
            Shift(id="2", start=DAY_START_TIME, end=DAY_END_TIME, location="Location", required_skill="Skill", employee=employee2))
     .penalizes_by(0))

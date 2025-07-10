from timefold.solver.score import (constraint_provider, ConstraintFactory, Joiners, HardSoftDecimalScore, ConstraintCollectors)
from datetime import datetime, date

from .domain import Employee, Shift


def get_minute_overlap(shift1: Shift, shift2: Shift) -> int:
    return (min(shift1.end, shift2.end) - max(shift1.start, shift2.start)).total_seconds() // 60


def is_overlapping_with_date(shift: Shift, dt: date) -> bool:
    return shift.start.date() == dt or shift.end.date() == dt


def overlapping_in_minutes(first_start_datetime: datetime, first_end_datetime: datetime,
                           second_start_datetime: datetime, second_end_datetime: datetime) -> int:
    latest_start = max(first_start_datetime, second_start_datetime)
    earliest_end = min(first_end_datetime, second_end_datetime)
    delta = (earliest_end - latest_start).total_seconds() / 60
    return max(0, delta)


def get_shift_overlapping_duration_in_minutes(shift: Shift, dt: date) -> int:
    overlap = 0
    start_date_time = datetime.combine(dt, datetime.max.time())
    end_date_time = datetime.combine(dt, datetime.min.time())
    overlap += overlapping_in_minutes(start_date_time, end_date_time, shift.start, shift.end)
    return overlap


@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        required_skill(constraint_factory),
        no_overlapping_shifts(constraint_factory),
        at_least_10_hours_between_two_shifts(constraint_factory),
        one_shift_per_day(constraint_factory),
        unavailable_employee(constraint_factory),
        # Soft constraints
        undesired_day_for_employee(constraint_factory),
        desired_day_for_employee(constraint_factory),
        balance_employee_shift_assignments(constraint_factory)
    ]


def required_skill(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Shift)
            .filter(lambda shift: shift.required_skill not in shift.employee.skills)
            .penalize(HardSoftDecimalScore.ONE_HARD)
            .as_constraint("Missing required skill")
            )


def no_overlapping_shifts(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each_unique_pair(Shift,
                                  Joiners.equal(lambda shift: shift.employee.name),
                                  Joiners.overlapping(lambda shift: shift.start, lambda shift: shift.end))
            .penalize(HardSoftDecimalScore.ONE_HARD, get_minute_overlap)
            .as_constraint("Overlapping shift")
            )


def at_least_10_hours_between_two_shifts(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Shift)
            .join(Shift,
                  Joiners.equal(lambda shift: shift.employee.name),
                  Joiners.less_than_or_equal(lambda shift: shift.end, lambda shift: shift.start)
                  )
            .filter(lambda first_shift, second_shift:
                    (second_shift.start - first_shift.end).total_seconds() // (60 * 60) < 10)
            .penalize(HardSoftDecimalScore.ONE_HARD,
                      lambda first_shift, second_shift:
                      600 - ((second_shift.start - first_shift.end).total_seconds() // 60))
            .as_constraint("At least 10 hours between 2 shifts")
            )


def one_shift_per_day(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each_unique_pair(Shift,
                                  Joiners.equal(lambda shift: shift.employee.name),
                                  Joiners.equal(lambda shift: shift.start.date()))
            .penalize(HardSoftDecimalScore.ONE_HARD)
            .as_constraint("Max one shift per day")
            )


def unavailable_employee(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Shift)
            .join(Employee, Joiners.equal(lambda shift: shift.employee, lambda employee: employee))
            .flatten_last(lambda employee: employee.unavailable_dates)
            .filter(lambda shift, unavailable_date: is_overlapping_with_date(shift, unavailable_date))
            .penalize(HardSoftDecimalScore.ONE_HARD,
                      lambda shift, unavailable_date: get_shift_overlapping_duration_in_minutes(shift,
                                                                                                unavailable_date))
            .as_constraint("Unavailable employee")
            )


def undesired_day_for_employee(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Shift)
            .join(Employee, Joiners.equal(lambda shift: shift.employee, lambda employee: employee))
            .flatten_last(lambda employee: employee.undesired_dates)
            .filter(lambda shift, undesired_date: is_overlapping_with_date(shift, undesired_date))
            .penalize(HardSoftDecimalScore.ONE_SOFT,
                      lambda shift, undesired_date: get_shift_overlapping_duration_in_minutes(shift, undesired_date))
            .as_constraint("Undesired day for employee")
            )


def desired_day_for_employee(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Shift)
            .join(Employee, Joiners.equal(lambda shift: shift.employee, lambda employee: employee))
            .flatten_last(lambda employee: employee.desired_dates)
            .filter(lambda shift, desired_date: is_overlapping_with_date(shift, desired_date))
            .reward(HardSoftDecimalScore.ONE_SOFT,
                    lambda shift, desired_date: get_shift_overlapping_duration_in_minutes(shift, desired_date))
            .as_constraint("Desired day for employee")
            )


def balance_employee_shift_assignments(constraint_factory: ConstraintFactory):
    return (constraint_factory.for_each(Shift)
            .group_by(lambda shift: shift.employee, ConstraintCollectors.count())
            .complement(Employee, lambda e: 0)  # Include all employees which are not assigned to any shift.
            .group_by(ConstraintCollectors.load_balance(lambda employee, shift_count: employee,
                                                        lambda employee, shift_count: shift_count))
            .penalize_decimal(HardSoftDecimalScore.ONE_SOFT, lambda load_balance: load_balance.unfairness())
            .as_constraint("Balance employee shift assignments")
            )


from datetime import date, datetime, time, timedelta
from itertools import product
from enum import Enum
from random import Random
from typing import Generator
from dataclasses import dataclass, field

from .domain import *


class DemoData(Enum):
    SMALL = 'SMALL'
    LARGE = 'LARGE'


@dataclass(frozen=True, kw_only=True)
class CountDistribution:
    count: int
    weight: float


def counts(distributions: tuple[CountDistribution, ...]) -> tuple[int, ...]:
    return tuple(distribution.count for distribution in distributions)


def weights(distributions: tuple[CountDistribution, ...]) -> tuple[float, ...]:
    return tuple(distribution.weight for distribution in distributions)


@dataclass(kw_only=True)
class DemoDataParameters:
    locations: tuple[str, ...]
    required_skills: tuple[str, ...]
    optional_skills: tuple[str, ...]
    days_in_schedule: int
    employee_count: int
    optional_skill_distribution: tuple[CountDistribution, ...]
    shift_count_distribution: tuple[CountDistribution, ...]
    availability_count_distribution: tuple[CountDistribution, ...]
    random_seed: int = field(default=37)


demo_data_to_parameters: dict[DemoData, DemoDataParameters] = {
    DemoData.SMALL: DemoDataParameters(
        locations=("Ambulatory care", "Critical care", "Pediatric care"),
        required_skills=("Doctor", "Nurse"),
        optional_skills=("Anaesthetics", "Cardiology"),
        days_in_schedule=14,
        employee_count=15,
        optional_skill_distribution=(
            CountDistribution(count=1, weight=3),
            CountDistribution(count=2, weight=1)
        ),
        shift_count_distribution=(
            CountDistribution(count=1, weight=0.9),
            CountDistribution(count=2, weight=0.1)
        ),
        availability_count_distribution=(
            CountDistribution(count=1, weight=4),
            CountDistribution(count=2, weight=3),
            CountDistribution(count=3, weight=2),
            CountDistribution(count=4, weight=1)
        ),
        random_seed=37
    ),

    DemoData.LARGE: DemoDataParameters(
        locations=("Ambulatory care",
                   "Neurology",
                   "Critical care",
                   "Pediatric care",
                   "Surgery",
                   "Radiology",
                   "Outpatient"),
        required_skills=("Doctor", "Nurse"),
        optional_skills=("Anaesthetics", "Cardiology", "Radiology"),
        days_in_schedule=28,
        employee_count=50,
        optional_skill_distribution=(
            CountDistribution(count=1, weight=3),
            CountDistribution(count=2, weight=1)
        ),
        shift_count_distribution=(
            CountDistribution(count=1, weight=0.5),
            CountDistribution(count=2, weight=0.3),
            CountDistribution(count=3, weight=0.2)
        ),
        availability_count_distribution=(
            CountDistribution(count=5, weight=4),
            CountDistribution(count=10, weight=3),
            CountDistribution(count=15, weight=2),
            CountDistribution(count=20, weight=1)
        ),
        random_seed=37
    )
}


FIRST_NAMES = ("Amy", "Beth", "Carl", "Dan", "Elsa", "Flo", "Gus", "Hugo", "Ivy", "Jay")
LAST_NAMES = ("Cole", "Fox", "Green", "Jones", "King", "Li", "Poe", "Rye", "Smith", "Watt")
SHIFT_LENGTH = timedelta(hours=8)
MORNING_SHIFT_START_TIME = time(hour=6, minute=0)
DAY_SHIFT_START_TIME = time(hour=9, minute=0)
AFTERNOON_SHIFT_START_TIME = time(hour=14, minute=0)
NIGHT_SHIFT_START_TIME = time(hour=22, minute=0)

SHIFT_START_TIMES_COMBOS = (
    (MORNING_SHIFT_START_TIME, AFTERNOON_SHIFT_START_TIME),
    (MORNING_SHIFT_START_TIME, AFTERNOON_SHIFT_START_TIME, NIGHT_SHIFT_START_TIME),
    (MORNING_SHIFT_START_TIME, DAY_SHIFT_START_TIME, AFTERNOON_SHIFT_START_TIME, NIGHT_SHIFT_START_TIME),
)


location_to_shift_start_time_list_map = dict()


def earliest_monday_on_or_after(target_date: date):
    """
    Returns the date of the next given weekday after
    the given date. For example, the date of next Monday.

    NB: if it IS the day we're looking for, this returns 0.
    consider then doing onDay(foo, day + 1).
    """
    days = (7 - target_date.weekday()) % 7
    return target_date + timedelta(days=days)


def generate_demo_data(demo_data_or_parameters: DemoData | DemoDataParameters) -> EmployeeSchedule:
    global location_to_shift_start_time_list_map, demo_data_to_parameters
    if isinstance(demo_data_or_parameters, DemoData):
        parameters = demo_data_to_parameters[demo_data_or_parameters]
    else:
        parameters = demo_data_or_parameters

    start_date = earliest_monday_on_or_after(date.today())
    random = Random(parameters.random_seed)
    shift_template_index = 0
    for location in parameters.locations:
        location_to_shift_start_time_list_map[location] = SHIFT_START_TIMES_COMBOS[shift_template_index]
        shift_template_index = (shift_template_index + 1) % len(SHIFT_START_TIMES_COMBOS)

    name_permutations = [f'{first_name} {last_name}'
                         for first_name, last_name in product(FIRST_NAMES, LAST_NAMES)]
    random.shuffle(name_permutations)

    employees = []
    for i in range(parameters.employee_count):
        count, = random.choices(population=counts(parameters.optional_skill_distribution),
                                weights=weights(parameters.optional_skill_distribution))
        skills = []
        skills += random.sample(parameters.optional_skills, count)
        skills += random.sample(parameters.required_skills, 1)
        employees.append(
            Employee(name=name_permutations[i],
                     skills=set(skills))
        )

    shifts: list[Shift] = []

    def id_generator():
        current_id = 0
        while True:
            yield str(current_id)
            current_id += 1

    ids = id_generator()

    for i in range(parameters.days_in_schedule):
        count, = random.choices(population=counts(parameters.availability_count_distribution),
                                weights=weights(parameters.availability_count_distribution))
        employees_with_availabilities_on_day = random.sample(employees, count)
        current_date = start_date + timedelta(days=i)
        for employee in employees_with_availabilities_on_day:
            rand_num = random.randint(0, 2)
            if rand_num == 0:
                employee.unavailable_dates.add(current_date)
            elif rand_num == 1:
                employee.undesired_dates.add(current_date)
            elif rand_num == 2:
                employee.desired_dates.add(current_date)
        shifts += generate_shifts_for_day(parameters, current_date, random, ids)

    shift_count = 0
    for shift in shifts:
        shift.id = str(shift_count)
        shift_count += 1

    return EmployeeSchedule(
        employees=employees,
        shifts=shifts
    )


def generate_shifts_for_day(parameters: DemoDataParameters, current_date: date, random: Random,
                            ids: Generator[str, any, any]) -> list[Shift]:
    global location_to_shift_start_time_list_map
    shifts = []
    for location in parameters.locations:
        shift_start_times = location_to_shift_start_time_list_map[location]
        for start_time in shift_start_times:
            shift_start_date_time = datetime.combine(current_date, start_time)
            shift_end_date_time = shift_start_date_time + SHIFT_LENGTH
            shifts += generate_shifts_for_timeslot(parameters, shift_start_date_time, shift_end_date_time,
                                                   location, random, ids)

    return shifts


def generate_shifts_for_timeslot(parameters: DemoDataParameters, timeslot_start: datetime, timeslot_end: datetime,
                                 location: str, random: Random, ids: Generator[str, any, any]) -> list[Shift]:
    shift_count, = random.choices(population=counts(parameters.shift_count_distribution),
                                  weights=weights(parameters.shift_count_distribution))

    shifts = []
    for i in range(shift_count):
        if random.random() >= 0.5:
            required_skill = random.choice(parameters.required_skills)
        else:
            required_skill = random.choice(parameters.optional_skills)
        shifts.append(Shift(
            id=next(ids),
            start=timeslot_start,
            end=timeslot_end,
            location=location,
            required_skill=required_skill))

    return shifts

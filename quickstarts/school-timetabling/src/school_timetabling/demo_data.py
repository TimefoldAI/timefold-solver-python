from enum import Enum
from datetime import time

from .domain import *


class DemoData(Enum):
    SMALL = 'SMALL'
    LARGE = 'LARGE'


def id_generator():
    current = 0
    while True:
        yield str(current)
        current += 1


def generate_demo_data(demo_data: DemoData) -> Timetable:
    ids = id_generator()
    days = (('MONDAY', 'TUESDAY') if demo_data == DemoData.SMALL
            else ('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'))
    timeslots = [
        Timeslot(id=next(ids),
                 day_of_week=day,
                 start_time=start,
                 end_time=start.replace(hour=start.hour + 1))
        for day in days
        for start in (time(8, 30), time(9, 30), time(10, 30), time(13, 30), time(14, 30))
    ]

    room_ids = (('A', 'B', 'C') if demo_data == DemoData.SMALL
                else ('A', 'B', 'C', 'D', 'E', 'F'))
    rooms = [Room(id=next(ids), name=f'Room {name}') for name in room_ids]

    lessons = []
    lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="Chemistry", teacher="M. Curie", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="Biology", teacher="C. Darwin", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="English", teacher="I. Jones", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="English", teacher="I. Jones", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="Spanish", teacher="P. Cruz", student_group="9th grade"))
    lessons.append(Lesson(id=next(ids), subject="Spanish", teacher="P. Cruz", student_group="9th grade"))
    if demo_data == DemoData.LARGE:
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="ICT", teacher="A. Turing", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Geography", teacher="C. Darwin", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Geology", teacher="C. Darwin", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="I. Jones", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Drama", teacher="I. Jones", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="9th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="9th grade"))

    lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="Chemistry", teacher="M. Curie", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="French", teacher="M. Curie", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="Geography", teacher="C. Darwin", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="10th grade"))
    lessons.append(Lesson(id=next(ids), subject="Spanish", teacher="P. Cruz", student_group="10th grade"))
    if demo_data == DemoData.LARGE:
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="ICT", teacher="A. Turing", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Biology", teacher="C. Darwin", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Geology", teacher="C. Darwin", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Drama", teacher="I. Jones", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="10th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="10th grade"))

        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="ICT", teacher="A. Turing", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Chemistry", teacher="M. Curie", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="French", teacher="M. Curie", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Geography", teacher="C. Darwin", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Biology", teacher="C. Darwin", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Geology", teacher="C. Darwin", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Spanish", teacher="P. Cruz", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Drama", teacher="P. Cruz", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="11th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="11th grade"))

        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Math", teacher="A. Turing", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="ICT", teacher="A. Turing", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Chemistry", teacher="M. Curie", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="French", teacher="M. Curie", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physics", teacher="M. Curie", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Geography", teacher="C. Darwin", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Biology", teacher="C. Darwin", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Geology", teacher="C. Darwin", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="History", teacher="I. Jones", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="English", teacher="P. Cruz", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Spanish", teacher="P. Cruz", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Drama", teacher="P. Cruz", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Art", teacher="S. Dali", student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="12th grade"))
        lessons.append(Lesson(id=next(ids), subject="Physical education", teacher="C. Lewis",
                              student_group="12th grade"))

    return Timetable(id=demo_data.name, timeslots=timeslots, rooms=rooms, lessons=lessons)

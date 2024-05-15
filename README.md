![Timefold Logo](https://raw.githubusercontent.com/TimefoldAI/timefold-solver/main/docs/src/modules/ROOT/images/shared/timefold-logo.png)

# Timefold Solver for Python

[![PyPI](https://img.shields.io/pypi/v/timefold-solver "PyPI")](https://pypi.org/project/timefold-solver/)

[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=timefold_solver_python&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=timefold_solver_python)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=timefold_solver_python&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=timefold_solver_python)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=timefold_solver_python&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=timefold_solver_python)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=timefold_solver_python&metric=coverage)](https://sonarcloud.io/summary/new_code?id=timefold_solver_python)

Timefold Solver is *an AI constraint solver for Python* to optimize
the Vehicle Routing Problem, Employee Rostering, Maintenance Scheduling, Task Assignment, School Timetabling,
Cloud Optimization, Conference Scheduling, Job Shop Scheduling, Bin Packing and many more planning problems.

Using Timefold Solver in Python is significantly slower than using Timefold Solver in Java or Kotlin.

## Requirements

- [Install Python 3.10 or later.](https://www.python.org)
- [Install JDK 17 or later](https://adoptium.net) with the environment variable `JAVA_HOME` configured to the JDK installation directory.

## Source code overview

### Domain

In Timefold Solver, the domain has three parts:

- Problem Facts, which do not change.
- Planning Entities, which have one or more planning variables.
- Planning Solution, which define the facts and entities of the problem.

#### Problem Facts

Problem facts can be any Python class, which are used to describe unchanging facts in your problem:

```python
from dataclasses import dataclass
from datetime import time

@dataclass
class Timeslot:
    id: int
    day_of_week: str
    start_time: time
    end_time: time
```

#### Planning Entities

To declare Planning Entities, use the `@planning_entity` decorator along with annotations:

```python
from dataclasses import dataclass, field
from typing import Annotated
from timefold.solver.domain import planning_entity, PlanningId, PlanningVariable

@planning_entity
@dataclass
class Lesson:
    id: Annotated[int, PlanningId]
    subject: str
    teacher: str
    student_group: str
    timeslot: Annotated[Timeslot, PlanningVariable] = field(default=None)
    room: Annotated[Room, PlanningVariable] = field(default=None)
```

- The `PlanningVariable` annotation is used to mark what fields the solver is allowed to change.

- The `PlanningId` annotation is used to uniquely identify an entity object of a particular class. The same Planning Id can be used on entities of different classes, but the ids of all entities in the same class must be different.

#### Planning Solution

To declare the Planning Solution, use the `@planning_solution` decorator:

```python
from dataclasses import dataclass, field
from typing import Annotated
from timefold.solver.domain import (planning_solution, ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningEntityCollectionProperty, PlanningScore)
from timefold.solver.score import HardSoftScore

@planning_solution
@dataclass
class TimeTable:
    timeslots: Annotated[list[Timeslot], ProblemFactCollectionProperty, ValueRangeProvider]
    rooms: Annotated[list[Room], ProblemFactCollectionProperty, ValueRangeProvider]
    lessons: Annotated[list[Lesson], PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)
```

- The `ValueRangeProvider` annotation is used to denote a field that contains possible planning values for a `PlanningVariable`.

- The`ProblemFactCollection` annotation is used to denote a field that contains problem facts. This allows these facts to be queried in your constraints.

- The `PlanningEntityCollection` annotation is used to denote a field that contains planning entities. The planning variables of these entities will be modified during solving. 

- The `PlanningScore` annotation is used to denote the field that holds the score of the current solution. The solver will set this field during solving.

### Constraints

You define your constraints by using the ConstraintFactory:

```python
from domain import Lesson
from timefold.solver.score import Joiners, HardSoftScore, constraint_provider

@constraint_provider
def define_constraints(constraint_factory):
    return [
        # Hard constraints
        room_conflict(constraint_factory),
        # Other constraints here...
    ]

def room_conflict(constraint_factory):
    # A room can accommodate at most one lesson at the same time.
    return constraint_factory.for_each_unique_pair(Lesson,
                # ... in the same timeslot ...
                Joiners.equal(lambda lesson: lesson.timeslot),
                # ... in the same room ...
                Joiners.equal(lambda lesson: lesson.room)) \
        .penalize("Room conflict", HardSoftScore.ONE_HARD)
```
for more details on Constraint Streams,
see https://timefold.ai/docs/timefold-solver/latest/constraints-and-score/score-calculation.

### Solve

```python
from timefold.solver import SolverFactory
from timefold.solver.config import SolverConfig, TerminationConfig, ScoreDirectorFactoryConfig, Duration
from constraints import define_constraints
from domain import TimeTable, Lesson, generate_problem

solver_config = SolverConfig(
    solution_class=TimeTable,
    entity_class_list=[Lesson],
    score_director_factory_config=ScoreDirectorFactoryConfig(
        constraint_provider_function=define_constraints
    ),
    termination_config=TerminationConfig(
        spent_limit=Duration(seconds=30)
    )
)

solver = SolverFactory.create(solver_config).build_solver()
solution = solver.solve(generate_problem())
```

`solution` will be a `TimeTable` instance with planning
variables set to the final best solution found.

## More information

For a full API spec, visit [the Timefold Documentation](https://timefold.ai/docs/timefold-solver/latest).

from timefold.solver import SolverStatus
from timefold.solver.score import HardSoftScore
from timefold.solver.domain import *

from datetime import datetime, timedelta
from typing import Annotated, Optional
from pydantic import Field, computed_field, BeforeValidator

from .json_serialization import *


LocationValidator = BeforeValidator(lambda location: location if isinstance(location, Location)
                                    else Location(latitude=location[0], longitude=location[1]))


class Location(JsonDomainBase):
    latitude: float
    longitude: float

    def driving_time_to(self, other: 'Location') -> int:
        return round((
             (self.latitude - other.latitude) ** 2 +
             (self.longitude - other.longitude) ** 2
         ) ** 0.5 * 4_000)

    def __str__(self):
        return f'[{self.latitude}, {self.longitude}]'

    def __repr__(self):
        return f'Location({self.latitude}, {self.longitude})'


@planning_entity
class Visit(JsonDomainBase):
    id: Annotated[str, PlanningId]
    name: str
    location: Annotated[Location, LocationSerializer, LocationValidator]
    demand: int
    min_start_time: datetime
    max_end_time: datetime
    service_duration: Annotated[timedelta, DurationSerializer]
    vehicle: Annotated[Optional['Vehicle'],
                       InverseRelationShadowVariable(source_variable_name='visits'),
                       IdSerializer, VehicleValidator, Field(default=None)]
    previous_visit: Annotated[Optional['Visit'],
                              PreviousElementShadowVariable(source_variable_name='visits'),
                              IdSerializer, VisitValidator, Field(default=None)]
    next_visit: Annotated[Optional['Visit'],
                          NextElementShadowVariable(source_variable_name='visits'),
                          IdSerializer, VisitValidator, Field(default=None)]
    arrival_time: Annotated[
        Optional[datetime],
        CascadingUpdateShadowVariable(target_method_name='update_arrival_time'),
        Field(default=None)]

    def update_arrival_time(self):
        if self.vehicle is None or (self.previous_visit is not None and self.previous_visit.arrival_time is None):
            self.arrival_time = None
        elif self.previous_visit is None:
            self.arrival_time = (self.vehicle.departure_time +
                                 timedelta(seconds=self.vehicle.home_location.driving_time_to(self.location)))
        else:
            self.arrival_time = (self.previous_visit.calculate_departure_time() +
                                 timedelta(seconds=self.previous_visit.location.driving_time_to(self.location)))

    def calculate_departure_time(self):
        if self.arrival_time is None:
            return None

        return max(self.arrival_time, self.min_start_time) + self.service_duration

    @computed_field
    @property
    def departure_time(self) -> Optional[datetime]:
        return self.calculate_departure_time()

    @computed_field
    @property
    def start_service_time(self) -> Optional[datetime]:
        if self.arrival_time is None:
            return None
        return max(self.arrival_time, self.min_start_time)

    def is_service_finished_after_max_end_time(self) -> bool:
        return self.arrival_time is not None and self.calculate_departure_time() > self.max_end_time

    def service_finished_delay_in_minutes(self) -> int:
        if self.arrival_time is None:
            return 0
        # Floor division always rounds down, so divide by a negative duration and negate the result
        # to round up
        # ex: 30 seconds / -1 minute = -0.5,
        # so 30 seconds // -1 minute = -1,
        # and negating that gives 1
        return -((self.calculate_departure_time() - self.max_end_time) // timedelta(minutes=-1))

    @computed_field
    @property
    def driving_time_seconds_from_previous_standstill(self) -> Optional[int]:
        if self.vehicle is None:
            return None

        if self.previous_visit is None:
            return self.vehicle.home_location.driving_time_to(self.location)
        else:
            return self.previous_visit.location.driving_time_to(self.location)

    def __str__(self):
        return self.id

    def __repr__(self):
        return f'Visit({self.id})'


@planning_entity
class Vehicle(JsonDomainBase):
    id: Annotated[str, PlanningId]
    capacity: int
    home_location: Annotated[Location, LocationSerializer, LocationValidator]
    departure_time: datetime
    visits: Annotated[list[Visit],
                      PlanningListVariable,
                      IdListSerializer, VisitListValidator, Field(default_factory=list)]

    @computed_field
    @property
    def arrival_time(self) -> datetime:
        if len(self.visits) == 0:
            return self.departure_time
        return (self.visits[-1].departure_time +
                timedelta(seconds=self.visits[-1].location.driving_time_to(self.home_location)))

    @computed_field
    @property
    def total_demand(self) -> int:
        return self.calculate_total_demand()

    @computed_field
    @property
    def total_driving_time_seconds(self) -> int:
        return self.calculate_total_driving_time_seconds()

    def calculate_total_demand(self) -> int:
        total_demand = 0
        for visit in self.visits:
            total_demand += visit.demand
        return total_demand

    def calculate_total_driving_time_seconds(self) -> int:
        if len(self.visits) == 0:
            return 0
        total_driving_time_seconds = 0
        previous_location = self.home_location

        for visit in self.visits:
            total_driving_time_seconds += previous_location.driving_time_to(visit.location)
            previous_location = visit.location

        total_driving_time_seconds += previous_location.driving_time_to(self.home_location)
        return total_driving_time_seconds

    def __str__(self):
        return self.id

    def __repr__(self):
        return f'Vehicle({self.id})'


@planning_solution
class VehicleRoutePlan(JsonDomainBase):
    name: str
    south_west_corner: Annotated[Location, LocationSerializer, LocationValidator]
    north_east_corner: Annotated[Location, LocationSerializer, LocationValidator]
    vehicles: Annotated[list[Vehicle], PlanningEntityCollectionProperty]
    visits: Annotated[list[Visit], PlanningEntityCollectionProperty, ValueRangeProvider]
    score: Annotated[Optional[HardSoftScore],
                     PlanningScore,
                     ScoreSerializer, ScoreValidator, Field(default=None)]
    solver_status: Annotated[Optional[SolverStatus],
                             Field(default=None)]

    @computed_field
    @property
    def total_driving_time_seconds(self) -> int:
        out = 0
        for vehicle in self.vehicles:
            out += vehicle.total_driving_time_seconds
        return out

    def __str__(self):
        return f'VehicleRoutePlan(name={self.id}, vehicles={self.vehicles}, visits={self.visits})'

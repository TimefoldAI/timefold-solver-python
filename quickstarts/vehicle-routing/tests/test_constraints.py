from timefold.solver.test import ConstraintVerifier

from vehicle_routing.domain import *
from vehicle_routing.constraints import *

from datetime import datetime

# LOCATION_1 to LOCATION_2 is sqrt(3**2 + 4**2) * 4000 == 20_000 seconds of driving time
# LOCATION_2 to LOCATION_3 is sqrt(3**2 + 4**2) * 4000 == 20_000 seconds of driving time
# LOCATION_1 to LOCATION_3 is sqrt(1**2 + 1**2) * 4000 == 5_656 seconds of driving time

LOCATION_1 = Location(latitude=0, longitude=0)
LOCATION_2 = Location(latitude=3, longitude=4)
LOCATION_3 = Location(latitude=-1, longitude=1)

DEPARTURE_TIME = datetime(2020, 1, 1)
MIN_START_TIME = DEPARTURE_TIME + timedelta(hours=2)
MAX_END_TIME = DEPARTURE_TIME + timedelta(hours=5)
SERVICE_DURATION = timedelta(hours=1)

constraint_verifier = ConstraintVerifier.build(define_constraints, VehicleRoutePlan, Vehicle, Visit)


def test_vehicle_capacity_unpenalized():
    vehicleA = Vehicle(id="1", capacity=100, home_location=LOCATION_1, departure_time=DEPARTURE_TIME)
    visit1 = Visit(id="2", name="John", location=LOCATION_2, demand=80,
                   min_start_time=MIN_START_TIME,
                   max_end_time=MAX_END_TIME,
                   service_duration=SERVICE_DURATION)
    connect(vehicleA, visit1)

    (constraint_verifier.verify_that(vehicle_capacity)
        .given(vehicleA, visit1)
        .penalizes_by(0))


def test_vehicle_capacity_penalized():
    vehicleA = Vehicle(id="1", capacity=100, home_location=LOCATION_1, departure_time=DEPARTURE_TIME)
    visit1 = Visit(id="2", name="John", location=LOCATION_2, demand=80,
                   min_start_time=MIN_START_TIME,
                   max_end_time=MAX_END_TIME,
                   service_duration=SERVICE_DURATION)
    visit2 = Visit(id="3", name="Paul", location=LOCATION_3, demand=40,
                   min_start_time=MIN_START_TIME,
                   max_end_time=MAX_END_TIME,
                   service_duration=SERVICE_DURATION)

    connect(vehicleA, visit1, visit2)

    (constraint_verifier.verify_that(vehicle_capacity)
        .given(vehicleA, visit1, visit2)
        .penalizes_by(20))


def test_service_finished_after_max_end_time_unpenalized():
    vehicleA = Vehicle(id="1", capacity=100, home_location=LOCATION_1, departure_time=DEPARTURE_TIME)
    visit1 = Visit(id="2", name="John", location=LOCATION_3, demand=80,
                   min_start_time=MIN_START_TIME,
                   max_end_time=MAX_END_TIME,
                   service_duration=SERVICE_DURATION)

    connect(vehicleA, visit1)

    (constraint_verifier.verify_that(service_finished_after_max_end_time)
     .given(vehicleA, visit1)
     .penalizes_by(0))


def test_service_finished_after_max_end_time_penalized():
    vehicleA = Vehicle(id="1", capacity=100, home_location=LOCATION_1, departure_time=DEPARTURE_TIME)
    visit1 = Visit(id="2", name="John", location=LOCATION_2, demand=80,
                   min_start_time=MIN_START_TIME,
                   max_end_time=MAX_END_TIME,
                   service_duration=SERVICE_DURATION)

    connect(vehicleA, visit1)

    # Service duration = 1 hour
    # Travel time ~= 5.5 hours
    # Max end time = 5 hours after vehicle departure
    # So (5.5 + 1) - 5 ~= 1.5 hours penalty, or about 90 minutes
    (constraint_verifier.verify_that(service_finished_after_max_end_time)
     .given(vehicleA, visit1)
     .penalizes_by(94))


def test_total_driving_time():
    vehicleA = Vehicle(id="1", capacity=100, home_location=LOCATION_1, departure_time=DEPARTURE_TIME,
                       min_start_time=MIN_START_TIME,
                       max_end_time=MAX_END_TIME,
                       service_duration=SERVICE_DURATION)
    visit1 = Visit(id="2", name="John", location=LOCATION_2, demand=80,
                   min_start_time=MIN_START_TIME,
                   max_end_time=MAX_END_TIME,
                   service_duration=SERVICE_DURATION)
    visit2 = Visit(id="3", name="Paul", location=LOCATION_3, demand=40,
                   min_start_time=MIN_START_TIME,
                   max_end_time=MAX_END_TIME,
                   service_duration=SERVICE_DURATION)

    connect(vehicleA, visit1, visit2)

    (constraint_verifier.verify_that(minimize_travel_time)
        .given(vehicleA, visit1, visit2)
        .penalizes_by(45657) # The sum of the approximate driving time between all three locations.
    )


def connect(vehicle: Vehicle, *visits: Visit):
    vehicle.visits = list(visits)
    for i in range(len(visits)):
        visit = visits[i]
        visit.vehicle = vehicle
        if i > 0:
            visit.previous_visit = visits[i - 1]

        if i < len(visits) - 1:
            visit.next_visit = visits[i + 1]
        visit.update_arrival_time()

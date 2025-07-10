from timefold.solver.score import ConstraintFactory, HardSoftScore, constraint_provider

from .domain import *

VEHICLE_CAPACITY = "vehicleCapacity"
MINIMIZE_TRAVEL_TIME = "minimizeTravelTime"
SERVICE_FINISHED_AFTER_MAX_END_TIME = "serviceFinishedAfterMaxEndTime"


@constraint_provider
def define_constraints(factory: ConstraintFactory):
    return [
        # Hard constraints
        vehicle_capacity(factory),
        service_finished_after_max_end_time(factory),
        # Soft constraints
        minimize_travel_time(factory)
    ]

##############################################
# Hard constraints
##############################################


def vehicle_capacity(factory: ConstraintFactory):
    return (factory.for_each(Vehicle)
            .filter(lambda vehicle: vehicle.calculate_total_demand() > vehicle.capacity)
            .penalize(HardSoftScore.ONE_HARD,
                      lambda vehicle: vehicle.calculate_total_demand() - vehicle.capacity)
            .as_constraint(VEHICLE_CAPACITY)
            )


def service_finished_after_max_end_time(factory: ConstraintFactory):
    return (factory.for_each(Visit)
            .filter(lambda visit: visit.is_service_finished_after_max_end_time())
            .penalize(HardSoftScore.ONE_HARD,
                      lambda visit: visit.service_finished_delay_in_minutes())
            .as_constraint(SERVICE_FINISHED_AFTER_MAX_END_TIME)
            )

##############################################
# Soft constraints
##############################################


def minimize_travel_time(factory: ConstraintFactory):
    return (
        factory.for_each(Vehicle)
        .penalize(HardSoftScore.ONE_SOFT,
                  lambda vehicle: vehicle.calculate_total_driving_time_seconds())
        .as_constraint(MINIMIZE_TRAVEL_TIME)
    )

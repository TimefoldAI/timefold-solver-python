from timefold.solver import SolverFactory
from timefold.solver.config import (SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration,
                                    TerminationCompositionStyle)

from employee_scheduling.rest_api import app
from employee_scheduling.domain import *

from fastapi.testclient import TestClient
from time import sleep
from pytest import fail

client = TestClient(app)


def test_feasible():
    demo_data_response = client.get("/demo-data/SMALL")
    assert demo_data_response.status_code == 200

    job_id_response = client.post("/schedules", json=demo_data_response.json())
    assert job_id_response.status_code == 200
    job_id = job_id_response.text[1:-1]

    ATTEMPTS = 1_000
    for _ in range(ATTEMPTS):
        sleep(0.1)
        schedule_response = client.get(f"/schedules/{job_id}")
        schedule_json = schedule_response.json()
        schedule = EmployeeSchedule.model_validate(schedule_json)
        if schedule.score is not None and schedule.score.is_feasible:
            stop_solving_response = client.delete(f"/schedules/{job_id}")
            assert stop_solving_response.status_code == 200
            return

    client.delete(f"/schedules/{job_id}")
    fail('solution is not feasible')

from vehicle_routing.rest_api import json_to_vehicle_route_plan, app

from fastapi.testclient import TestClient
from time import sleep
from pytest import fail

client = TestClient(app)


def test_feasible():
    demo_data_response = client.get("/demo-data/PHILADELPHIA")
    assert demo_data_response.status_code == 200

    job_id_response = client.post("/route-plans", json=demo_data_response.json())
    assert job_id_response.status_code == 200
    job_id = job_id_response.text[1:-1]

    ATTEMPTS = 1_000
    for _ in range(ATTEMPTS):
        sleep(0.1)
        route_plan_response = client.get(f"/route-plans/{job_id}")
        route_plan_json = route_plan_response.json()
        timetable = json_to_vehicle_route_plan(route_plan_json)
        if timetable.score is not None and timetable.score.is_feasible:
            stop_solving_response = client.delete(f"/route-plans/{job_id}")
            assert stop_solving_response.status_code == 200
            return

    client.delete(f"/route-plans/{job_id}")
    fail('solution is not feasible')

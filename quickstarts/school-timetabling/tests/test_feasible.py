from school_timetabling.rest_api import app
from school_timetabling.domain import *

from fastapi.testclient import TestClient
from time import sleep
from pytest import fail

client = TestClient(app)


def test_feasible():
    demo_data_response = client.get("/demo-data/SMALL")
    assert demo_data_response.status_code == 200

    job_id_response = client.post("/timetables", json=demo_data_response.json())
    assert job_id_response.status_code == 200
    job_id = job_id_response.text[1:-1]

    ATTEMPTS = 1_000
    for _ in range(ATTEMPTS):
        sleep(0.1)
        timetable_response = client.get(f"/timetables/{job_id}")
        timetable_json = timetable_response.json()
        timetable = Timetable.model_validate(timetable_json,
                                             context={
                                                 'rooms': {
                                                     room['id']: Room.model_validate(room)
                                                     for room in timetable_json.get('rooms', [])
                                                 },
                                                 'timeslots': {
                                                     timeslot['id']: Timeslot.model_validate(timeslot)
                                                     for timeslot in timetable_json.get('timeslots', [])
                                                 },
                                             })
        if timetable.score is not None and timetable.score.is_feasible:
            stop_solving_response = client.delete(f"/timetables/{job_id}")
            assert stop_solving_response.status_code == 200
            return

    client.delete(f"/timetables/{job_id}")
    fail('solution is not feasible')

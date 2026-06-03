from tests.conftest import register_user, auth_headers, create_job, create_slot

FUTURE_START = "2030-01-01T10:00:00"
FUTURE_END   = "2030-01-01T11:00:00"

def test_recruiter_can_create_slot(client):
    register_user(client, "Rec", "rec@test.com", "pass123", "recruiter")
    headers = auth_headers(client, "rec@test.com", "pass123")
    job = create_job(client, headers)
    job_id = job.json()["id"]
    res = create_slot(client, headers, job_id, FUTURE_START, FUTURE_END)
    assert res.status_code == 201
    assert res.json()["id"] is not None

def test_candidate_cannot_create_slot(client):
    register_user(client, "Rec", "rec@test.com", "pass123", "recruiter")
    register_user(client, "Can", "can@test.com", "pass123", "candidate")
    rec_headers = auth_headers(client, "rec@test.com", "pass123")
    can_headers = auth_headers(client, "can@test.com", "pass123")
    job = create_job(client, rec_headers)
    job_id = job.json()["id"]
    res = create_slot(client, can_headers, job_id, FUTURE_START, FUTURE_END)
    assert res.status_code == 403

def test_overlapping_slot_rejected(client):
    register_user(client, "Rec", "rec@test.com", "pass123", "recruiter")
    headers = auth_headers(client, "rec@test.com", "pass123")
    job = create_job(client, headers)
    job_id = job.json()["id"]
    create_slot(client, headers, job_id, FUTURE_START, FUTURE_END)
    res = create_slot(client, headers, job_id, FUTURE_START, FUTURE_END)
    assert res.status_code == 409
    assert "overlap" in res.json()["detail"].lower()
    
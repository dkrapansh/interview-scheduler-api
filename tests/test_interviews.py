from tests.conftest import (
    register_user, auth_headers, create_job, create_slot
)

FUTURE_START = "2030-06-01T10:00:00"
FUTURE_END   = "2030-06-01T11:00:00"


def _setup_booked_interview(client):
    """Helper: creates recruiter, candidate, job, slot, books it. Returns useful ids."""
    register_user(client, "Rec", "rec@test.com", "pass123", "recruiter")
    register_user(client, "Can", "can@test.com", "pass123", "candidate")

    rec_headers = auth_headers(client, "rec@test.com", "pass123")
    can_headers = auth_headers(client, "can@test.com", "pass123")

    job_id = create_job(client, rec_headers).json()["id"]
    slot_id = create_slot(client, rec_headers, job_id, FUTURE_START, FUTURE_END).json()["id"]

    res = client.post("/interviews/book", json={"slot_id": slot_id}, headers=can_headers)
    return res, slot_id, rec_headers, can_headers


def test_candidate_can_book_slot(client):
    res, _, _, _ = _setup_booked_interview(client)
    assert res.status_code == 201
    assert res.json()["status"] == "scheduled"


def test_double_booking_rejected(client):
    _, slot_id, _, _ = _setup_booked_interview(client)

    # Second candidate tries to book same slot
    register_user(client, "Can2", "can2@test.com", "pass123", "candidate")
    can2_headers = auth_headers(client, "can2@test.com", "pass123")
    res = client.post("/interviews/book", json={"slot_id": slot_id}, headers=can2_headers)
    assert res.status_code == 400
    assert "already booked" in res.json()["detail"].lower()


def test_candidate_can_cancel_own_interview(client):
    res, _, _, can_headers = _setup_booked_interview(client)
    interview_id = res.json()["id"]
    cancel_res = client.patch(f"/interviews/{interview_id}/cancel", headers=can_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"


def test_unrelated_user_cannot_cancel(client):
    res, _, _, _ = _setup_booked_interview(client)
    interview_id = res.json()["id"]

    # Third user — unrelated to this interview
    register_user(client, "Stranger", "stranger@test.com", "pass123", "candidate")
    stranger_headers = auth_headers(client, "stranger@test.com", "pass123")

    cancel_res = client.patch(f"/interviews/{interview_id}/cancel", headers=stranger_headers)
    assert cancel_res.status_code == 403
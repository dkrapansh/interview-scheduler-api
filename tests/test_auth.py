from tests.conftest import register_user, login
def test_register_success(client):
    res = register_user(client, "Alice", "alice@test.com", "pass123", "candidate")
    assert res.status_code == 201
    assert res.json()["email"] == "alice@test.com"

def test_register_duplicate_email(client):
    register_user(client, "Alice", "alice@test.com", "pass123", "candidate")
    res = register_user(client, "Alice2", "alice@test.com", "pass456", "candidate")
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"]

def test_login_success(client):
    register_user(client, "Alice", "alice@test.com", "pass123", "candidate")
    res = login(client, "alice@test.com", "pass123")
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_wrong_password(client):
    register_user(client, "Alice", "alice@test.com", "pass123", "candidate")
    res = login(client, "alice@test.com", "wrongpassword")
    assert res.status_code == 401


from app.core.security import hash_password
from app.models.user import User, UserRole


def _create_user(db_session, email="owner@test.com", password="Test@1234", role=UserRole.OWNER):
    user = User(
        name="Test Owner",
        email=email,
        password_hash=hash_password(password),
        role=role.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_with_correct_credentials_returns_a_token(client, db_session):
    _create_user(db_session)

    response = client.post("/auth/login", json={"email": "owner@test.com", "password": "Test@1234"})

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "OWNER"
    assert "access_token" in body


def test_login_with_wrong_password_returns_401(client, db_session):
    _create_user(db_session)

    response = client.post("/auth/login", json={"email": "owner@test.com", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"
    assert "request_id" in response.json()["error"]


def test_login_with_unknown_email_returns_401(client, db_session):
    response = client.post("/auth/login", json={"email": "nobody@test.com", "password": "whatever"})
    assert response.status_code == 401


def test_me_requires_a_token(client, db_session):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client, db_session):
    _create_user(db_session)
    login = client.post("/auth/login", json={"email": "owner@test.com", "password": "Test@1234"})
    token = login.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "owner@test.com"
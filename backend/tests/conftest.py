import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db_session):
    def _make(email: str, role: str, password: str = "Test@1234"):
        user = User(
            name=email.split("@")[0], email=email, password_hash=hash_password(password), role=role, is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _make


@pytest.fixture
def auth_headers(client, make_user):
    def _headers(email: str, role: str, password: str = "Test@1234"):
        make_user(email, role, password)
        login = client.post("/auth/login", json={"email": email, "password": password})
        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture
def override_ai_provider(client):
    """Overrides the get_ai_provider dependency, same mechanism as get_db —
    no monkeypatching internals. client's own teardown clears it."""
    from app.ai.provider import get_ai_provider
    from app.main import app as fastapi_app

    def _override(provider):
        fastapi_app.dependency_overrides[get_ai_provider] = lambda: provider

    return _override
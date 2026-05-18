import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Overrides get_db before importing app so it is applied correctly
from database import get_db


async def override_get_db():
    mock_session = AsyncMock()
    mock_result = MagicMock()

    # Configure synchronous chain return values
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_scalars.all.return_value = []

    mock_result.scalars.return_value = mock_scalars

    # Configure execute to return the mock_result coroutine
    mock_session.execute.return_value = mock_result

    # Configure commit/refresh to populate required fields
    async def mock_refresh(instance):
        instance.id = 1
        instance.created_at = datetime.utcnow()

    mock_session.refresh = mock_refresh
    yield mock_session


# Patch engine at module import time to prevent real DB connection in startup
mock_engine = MagicMock()
mock_begin_context = MagicMock()

# Setup mocks for 'async with engine.begin()'
async_enter = AsyncMock()
mock_begin_context.__aenter__ = async_enter
mock_begin_context.__aexit__ = AsyncMock()

mock_engine.begin.return_value = mock_begin_context

with patch('database.engine', mock_engine):
    from main import app
    app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch('main.publish_event', new_callable=AsyncMock)
def test_create_user(mock_publish, client):
    response = client.post(
        "/users", json={"name": "Test", "email": "test@example.com"})
    assert response.status_code in [200, 201]


def test_create_user_invalid(client):
    response = client.post("/users", json={"name": "Test"})
    assert response.status_code == 422


def test_list_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

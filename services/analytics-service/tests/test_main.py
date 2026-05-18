import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

# Overrides get_db before importing app so it is applied correctly
from database import get_db


async def override_get_db():
    mock_session = AsyncMock()
    mock_result = MagicMock()

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars

    # Configure scalar mock specifically for summary metrics calculation
    mock_result.scalar.return_value = 0
    mock_session.execute.return_value = mock_result

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


def test_summary(client):
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_orders" in data

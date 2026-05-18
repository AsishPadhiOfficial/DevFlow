import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app, get_db


async def override_get_db():
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalars().all.return_value = []
    mock_session.execute.return_value = mock_result
    yield mock_session

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def mock_db_engine():
    with patch('main.engine.begin', new_callable=AsyncMock):
        yield


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_notifications():
    response = client.get("/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

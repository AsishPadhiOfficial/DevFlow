import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app, get_db, user_service_cb


async def override_get_db():
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.scalars().all.return_value = []
    mock_session.execute.return_value = mock_result
    yield mock_session

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    with patch('database.engine.begin', new_callable=AsyncMock):
        with TestClient(app) as c:
            yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch('main.publish_event', new_callable=AsyncMock)
@patch.object(user_service_cb, 'call', new_callable=AsyncMock)
def test_create_order(mock_cb_call, mock_publish, client):
    response = client.post(
        "/orders", json={"user_id": 1, "product": "Test", "amount": 9.99})
    assert response.status_code in [200, 201]


def test_list_orders(client):
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

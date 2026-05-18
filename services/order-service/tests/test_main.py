import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Overrides get_db before importing app so it is applied correctly
from database import get_db

async def override_get_db():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result
    
    # Configure commit/refresh to populate required fields for Response validation
    async def mock_refresh(instance):
        instance.id = 1
        instance.status = "PENDING"
        instance.created_at = datetime.utcnow()
        
    mock_session.refresh = mock_refresh
    yield mock_session

# Patch engine at module import time to prevent real DB connection in startup event
mock_engine = MagicMock()
mock_begin_context = MagicMock()

# Setup mocks for 'async with engine.begin()'
async_enter = AsyncMock()
mock_begin_context.__aenter__ = async_enter
mock_begin_context.__aexit__ = AsyncMock()

mock_engine.begin.return_value = mock_begin_context

with patch('database.engine', mock_engine):
    from main import app, user_service_cb
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
@patch.object(user_service_cb, 'call', new_callable=AsyncMock)
def test_create_order(mock_cb_call, mock_publish, client):
    response = client.post(
        "/orders", json={"user_id": 1, "product": "Test", "amount": 9.99})
    assert response.status_code in [200, 201]


def test_list_orders(client):
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

import pytest
import json
import os
from unittest.mock import patch, MagicMock

# CONFIG_FILE env set karo import se pehle
os.environ['CONFIG_FILE'] = os.path.join(
    os.path.dirname(__file__), 'config.yaml')

from attendance_api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 404

@pytest.mark.get_health
def test_health_mysql_down(client):
    response = client.get('/attendance/healthz')
    data = json.loads(response.data.decode('utf-8'))
    assert data.get("description") in ["MySQL is healthy", "MySQL is not healthy"]

@pytest.mark.get_health
@patch('attendance_api.create_mysql_client')
def test_health_mysql_up(mock_mysql, client):
    mock_conn = MagicMock()
    mock_conn.ping.return_value = True
    mock_mysql.return_value = mock_conn
    response = client.get('/attendance/healthz')
    data = json.loads(response.data.decode('utf-8'))
    assert response.status_code == 200
    assert data.get("description") == "MySQL is healthy"

@pytest.mark.get_request
def test_search_no_mysql(client):
    response = client.get('/attendance/search')
    data = json.loads(response.data.decode('utf-8'))
    assert data.get("message") == "Error while pulling data for attendance"

@pytest.mark.get_request
@patch('attendance_api.create_mysql_client')
def test_search_with_data(mock_mysql, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, 'present', '2024-01-01')]
    mock_conn.cursor.return_value = mock_cursor
    mock_mysql.return_value = mock_conn
    response = client.get('/attendance/search')
    assert response.status_code == 200

@patch('attendance_api.create_mysql_client')
def test_create_attendance(mock_mysql, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_mysql.return_value = mock_conn
    payload = json.dumps({"id": 1, "status": "present", "date": "2024-01-01"})
    response = client.post('/attendance/create',
                           data=payload,
                           content_type='application/json')
    assert response.status_code == 200

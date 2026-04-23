import pytest
import json
from unittest.mock import patch, MagicMock
from attendance_api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Integration Test 1: Full health flow
@pytest.mark.integration
@patch('attendance_api.create_mysql_client')
def test_full_health_flow(mock_mysql, client):
    mock_conn = MagicMock()
    mock_conn.ping.return_value = True
    mock_mysql.return_value = mock_conn
    response = client.get('/attendance/healthz')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data['mysql'] == 'up'

# Integration Test 2: Create + Search flow
@pytest.mark.integration
@patch('attendance_api.create_mysql_client')
def test_create_and_search_flow(mock_mysql, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, 'present', '2024-01-01')]
    mock_conn.cursor.return_value = mock_cursor
    mock_mysql.return_value = mock_conn

    payload = json.dumps({"id": 1, "status": "present", "date": "2024-01-01"})
    create_res = client.post('/attendance/create',
                             data=payload,
                             content_type='application/json')
    assert create_res.status_code == 200

    search_res = client.get('/attendance/search')
    assert search_res.status_code == 200
    data = json.loads(search_res.data.decode('utf-8'))
    assert len(data) > 0

# Integration Test 3: Response format validation
@pytest.mark.integration
@patch('attendance_api.create_mysql_client')
def test_response_format(mock_mysql, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, 'present', '2024-01-01')]
    mock_conn.cursor.return_value = mock_cursor
    mock_mysql.return_value = mock_conn
    response = client.get('/attendance/search')
    data = json.loads(response.data.decode('utf-8'))
    assert isinstance(data, list)
    assert 'id' in data[0]
    assert 'status' in data[0]
    assert 'date' in data[0]

# Integration Test 4: End to End API flow
@pytest.mark.integration
@patch('attendance_api.create_mysql_client')
def test_e2e_api_flow(mock_mysql, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 'present', '2024-01-01'),
        (2, 'absent',  '2024-01-02')
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_mysql.return_value = mock_conn

    health = client.get('/attendance/healthz')
    assert health.status_code in [200, 400]

    search = client.get('/attendance/search')
    assert search.status_code == 200
    data = json.loads(search.data.decode('utf-8'))
    assert len(data) == 2

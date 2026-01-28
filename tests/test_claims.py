import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_claim_success(client):
    response = client.get('/claims/CLM-2024-001')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 'CLM-2024-001'
    assert data['status'] == 'open'

def test_get_claim_not_found(client):
    response = client.get('/claims/INVALID-ID')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
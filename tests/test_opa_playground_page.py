import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user'] = 'testuser'
        yield client

def test_opa_playground_route(client):
    """Test that the OPA Playground page is accessible and contains the iFrame."""
    response = client.get('/opa/playground')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert '<h1>OPA Playground</h1>' in html
    assert '<iframe src="https://play.openpolicyagent.org/"' in html
    assert 'width="100%"' in html
    assert 'height="600"' in html

def test_opa_playground_nav_link(client):
    """Test that the navigation link to OPA Playground exists in the base template."""
    response = client.get('/dashboard')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'href="/opa/playground"' in html
    assert 'OPA Playground' in html

def test_login_page_accessible(client):
    """Test that login page is accessible without auth"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Password' in response.data

def test_login_with_correct_password(client):
    """Test login with correct password"""
    response = client.post('/login', data={'password': 'testpass'}, follow_redirects=True)
    assert response.status_code == 200

def test_login_with_wrong_password(client):
    """Test login with incorrect password"""
    response = client.post('/login', data={'password': 'wrongpass'})
    assert b'Invalid password' in response.data

def test_homepage_requires_auth(client):
    """Test that homepage redirects to login without auth"""
    response = client.get('/')
    assert response.status_code == 302  # Redirect
    assert '/login' in response.location

def test_homepage_accessible_when_authenticated(authenticated_client):
    """Test that homepage is accessible when authenticated"""
    response = authenticated_client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_voting_page_requires_auth(client):
    """Test that voting page requires authentication"""
    response = client.get('/voting/bracket')
    assert response.status_code == 302

def test_voting_page_accessible_when_authenticated(authenticated_client):
    """Test that voting page is accessible when authenticated"""
    response = authenticated_client.get('/voting/bracket')
    assert response.status_code == 200
    assert b'Bracket' in response.data

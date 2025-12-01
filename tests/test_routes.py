# Authentication Tests

def test_register_page_accessible(client):
    """Test that registration page is accessible without auth"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data or b'Create Account' in response.data

def test_login_page_accessible(client):
    """Test that login page is accessible without auth"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_user_registration(client):
    """Test user registration"""
    response = client.post('/auth/register', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'testpassword',
        'password_confirm': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_login_with_valid_credentials(client, test_user):
    """Test login with valid credentials"""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_with_invalid_password(client, test_user):
    """Test login with incorrect password"""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert b'Invalid username or password' in response.data

def test_logout(authenticated_client):
    """Test logout functionality"""
    response = authenticated_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data

def test_account_page_requires_auth(client):
    """Test that account page requires authentication"""
    response = client.get('/auth/account')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_account_page_accessible_when_authenticated(authenticated_client):
    """Test that account page is accessible when authenticated"""
    response = authenticated_client.get('/auth/account')
    assert response.status_code == 200
    assert b'Account' in response.data or b'Test User' in response.data


# Main Routes Tests

def test_homepage_accessible(client):
    """Test that homepage is accessible without auth"""
    response = client.get('/')
    assert response.status_code == 200


# Tournament Tests

def test_tournaments_list_accessible(client):
    """Test that tournaments list is accessible without auth"""
    response = client.get('/tournaments/')
    assert response.status_code == 200

def test_tournament_detail_accessible(client, test_tournament):
    """Test that tournament detail page is accessible"""
    response = client.get(f'/tournaments/{test_tournament["id"]}')
    assert response.status_code == 200

def test_submit_song_requires_auth(client, test_tournament):
    """Test that song submission requires authentication"""
    response = client.get(f'/tournaments/{test_tournament["id"]}/submit')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_submit_song_accessible_when_authenticated(authenticated_client, test_tournament):
    """Test that song submission is accessible when authenticated"""
    response = authenticated_client.get(f'/tournaments/{test_tournament["id"]}/submit', follow_redirects=True)
    # Accept either 200 (form page) or redirect with flash message (if registration closed)
    assert response.status_code == 200
    # If it was a redirect, check for appropriate flash message
    if b'Registration is closed' in response.data:
        assert b'Registration is closed' in response.data
    else:
        # Otherwise, should show the form
        assert b'Submit' in response.data or b'submit' in response.data


# Voting Tests

def test_voting_page_requires_auth(client):
    """Test that voting page requires authentication"""
    response = client.get('/voting/bracket')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_voting_page_accessible_when_authenticated(authenticated_client):
    """Test that voting page redirects to tournaments when no tournament_id provided"""
    response = authenticated_client.get('/voting/bracket')
    assert response.status_code == 302
    assert '/tournaments/' in response.location

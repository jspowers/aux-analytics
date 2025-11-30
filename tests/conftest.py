import pytest
from app import create_app
from app.extensions import db
from app.models import User, Tournament

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            email='test@example.com',
            name='Test User'
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    # Return a dictionary of user data instead of the ORM object
    return {'id': user_id, 'email': 'test@example.com', 'password': 'testpassword'}

@pytest.fixture
def authenticated_client(client, test_user):
    """Create authenticated test client"""
    client.post('/auth/login', data={
        'email': test_user['email'],
        'password': test_user['password']
    })
    return client

@pytest.fixture
def test_tournament(app):
    """Create a test tournament"""
    with app.app_context():
        import time
        # Unix timestamps for test tournament
        now = int(time.time())
        seven_days = 7 * 24 * 60 * 60
        tournament = Tournament(
            tournament_code=Tournament.generate_unique_code(),
            name='Test Tournament 2025',
            description='A test tournament',
            year=2025,
            status='active',
            registration_deadline=now + seven_days,
            max_submissions_per_user=4,
            created_by_user_id=1
        )
        db.session.add(tournament)
        db.session.commit()
        tournament_id = tournament.id
        tournament_code = tournament.tournament_code
    # Return a dictionary with tournament data instead of the ORM object
    return {'id': tournament_id, 'name': 'Test Tournament 2025', 'code': tournament_code}

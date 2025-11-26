# Flask Testing Guidelines
- The instructions below are simplified testing practices for personal projects.

## Testing Framework
- Use pytest for testing (simple and powerful)
- Leverage Flask's test client for route testing
- Set up tests when adding new features, but don't stress over perfect coverage

## Basic Test Structure
```
tests/
├── conftest.py              # Shared test fixtures
├── test_routes.py           # Test your routes/endpoints
└── test_services.py         # Test business logic (optional)
```

## What to Test
- Critical user flows (authentication, main features)
- Business logic in services layer
- API endpoints (if building APIs)
- Don't worry about testing simple CRUD operations or framework code

## Basic Testing Pattern
- Use pytest fixtures for common setup (test client, test database)
- Write descriptive test names: `test_login_with_valid_credentials()`
- Follow arrange-act-assert pattern
- Keep tests simple and readable

## Fixtures (conftest.py)
Create basic fixtures you'll reuse:
- Test client fixture
- Test database fixture (if using database)
- Authenticated client fixture (if using auth)

## Running Tests
- Run with `pytest` command
- Add tests as you build features, not all at once
- Focus on testing what matters for your use cases
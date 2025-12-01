# Flask General Development Guidelines
- The instructions below are simplified guidelines for personal projects.

## Code Quality & Style
- Use clear, descriptive variable and function names
- Keep functions focused - if it's getting long, consider splitting it
- Add comments only where logic isn't obvious

## Flask Best Practices
- Use Flask-SQLAlchemy for database operations
- If model updates are required, ask before doing any operation that will reset/delete the database and EXPLICITLY WARN THE USER.
- If model updates are required, ask before doing any operation that will reset/delete the database and EXPLICITLY WARN THE USER.
- Use Flask's config object for configuration values
- Use environment variables for secrets (python-dotenv)
- Implement basic error handling (at least custom 404/500 pages)
- Add logging for debugging (especially in services layer)

## Dependencies & Environment
- Use virtual environment (venv)
- Maintain requirements.txt (can use `pip freeze > requirements.txt`)
- Keep .env.example updated when adding new environment variables

## When Writing Code
- Provide complete, runnable code
- Include necessary imports
- Suggest appropriate file locations based on the architecture (routes/, services/, models/)
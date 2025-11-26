# Flask Application Architecture
- The instructions below are general guidelines. They are meant to cover edge case requests and provide general direction. 

## Project Structure
Use this standard structure for Flask applications:
```
project/
├── app/
│   ├── __init__.py          # Application factory
│   ├── blueprints/          # Database models
│   │   ├── models/          # blueprint specific Database models
│   │   ├── routes/          # Blueprint route handlers
│   │   ├── services/        # blueprint specific Business logic layer
│   │   ├── forms/           # blueprint specific Business logic layer
|   │   ├── templates/       # blueprint specific Jinja2 templates
│   ├── models/              # global application models, if any
│   ├── static/              # Global CSS, JS, images for consistency
|   ├── templates/           # Base application Jinja2 templates
│   └── utils/               # Helper functions
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/             # Database migrations (Flask-Migrate)
├── config.py               # Configuration classes
├── wsgi.py                 # WSGI entry point
├── requirements.txt
└── .env
```

## Application Factory Pattern
Always use the application factory pattern:
- Create app instance in `app/__init__.py` using `create_app()`
- Register blueprints within the factory
- Load configuration based on environment

## Blueprint Organization
- Organize routes into blueprints by domain/feature
- Keep blueprint files focused (auth, api, main, admin, etc.)
- Register blueprints with URL prefixes for clarity
- Use blueprint-specific template folders when needed

## Configuration Management
- Create separate config classes: Development, Testing, Production
- Never hardcode configuration values in code
- Use environment variables for sensitive data
- Implement config validation on app startup

## Service Layer Pattern
- Keep route handlers thin - delegate to service layer
- Business logic goes in services/, not routes/
- Services should be testable without Flask context
- Return data structures from services, not Response objects
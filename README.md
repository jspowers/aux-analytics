# aux-analytics
Random projects from James Powers

## Overview
This is a container Flask application designed to hold multiple sub-applications. The goal is to consolidate infrastructure in one core project and rapidly produce new blueprints for different features.

## Architecture
The project follows a Flask blueprint and services architecture:
- **Blueprints** (`app/blueprints/`) - One blueprint per feature/sub-application
- **Services** - Business logic layer within each blueprint
- **Models** (`app/models/`) - Database models (to be added as needed)
- **Application Factory** - Clean app initialization with `create_app()`
- **Main Landing Page** - Entry point displaying all registered sub-applications

## Development Guidelines
Simplified development instructions are available in `.claude/instructions/`:
- **flask-architecture.md** - Project structure and organization patterns
- **flask-general.md** - General Flask development practices
- **flask-security.md** - Baseline security practices
- **flask-testing.md** - Testing guidelines with pytest
- **terraform-aws.md** - AWS EC2 deployment with Terraform

These guidelines are tailored for personal projects - keeping best practices while avoiding enterprise complexity.

## Getting Started

### Prerequisites
- Python 3.11 or higher
- pip

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your SECRET_KEY and other configuration

# Run the application
flask run
```

The application will be available at `http://localhost:5000`

### Project Structure
```
aux-analytics/
├── app/
│   ├── __init__.py              # Application factory
│   ├── blueprints/
│   │   └── main/                # Main landing page blueprint
│   │       ├── routes/          # Route handlers
│   │       ├── services/        # Business logic (AppRegistryService)
│   │       └── templates/       # Blueprint-specific templates
│   ├── static/
│   │   └── css/
│   │       └── custom.css       # Custom styles (Milligram CSS framework)
│   └── templates/
│       ├── base.html            # Base template
│       └── errors/              # Error pages (404, 500)
├── config.py                    # Configuration and SUB_APPS registry
├── wsgi.py                      # WSGI entry point
└── requirements.txt
```

## Adding New Sub-Applications

To add a new sub-application:

1. **Register the app in config.py:**
```python
SUB_APPS = [
    {
        'id': 'your-app',
        'name': 'Your Application Name',
        'description': 'Brief description of what your app does',
        'url_prefix': '/your-app',
        'icon': '🚀',  # Optional emoji or icon
        'enabled': True
    }
]
```

2. **Create a new blueprint:**
```bash
mkdir -p app/blueprints/your-app/{routes,services,templates}
touch app/blueprints/your-app/__init__.py
touch app/blueprints/your-app/routes/__init__.py
```

3. **Implement your blueprint routes:**
```python
# app/blueprints/your-app/routes/__init__.py
from flask import Blueprint, render_template

your_app_bp = Blueprint('your_app', __name__, url_prefix='/your-app')

@your_app_bp.route('/')
def index():
    return render_template('index.html')
```

4. **Register the blueprint in app/__init__.py:**
```python
from app.blueprints.your_app.routes import your_app_bp
app.register_blueprint(your_app_bp)
```

The new application will automatically appear on the landing page!

## Deployment
The application is designed to be deployed to AWS EC2 using Terraform. See `.claude/instructions/terraform-aws.md` for deployment instructions.

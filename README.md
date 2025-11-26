# aux-analytics
Random projects from James Powers

## Overview
This is a container Flask application designed to hold multiple sub-applications. The goal is to consolidate infrastructure in one core project and rapidly produce new blueprints for different features.

## Architecture
The project follows a Flask blueprint and services architecture:
- **Blueprints** (`app/routes/`) - One blueprint per feature/sub-application
- **Services** (`app/services/`) - Business logic layer
- **Models** (`app/models/`) - Database models
- **Application Factory** - Clean app initialization with `create_app()`

## Development Guidelines
Simplified development instructions are available in `.claude/instructions/`:
- **flask-architecture.md** - Project structure and organization patterns
- **flask-general.md** - General Flask development practices
- **flask-security.md** - Baseline security practices
- **flask-testing.md** - Testing guidelines with pytest
- **terraform-aws.md** - AWS EC2 deployment with Terraform

These guidelines are tailored for personal projects - keeping best practices while avoiding enterprise complexity.

## Getting Started
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
flask run
```

## Deployment
The application is designed to be deployed to AWS EC2 using Terraform. See `.claude/instructions/terraform-aws.md` for deployment instructions.

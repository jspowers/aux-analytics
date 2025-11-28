# aux-analytics
By James Powers

## Overview
Auxiliary Analytics is a song voting website for our annual Song Bracket Tournament. It utilizes a mixture of YouTube and Spotify API calls to serve links for individuals voting during the tournament and a vehicle to track and store votes that are placed during the tournament as well. 

## Architecture
The project follows a Flask blueprint and services architecture:
- **Blueprints** (`app/routes/`) - One blueprint per feature/sub-application
- **Services** (`app/services/`) - Business logic layer
- **Models** (`app/models/`) - Database models
- **Application Factory** - Clean app initialization with `create_app()`
- **UI Framework** - Spectre CSS for lightweight, modern styling
  - Core: `spectre.min.css` - Base styles and components
  - Experimental: `spectre-exp.min.css` - Advanced components
  - Icons: `spectre-icons.min.css` - Icon support

## Development Guidelines
Simplified development instructions are available in `.claude/instructions/`:
- **flask-architecture.md** - Project structure and organization patterns
- **flask-general.md** - General Flask development practices
- **flask-security.md** - Baseline security practices
- **flask-testing.md** - Testing guidelines with pytest
- **terraform-aws.md** - AWS EC2 deployment with Terraform

These guidelines are tailored for personal projects - keeping best practices while avoiding enterprise complexity.

## MVP Status

This is currently a minimal viable product with:
- Simple password-protected access (shared password)
- Homepage with project overview
- Interactive tournament bracket UI with round navigation
- Deployed to AWS EC2 with HTTPS

**What Works:**
- Infrastructure: EC2, Nginx, Gunicorn, SSL
- Authentication: Simple password protection
- Navigation: Homepage and voting bracket pages
- UI Framework: Spectre CSS for lightweight, responsive design
- Bracket Interface: Navigatable tournament rounds with tab-based navigation

**Coming Next:**
- SQLite database integration
- Backend voting functionality connected to UI
- YouTube/Spotify API integration
- User-specific voting (migrate to Flask-Login)

## Getting Started

### Local Development
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your APP_PASSWORD and SECRET_KEY

# Run tests
PYTHONPATH=. pytest -v

# Run development server
flask run
```

Visit `http://localhost:5000` and login with the password from your `.env` file.

## Deployment

### Production Deployment to AWS

Prerequisites:
- AWS account with Route53 hosted zone for auxanalytics.com
- SSH key pair created in AWS EC2
- GitHub repository with code pushed

Steps:
```bash
cd terraform

# Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values:
# - key_name: Your AWS SSH key pair name
# - app_password: Strong password for the site
# - secret_key: Generate with: python3 -c 'import secrets; print(secrets.token_hex(32))'
# - github_repo_url: Your GitHub repository URL
# - allowed_ssh_cidr: Your IP address (format: x.x.x.x/32)

# Deploy infrastructure
terraform init
terraform plan
terraform apply

# Wait 5-15 minutes for DNS propagation
# Visit https://auxanalytics.com
```

See `.claude/instructions/terraform-aws.md` for detailed deployment instructions.

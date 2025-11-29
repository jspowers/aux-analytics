# aux-analytics
By James Powers

## Overview
Auxiliary Analytics is a song voting website for our annual Song Bracket Tournament. It utilizes a mixture of YouTube and Spotify API calls to serve links for individuals voting during the tournament and a vehicle to track and store votes that are placed during the tournament as well. 

## Architecture
The project follows a Flask blueprint and services architecture:
- **Blueprints** (`app/blueprints/`) - One blueprint per feature:
  - `auth` - User registration, login, logout, account management
  - `main` - Homepage and general routes
  - `tournaments` - Tournament listing, details, and song submissions
  - `voting` - Voting bracket interface
- **Services** (`app/services/`) - External API integrations:
  - `spotify_service.py` - Spotify Web API for track metadata
  - `youtube_service.py` - YouTube Data API for video metadata
- **Models** (`app/models.py`) - SQLAlchemy database models:
  - User, Tournament, Round, Song, Matchup, Vote
- **Application Factory** - Clean app initialization with `create_app()`
- **Authentication** - Flask-Login for session-based user authentication
- **Database** - SQLite with Flask-SQLAlchemy and Flask-Migrate
- **UI Framework** - Bulma CSS for modern, responsive styling
  - Lightweight and mobile-first design
  - Card-based layout with key-value pair patterns
  - Flexible grid system

## Development Guidelines
Simplified development instructions are available in `.claude/instructions/`:
- **flask-architecture.md** - Project structure and organization patterns
- **flask-general.md** - General Flask development practices
- **flask-security.md** - Baseline security practices
- **flask-testing.md** - Testing guidelines with pytest
- **terraform-aws.md** - AWS EC2 deployment with Terraform

These guidelines are tailored for personal projects - keeping best practices while avoiding enterprise complexity.

## Current Features

**Authentication & User Management:**
- User registration with form validation
- Flask-Login session-based authentication
- Account page showing user info and song submissions
- Password hashing with Werkzeug

**Tournament System:**
- Tournament creation with:
  - Name and description
  - Registration deadline (date and time)
  - Voting start and end dates
  - Auto-set year to current year
  - Date validation (voting must be after registration, voting end after start)
  - Unix timestamp storage for all dates
- Tournament listing with status indicators
- Tournament details with submitted songs
- Song submission via:
  - Manual entry (title, artist, album)
  - Spotify URL with automatic metadata fetching
  - YouTube URL with automatic metadata fetching
- User can view their own submissions per tournament
- Registration deadline enforcement
- Round auto-generation based on song count (infrastructure ready)

**Database:**
- SQLite database with SQLAlchemy ORM
- Flask-Migrate for database migrations
- Models: User, Tournament, Round, Song, Matchup, Vote
- Proper relationships and constraints

**UI:**
- Bulma CSS framework
- Responsive, mobile-first design
- Card-based layouts with key-value pairs
- Unified auth template for login/register/account
- Flash message notifications

**Coming Next:**
- Bracket seeding and matchup generation
- Voting functionality
- Round progression logic
- Tournament administration and status management
- AWS deployment updates

## Getting Started

### Local Development

1. **Set up virtual environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration:
# - SECRET_KEY: Generate with: python3 -c 'import secrets; print(secrets.token_hex(32))'
# - DATABASE_URL: Default is sqlite:///app.db (good for development)
# - SPOTIFY_CLIENT_ID: Get from https://developer.spotify.com/dashboard
# - SPOTIFY_CLIENT_SECRET: Get from Spotify Developer Dashboard
# - YOUTUBE_API_KEY: Get from https://console.cloud.google.com/
```

4. **Initialize database:**
```bash
# Initialize migrations (only needed once)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations to create database
flask db upgrade
```

5. **Create a test user (optional):**
```bash
flask create-user
# Follow the prompts to create a user account
```

6. **Run tests:**
```bash
PYTHONPATH=. pytest -v
```

7. **Run development server:**
```bash
flask run
```

Visit `http://localhost:5000` in your browser. You can:
- Register a new account at `/auth/register`
- Login at `/auth/login`
- View tournaments at `/tournaments/`
- Access your account page at `/auth/account`

### API Keys Setup

**Spotify API:**
1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Copy the Client ID and Client Secret to your `.env` file

**YouTube API:**
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Copy the API key to your `.env` file

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

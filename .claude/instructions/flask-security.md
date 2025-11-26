# Flask Security Best Practices
- The instructions below are baseline security practices for personal projects.

## Critical Security Practices (Always Do These)

### Password & Authentication
- Use Flask-Login for session-based authentication
- Hash passwords with werkzeug.security (generate_password_hash, check_password_hash)
- Never store passwords in plain text
- Use @login_required decorator for protected routes

### SQL Injection Prevention
- Always use SQLAlchemy ORM (never build queries with string concatenation)
- Parameterize any raw SQL queries using SQLAlchemy's text() with bound parameters

### Secret Management
- Never commit secrets to version control
- Use environment variables for secrets (SECRET_KEY, DATABASE_URL, API keys)
- Add .env to .gitignore
- Provide .env.example with dummy values

### CSRF Protection
- Use Flask-WTF for automatic CSRF protection
- Include CSRF tokens in all forms that modify data

## Good Practices (Recommended)

### Input Validation
- Validate user inputs (Flask-WTF is simple and effective)
- Jinja2 auto-escapes by default (prevents XSS)
- Validate file uploads if accepting them (type, size)

### Error Handling
- Don't expose stack traces in production (set DEBUG=False)
- Implement basic custom error pages (404, 500)
- Log errors for debugging

### Production Deployment
- Use HTTPS in production (Let's Encrypt via Terraform setup)
- Set secure session cookies in production config
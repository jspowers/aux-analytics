# Terraform AWS EC2 Deployment for Flask Applications
- Simplified deployment instructions for personal Flask projects on AWS.

## Overview
Deploy Flask applications to AWS EC2:
- EC2 instance with Gunicorn WSGI server
- Nginx reverse proxy
- SSL with Let's Encrypt
- Basic security setup

## Terraform Project Structure
```
terraform/
├── main.tf                  # Main infrastructure definitions
├── variables.tf             # Input variables
├── outputs.tf               # Output values
├── terraform.tfvars         # Variable values (gitignored)
└── user-data.sh            # EC2 initialization script
```

## EC2 Instance Setup

### Instance Configuration
- Use Ubuntu LTS AMI (e.g., Ubuntu 22.04 or 24.04)
- Instance type: t3.micro (free tier) or t3.small for personal projects
- 20GB root volume
- Add tags for identification
- Use SSH key pair for access

### Security Group
Inbound rules:
- Port 22 (SSH) - restrict to your IP
- Port 80 (HTTP) - open to 0.0.0.0/0
- Port 443 (HTTPS) - open to 0.0.0.0/0

Outbound: Allow all (for package installation)

## User Data Script (user-data.sh)

The user data script should set up the server automatically:
1. Update system packages
2. Install Python 3, pip, venv
3. Install Nginx
4. Clone/copy application code
5. Install Python dependencies in virtualenv
6. Create systemd service for Gunicorn
7. Configure Nginx as reverse proxy
8. Set up SSL with Let's Encrypt (certbot)
9. Start services

## Gunicorn Configuration

### Systemd Service (`/etc/systemd/system/flask-app.service`)
- Run as non-root user (ubuntu or similar)
- Set working directory to app root
- Bind to Unix socket: `/run/gunicorn.sock`
- Workers: 3-4 (sufficient for personal projects)
- Configure auto-restart on failure
- Load environment variables from .env file

## Nginx Configuration

### Basic Setup
- Proxy requests to Gunicorn Unix socket
- Set proxy headers: Host, X-Real-IP, X-Forwarded-For, X-Forwarded-Proto
- Serve static files directly (don't proxy to Gunicorn)
- Set client_max_body_size for file uploads if needed

### SSL with Let's Encrypt
- Use certbot for free SSL certificates
- Redirect HTTP to HTTPS
- Certbot will auto-configure SSL settings

## Terraform Variables
Essential variables to define:
- `aws_region` - AWS region (e.g., us-east-1)
- `instance_type` - EC2 instance type (e.g., t3.micro)
- `key_name` - SSH key pair name
- `domain_name` - Your domain for the app (optional, for SSL)
- Environment variables for app (DATABASE_URL, SECRET_KEY, etc.)

## Terraform Outputs
Useful outputs:
- `instance_public_ip` - Public IP address
- `instance_public_dns` - Public DNS name

## State Management
- Store terraform.tfstate locally (gitignored) for personal projects
- For team projects, use S3 backend for remote state

## Deployment Process
```bash
terraform init
terraform plan
terraform apply
```

After deployment:
- SSH into instance to verify setup
- Check logs: `journalctl -u flask-app`
- Test your domain/IP in browser

## Key Security Practices
- Never commit terraform.tfvars (add to .gitignore)
- Use environment variables for secrets
- Keep SSH key secure
- Enable automatic security updates in user-data script
- Use HTTPS (Let's Encrypt setup in user-data)
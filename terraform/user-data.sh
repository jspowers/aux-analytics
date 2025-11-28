#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx

# Create application user
useradd -m -s /bin/bash flaskapp || true

# Clone application code
cd /home/flaskapp
git clone ${github_repo_url} app || (cd app && git pull)
cd app

# Set ownership
chown -R flaskapp:flaskapp /home/flaskapp

# Create virtual environment and install dependencies
sudo -u flaskapp python3 -m venv venv
sudo -u flaskapp /home/flaskapp/app/venv/bin/pip install --upgrade pip
sudo -u flaskapp /home/flaskapp/app/venv/bin/pip install -r requirements.txt

# Create .env file
cat > /home/flaskapp/app/.env << EOF
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=${secret_key}
APP_PASSWORD=${app_password}
DEBUG=False
EOF

chown flaskapp:flaskapp /home/flaskapp/app/.env
chmod 600 /home/flaskapp/app/.env

# Create Gunicorn systemd service
cat > /etc/systemd/system/flask-app.service << EOF
[Unit]
Description=Gunicorn instance for aux-analytics Flask app
After=network.target

[Service]
User=flaskapp
Group=www-data
WorkingDirectory=/home/flaskapp/app
Environment="PATH=/home/flaskapp/app/venv/bin"
EnvironmentFile=/home/flaskapp/app/.env
ExecStart=/home/flaskapp/app/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock wsgi:app

[Install]
WantedBy=multi-user.target
EOF

# Start and enable Gunicorn
systemctl daemon-reload
systemctl start flask-app
systemctl enable flask-app

# Configure Nginx
cat > /etc/nginx/sites-available/flask-app << 'NGINXEOF'
server {
    listen 80;
    server_name ${domain_name} www.${domain_name};

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/flaskapp/app/app/static;
    }
}
NGINXEOF

# Enable site
ln -sf /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx

# Wait for DNS propagation (give it a minute)
sleep 60

# Set up SSL with Let's Encrypt
certbot --nginx -d ${domain_name} -d www.${domain_name} --non-interactive --agree-tos --email admin@${domain_name} --redirect

# Enable auto-renewal
systemctl enable certbot.timer

echo "Deployment complete!"

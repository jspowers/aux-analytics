#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y python3 python3-pip python3-venv nginx git

# Create application directory
APP_DIR="/opt/${application_name}"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone application code (for now, we'll create a simple deployment)
# NOTE: In production, you'd clone from a git repository
# For this deployment, we'll need to manually upload the code after instance creation

# Create application user
useradd -r -s /bin/bash -d $APP_DIR ${application_name} || true
chown -R ${application_name}:${application_name} $APP_DIR

# Create virtual environment
sudo -u ${application_name} python3 -m venv $APP_DIR/venv

# Create environment file
cat > $APP_DIR/.env <<EOF
FLASK_APP=wsgi.py
FLASK_ENV=production
SECRET_KEY=${flask_secret_key}
DEBUG=False
EOF

chown ${application_name}:${application_name} $APP_DIR/.env
chmod 600 $APP_DIR/.env

# Create systemd service for Gunicorn
cat > /etc/systemd/system/${application_name}.service <<EOF
[Unit]
Description=Gunicorn instance for ${application_name}
After=network.target

[Service]
User=${application_name}
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/${application_name}.sock wsgi:app

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
cat > /etc/nginx/sites-available/${application_name} <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://unix:$APP_DIR/${application_name}.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $APP_DIR/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 10M;
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/${application_name} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Enable and start services
systemctl daemon-reload
systemctl enable ${application_name}
systemctl enable nginx
systemctl restart nginx

# Create deployment script for manual deployment
cat > $APP_DIR/deploy.sh <<'DEPLOY_EOF'
#!/bin/bash
set -e

APP_DIR="/opt/${application_name}"
cd $APP_DIR

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart ${application_name}

echo "Deployment complete!"
DEPLOY_EOF

chmod +x $APP_DIR/deploy.sh
chown ${application_name}:${application_name} $APP_DIR/deploy.sh

# Create README for deployment instructions
cat > $APP_DIR/DEPLOYMENT_README.md <<'README_EOF'
# Deployment Instructions

## Initial Deployment

1. Copy your application files to this server:
   ```
   scp -i ~/.ssh/aux-analytics-key -r /path/to/local/aux-analytics/* ubuntu@<instance-ip>:/tmp/app/
   ```

2. SSH into the server:
   ```
   ssh -i ~/.ssh/aux-analytics-key ubuntu@<instance-ip>
   ```

3. Move files to application directory:
   ```
   sudo cp -r /tmp/app/* /opt/${application_name}/
   sudo chown -R ${application_name}:${application_name} /opt/${application_name}
   ```

4. Deploy the application:
   ```
   cd /opt/${application_name}
   sudo -u ${application_name} ./deploy.sh
   ```

## Subsequent Deployments

Repeat steps 1-4 above.

## Useful Commands

- Check service status: `sudo systemctl status ${application_name}`
- View logs: `sudo journalctl -u ${application_name} -f`
- Restart service: `sudo systemctl restart ${application_name}`
- Check Nginx status: `sudo systemctl status nginx`
- View Nginx logs: `sudo tail -f /var/log/nginx/error.log`
README_EOF

chmod 644 $APP_DIR/DEPLOYMENT_README.md

echo "Server provisioning complete. Application files need to be deployed manually."
echo "See $APP_DIR/DEPLOYMENT_README.md for instructions."

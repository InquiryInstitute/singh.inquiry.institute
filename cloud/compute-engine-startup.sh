#!/bin/bash
# Startup script for Compute Engine VM to run Khan Academy download pipeline

set -e

echo "Starting Khan Academy download pipeline setup..."

# Update system
apt-get update
apt-get install -y python3-pip python3-venv git docker.io docker-compose

# Install Docker
systemctl start docker
systemctl enable docker
usermod -aG docker $USER

# Create application directory
APP_DIR="/opt/khan-academy-downloader"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository (or copy files)
# For now, we'll assume files are copied via startup script metadata
# In production, you'd clone from Git or use a custom image

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
mkdir -p data/videos data/transcripts data/metadata data/exercises

# Set up GCS credentials (if provided via metadata)
if [ -f "/tmp/gcs-credentials.json" ]; then
    mkdir -p ~/.config/gcloud
    cp /tmp/gcs-credentials.json ~/.config/gcloud/application_default_credentials.json
    export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/application_default_credentials.json
fi

# Create systemd service for the downloader
cat > /etc/systemd/system/khan-downloader.service <<EOF
[Unit]
Description=Khan Academy Video Downloader
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
Environment="GCS_BUCKET=khan-academy-videos"
ExecStart=$APP_DIR/venv/bin/python scripts/download_all.py --gcs-bucket khan-academy-videos
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service (optional - comment out if you want manual start)
# systemctl daemon-reload
# systemctl enable khan-downloader
# systemctl start khan-downloader

echo "Setup complete. To start the downloader, run:"
echo "  systemctl start khan-downloader"
echo "Or manually:"
echo "  cd $APP_DIR && source venv/bin/activate && python scripts/download_all.py --gcs-bucket khan-academy-videos"

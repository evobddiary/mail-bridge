#!/bin/bash

# MailDocker Update Script
# Pull latest changes and restart container

set -e

echo "Updating MailDocker..."

# Go to the repo directory
cd /mnt/user/appdata/mail-bridge

# Pull latest changes
git pull

# Run the startup script
cd docker
chmod +x start.sh
./start.sh

echo "MailDocker updated and restarted!"

#!/bin/bash

# MailDocker Simple Deployment Script for UNRAID
# This script handles everything needed to get MailDocker running

set -e

echo "========================================="
echo "  MailDocker UNRAID Deployment"
echo "========================================="

# Configuration
CONTAINER_NAME="mail-bridge"
IMAGE_NAME="mail-bridge:latest"
BASE_DIR="/mnt/user/appdata/mail-bridge"
DOCKER_DIR="/mnt/user/appdata/mail-bridge/docker"
CONFIG_DIR="/mnt/user/appdata/mail-bridge/docker/config"
MAILDATA_DIR="/mnt/user/appdata/mail-bridge/docker/maildata"
LOGS_DIR="/mnt/user/appdata/mail-bridge/docker/logs"
TEMPLATES_DIR="/mnt/user/appdata/mail-bridge/docker/templates"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running on UNRAID
if [ ! -d "/mnt/user" ]; then
    echo -e "${RED}Error: This script must be run on UNRAID server${NC}"
    exit 1
fi

# Navigate to the repo directory
cd "$BASE_DIR"

echo -e "${GREEN}Step 1: Pulling latest changes...${NC}"
git pull

echo -e "${GREEN}Step 2: Stopping existing container...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "Step 3: Creating directories..."
mkdir -p "$CONFIG_DIR" "$MAILDATA_DIR" "$LOGS_DIR" "$TEMPLATES_DIR"

# Copy templates if they don't exist
if [ ! -f "$CONFIG_DIR/accounts.yaml" ]; then
    echo "Creating accounts.yaml from template..."
    cp "$DOCKER_DIR/templates/accounts.yaml.template" "$CONFIG_DIR/accounts.yaml"
fi

if [ ! -f "$CONFIG_DIR/fetchmailrc" ]; then
    echo "Creating empty fetchmailrc..."
    touch "$CONFIG_DIR/fetchmailrc"
    chmod 600 "$CONFIG_DIR/fetchmailrc"
fi

echo -e "${GREEN}Step 4: Building Docker image...${NC}"
cd "$BASE_DIR/docker"
docker build -t $IMAGE_NAME .

echo -e "${GREEN}Step 5: Starting container...${NC}"
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p 8787:8787 \
    -p 143:143 \
    -p 993:993 \
    -v "$BASE_DIR/docker/config:/config" \
    -v "$BASE_DIR/docker/maildata:/maildata" \
    -v "$BASE_DIR/docker/logs:/logs" \
    -v "$BASE_DIR/docker/templates:/templates:ro" \
    -v "$BASE_DIR/docker/scripts:/scripts:ro" \
    -v "$BASE_DIR/docker/web:/app/web:ro" \
    $IMAGE_NAME

echo ""
echo -e "${GREEN}Step 6: Waiting for container to start...${NC}"
sleep 5

# Check if container is running
if docker ps | grep -q $CONTAINER_NAME; then
    UNRAID_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  MailDocker Started Successfully!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo -e "${YELLOW}Web Interface:${NC} http://$UNRAID_IP:8787"
    echo -e "${YELLOW}IMAP Server:${NC} $UNRAID_IP:143"
    echo ""
    echo -e "${YELLOW}Checking logs...${NC}"
    echo ""
    docker logs $CONTAINER_NAME --tail 15
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Open http://$UNRAID_IP:8787 in your browser"
    echo "2. Add your POP3 accounts"
    echo "3. Configure email filters"
    echo ""
    echo -e "${YELLOW}Useful commands:${NC}"
    echo "  View logs: docker logs $CONTAINER_NAME"
    echo "  Restart: docker restart $CONTAINER_NAME"
    echo "  Stop: docker stop $CONTAINER_NAME"
    echo -e "${GREEN}=========================================${NC}"
else
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}  Container failed to start!${NC}"
    echo -e "${RED}=========================================${NC}"
    echo ""
    echo -e "${YELLOW}Checking logs for errors...${NC}"
    echo ""
    docker logs $CONTAINER_NAME --tail 30
    echo ""
    echo -e "${RED}Please check the logs above for errors.${NC}"
    exit 1
fi

#!/bin/bash

# MailDocker UNRAID Startup Script
# This script builds and runs the MailDocker container on UNRAID

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="mail-bridge"
IMAGE_TAG="latest"
CONTAINER_NAME="mail-bridge"
WEB_PORT="8787"
IMAP_PORT="143"
IMAPS_PORT="993"

# Paths
BASE_DIR="/mnt/user/appdata/mail-bridge"
DOCKER_DIR="$BASE_DIR/docker"
CONFIG_DIR="$DOCKER_DIR/config"
MAILDATA_DIR="$DOCKER_DIR/maildata"
LOGS_DIR="$DOCKER_DIR/logs"
SCRIPTS_DIR="$DOCKER_DIR/scripts"
WEB_DIR="$DOCKER_DIR/web"

echo -e "${BLUE}========================================"
echo -e " MailDocker UNRAID Startup Script"
echo -e "========================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running on UNRAID
if [ ! -d "/mnt/user" ]; then
    print_error "This script must be run on UNRAID server"
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    print_error "Please enable Docker in UNRAID Settings → Docker"
    exit 1
fi

print_status "Docker is available"

# Check if we're in the right directory
if [ ! -f "$DOCKER_DIR/Dockerfile" ]; then
    print_error "Dockerfile not found in $DOCKER_DIR"
    print_error "Please run this script from the mail-bridge directory"
    exit 1
fi

print_status "Found Dockerfile in $DOCKER_DIR"

# Stop and remove existing container if it exists
if docker ps -a | grep -q $CONTAINER_NAME; then
    print_status "Stopping existing container..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    print_status "Removing existing container..."
    docker rm $CONTAINER_NAME 2>/dev/null || true
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p "$MAILDATA_DIR"
mkdir -p "$LOGS_DIR"
mkdir -p "$CONFIG_DIR"

# Fix permissions - only scripts should be executable
print_status "Setting permissions..."
chmod 644 "$DOCKER_DIR"/*.md "$DOCKER_DIR"/*.conf "$DOCKER_DIR"/*.yaml "$DOCKER_DIR"/*.yml "$DOCKER_DIR"/*.xml "$DOCKER_DIR"/Dockerfile* 2>/dev/null || true
chmod 755 "$DOCKER_DIR"/*.sh "$DOCKER_DIR"/scripts/*.py 2>/dev/null || true

# Build the Docker image
print_status "Building Docker image..."
cd "$DOCKER_DIR"
if ! ./build.sh; then
    print_error "Failed to build Docker image"
    exit 1
fi

print_status "Docker image built successfully"

# Run the container
print_status "Starting MailDocker container..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $WEB_PORT:8787 \
    -p $IMAP_PORT:143 \
    -p $IMAPS_PORT:993 \
    -v "$CONFIG_DIR:/config" \
    -v "$MAILDATA_DIR:/maildata" \
    -v "$LOGS_DIR:/logs" \
    -v "$SCRIPTS_DIR:/scripts:ro" \
    -v "$WEB_DIR:/app/web:ro" \
    $IMAGE_NAME:$IMAGE_TAG \
    /entrypoint.sh

# Check if container started successfully
sleep 3
if docker ps | grep -q $CONTAINER_NAME; then
    print_status "Container started successfully!"
    
    # Get UNRAID IP address
    UNRAID_IP=$(hostname -I | awk '{print $1}')
    
    echo -e "${GREEN}========================================"
    echo -e " MailDocker is now running!"
    echo -e "========================================${NC}"
    echo -e "${BLUE}Web Interface:${NC} http://$UNRAID_IP:$WEB_PORT"
    echo -e "${BLUE}IMAP Server:${NC} $UNRAID_IP:$IMAP_PORT"
    echo -e "${BLUE}IMAPS Server:${NC} $UNRAID_IP:$IMAPS_PORT"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "1. Open the web interface in your browser"
    echo -e "2. Add your POP3 accounts"
    echo -e "3. Set environment variables for passwords"
    echo -e "4. Test connections"
    echo -e "5. Connect your email client"
    echo ""
    echo -e "${YELLOW}To check logs:${NC} docker logs $CONTAINER_NAME"
    echo -e "${YELLOW}To stop container:${NC} docker stop $CONTAINER_NAME"
    echo -e "${YELLOW}To restart container:${NC} docker restart $CONTAINER_NAME"
    echo -e "${GREEN}========================================${NC}"
    
else
    print_error "Container failed to start!"
    echo -e "${RED}Check logs with: docker logs $CONTAINER_NAME${NC}"
    exit 1
fi

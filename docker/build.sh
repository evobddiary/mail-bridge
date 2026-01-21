#!/bin/sh

set -e

IMAGE_NAME="mail-bridge"
IMAGE_TAG="latest"

echo "========================================"
echo " Building Docker image: $IMAGE_NAME:$IMAGE_TAG"
echo "========================================"

# Проверка дали Dockerfile съществува
if [ ! -f Dockerfile ]; then
  echo "ERROR: Dockerfile not found in current directory"
  exit 1
fi

# Build
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo ""
echo "========================================"
echo " Build completed successfully"
echo " Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "========================================"

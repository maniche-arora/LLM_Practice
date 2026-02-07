#!/bin/bash

# Resume AI Agent - AWS EC2 Ubuntu Deployment Script
# Run this script on your Ubuntu EC2 instance to deploy the application

set -e  # Exit on error

echo "=========================================="
echo "Resume AI Agent - EC2 Deployment Script"
echo "=========================================="
echo ""

# Step 1: Update System
echo "Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install Docker
echo "Step 2: Installing Docker..."
sudo apt install -y docker.io docker-compose git curl

# Step 3: Enable Docker without sudo
echo "Step 3: Configuring Docker..."
sudo usermod -aG docker ubuntu
sudo systemctl start docker
sudo systemctl enable docker

# Step 4: Clone Repository
echo "Step 4: Cloning repository..."
cd /home/ubuntu
git clone https://github.com/maniche-arora/LLM_Practice.git
cd LLM_Practice

# Step 5: Create Environment File
echo "Step 5: Setting up environment..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: Please set OPENAI_API_KEY environment variable first"
    echo "Usage: export OPENAI_API_KEY='your-api-key' && bash deploy.sh"
    exit 1
fi

echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
echo "ENVIRONMENT=production" >> .env

# Step 6: Build Docker Image
echo "Step 6: Building Docker image..."
docker build -t resume-analyzer:latest .

# Step 7: Run Container
echo "Step 7: Starting application..."
docker-compose up -d

# Step 8: Verify
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Your application is running!"
echo ""
echo "Access it at:"
echo "http://$(ec2-metadata --public-ipv4 | cut -d " " -f 2):8501"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop app: docker-compose down"
echo "  Restart app: docker-compose restart"
echo ""

#!/bin/bash
# Vultr Deployment Script for Mad Ads Backend
# Run this script on your Vultr server after SSH connection

set -e  # Exit on error

echo "🚀 Starting Mad Ads Backend Deployment on Vultr..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install Git
echo -e "${YELLOW}📦 Installing Git...${NC}"
apt install git -y

# Install Docker
echo -e "${YELLOW}🐳 Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo -e "${YELLOW}🐳 Installing Docker Compose...${NC}"
apt install docker-compose-plugin -y

# Verify installations
echo -e "${GREEN}✅ Verifying installations...${NC}"
docker --version
docker compose version
git --version

# Clone repository
echo -e "${YELLOW}📥 Cloning repository...${NC}"
cd /opt
if [ -d "mad-ads-backend" ]; then
    echo "Directory exists, pulling latest changes..."
    cd mad-ads-backend
    git fetch origin
    git checkout deploy
    git pull origin deploy
else
    git clone https://github.com/kennethnrk/mad-ads.git mad-ads-backend
    cd mad-ads-backend
    git checkout deploy
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating template...${NC}"
    cat > .env << 'EOF'
# Frontend API URL - Update with your server IP
REACT_APP_API_URL=http://155.138.220.228:8000

# Add your environment variables below:
# SNOWFLAKE_ACCOUNT=your_account
# SNOWFLAKE_USER=your_user
# SNOWFLAKE_PASSWORD=your_password
# SNOWFLAKE_WAREHOUSE=your_warehouse
# SNOWFLAKE_DATABASE=your_database
# SNOWFLAKE_SCHEMA=your_schema
# SNOWFLAKE_CORTEX_SERVICE_NAME=product_search
# SNOWFLAKE_ACCOUNT_URL=your_account_url
# SNOWFLAKE_PAT=your_pat
# GEMINI_API_KEY=your_gemini_key
# ELEVENLABS_API_KEY=your_elevenlabs_key
# CLOUDINARY_CLOUD_NAME=your_cloud_name
# CLOUDINARY_API_KEY=your_api_key
# CLOUDINARY_API_SECRET=your_api_secret
EOF
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual credentials:${NC}"
    echo "   nano .env"
    echo "   Press any key to continue after editing..."
    read -n 1 -s
fi

# Configure firewall
echo -e "${YELLOW}🔥 Configuring firewall...${NC}"
ufw allow 22/tcp    # SSH
ufw allow 8000/tcp # Backend API
ufw allow 8001/tcp # Embedding Service
ufw allow 3000/tcp # Frontend
ufw --force enable

# Build and start containers
echo -e "${YELLOW}🏗️  Building and starting containers...${NC}"
docker compose up -d --build

# Wait a moment for containers to start
sleep 5

# Check status
echo -e "${GREEN}📊 Container Status:${NC}"
docker compose ps

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "🌐 Your application is now available at:"
echo "   Frontend:    http://155.138.220.228:3000"
echo "   Backend API: http://155.138.220.228:8000"
echo "   API Docs:    http://155.138.220.228:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs:    docker compose logs -f"
echo "   Stop:         docker compose down"
echo "   Restart:      docker compose restart"
echo "   Rebuild:      docker compose up -d --build"


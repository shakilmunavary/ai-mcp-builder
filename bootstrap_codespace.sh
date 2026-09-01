#!/usr/bin/env bash
# ==============================================================================
# All-in-One Codespaces Bootstrap & Environment Installer
# Works in both Recovery Mode and standard Devcontainers!
# ==============================================================================

set -e

echo "========================================================"
echo "      🚀 Bootstrapping AI DevOps Platform & Jenkins     "
echo "========================================================"

# 1. Install Docker if missing (Recovery Mode fix)
if ! command -v docker >/dev/null 2>&1; then
    echo "📦 Docker not found. Installing Docker CE..."
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm -f get-docker.sh
    sudo usermod -aG docker "$USER" 2>/dev/null || true
    echo "✅ Docker installed successfully!"
fi

# 2. Start Docker Service
echo "🐳 Ensuring Docker daemon is running..."
sudo service docker start 2>/dev/null || sudo systemctl start docker 2>/dev/null || sudo dockerd >/dev/null 2>&1 &
sleep 3

# Test Docker
if ! sudo docker info >/dev/null 2>&1; then
    echo "⚠️  Waiting for Docker daemon to become responsive..."
    sleep 3
fi

# 3. Setup Jenkins Container
echo "🏗️ Setting up Jenkins LTS container on Port 8080..."
if sudo docker ps -a --format '{{.Names}}' | grep -Eq "^jenkins$"; then
    echo "⚠️  Jenkins container already exists. Starting it..."
    sudo docker start jenkins >/dev/null 2>&1 || true
else
    echo "📦 Pulling and starting Jenkins container..."
    sudo docker run -d \
        --name jenkins \
        --restart unless-stopped \
        -p 8080:8080 \
        -p 50000:50000 \
        -v jenkins_home:/var/jenkins_home \
        jenkins/jenkins:lts-jdk17
fi

# 4. Install Python Dependencies
echo "🐍 Installing Python dependencies..."
if ! command -v pip3 >/dev/null 2>&1 && ! command -v pip >/dev/null 2>&1; then
    sudo apt-get install -y python3-pip python3-venv
fi

pip install --upgrade pip 2>/dev/null || sudo pip install --upgrade pip 2>/dev/null || pip3 install --upgrade pip 2>/dev/null || true
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt --break-system-packages 2>/dev/null || sudo pip install -r requirements.txt 2>/dev/null || true

# 5. Retrieve Jenkins Password
echo ""
echo "⏳ Waiting for Jenkins admin password to be generated..."
for i in {1..20}; do
    if sudo docker exec jenkins test -f /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null; then
        break
    fi
    sleep 2
done

if sudo docker exec jenkins test -f /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null; then
    ADMIN_PWD=$(sudo docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
    echo "========================================================"
    echo "🔑 Jenkins Initial Admin Password:"
    echo "--------------------------------------------------------"
    echo "$ADMIN_PWD"
    echo "--------------------------------------------------------"
    echo "🌐 Jenkins URL: http://localhost:8080"
    echo "========================================================"
fi

echo "========================================================"
echo "🎉 Bootstrap Complete! You can now start the portal:"
echo "👉 Run: ./start.sh"
echo "========================================================"

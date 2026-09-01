#!/usr/bin/env bash
# ==============================================================================
# Install Native Standalone Docker & Jenkins Service (Like WSL/Bare-Metal VM)
# ==============================================================================

set -e

echo "========================================================"
echo "  🚀 Installing Native Docker & Standalone Jenkins       "
echo "========================================================"

# Step 1: Install Native Docker CE
echo "📦 1/3: Installing Native Docker Engine..."
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release wget

if ! command -v docker >/dev/null 2>&1; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm -f get-docker.sh
fi

sudo usermod -aG docker "$USER" 2>/dev/null || true
echo "🐳 Starting Docker Service..."
sudo service docker start 2>/dev/null || sudo systemctl start docker 2>/dev/null || sudo dockerd >/dev/null 2>&1 &
sleep 2

# Verify Docker
if sudo docker ps >/dev/null 2>&1; then
    echo "✅ Native Docker is running on /var/run/docker.sock"
fi

# Step 2: Install Java 17 & Standalone Jenkins Service
echo "☕ 2/3: Installing OpenJDK 17 & Native Jenkins Service..."
sudo apt-get install -y openjdk-17-jdk openjdk-17-jre

if ! command -v jenkins >/dev/null 2>&1 && [ ! -f /usr/share/java/jenkins.war ]; then
    echo "🔑 Adding Jenkins official repository key..."
    sudo mkdir -p /usr/share/keyrings
    sudo wget -q -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
    echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y jenkins
fi

echo "🏗️ Starting Standalone Jenkins Service on Port 8080..."
sudo service jenkins start 2>/dev/null || sudo systemctl start jenkins 2>/dev/null || true

# Check if running; if not started via systemd/service, start background daemon
if ! pgrep -f "jenkins.war" >/dev/null 2>&1; then
    if [ -f /usr/share/java/jenkins.war ]; then
        echo "▶️ Launching standalone Jenkins daemon..."
        sudo nohup java -jar /usr/share/java/jenkins.war --httpPort=8080 > /tmp/jenkins.log 2>&1 &
    fi
fi

# Step 3: Install Python Dependencies
echo "🐍 3/3: Installing Python dependencies for AI DevOps Portal..."
sudo apt-get install -y python3-pip python3-venv
pip install --upgrade pip 2>/dev/null || pip3 install --upgrade pip 2>/dev/null || true
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt --break-system-packages 2>/dev/null || true

# Step 4: Wait & Retrieve Initial Admin Password
echo "⏳ Waiting for Jenkins initial admin password..."
for i in {1..20}; do
    if sudo test -f /var/lib/jenkins/secrets/initialAdminPassword 2>/dev/null; then
        break
    elif sudo test -f /root/.jenkins/secrets/initialAdminPassword 2>/dev/null; then
        break
    fi
    sleep 2
done

ADMIN_PWD=""
if sudo test -f /var/lib/jenkins/secrets/initialAdminPassword 2>/dev/null; then
    ADMIN_PWD=$(sudo cat /var/lib/jenkins/secrets/initialAdminPassword)
elif sudo test -f /root/.jenkins/secrets/initialAdminPassword 2>/dev/null; then
    ADMIN_PWD=$(sudo cat /root/.jenkins/secrets/initialAdminPassword)
fi

echo ""
echo "========================================================"
echo "🎉 Native Docker & Standalone Jenkins Installation Done!"
echo "========================================================"
echo "🐳 Docker Daemon:  /var/run/docker.sock (Running)"
echo "🏗️ Jenkins URL:    http://localhost:8080"
echo "👤 Username:       admin"
if [ -n "$ADMIN_PWD" ]; then
    echo "🔑 Initial Password:"
    echo "--------------------------------------------------------"
    echo "$ADMIN_PWD"
    echo "--------------------------------------------------------"
fi
echo "========================================================"
echo "👉 You can now start the AI DevOps Portal with: ./start.sh"
echo "========================================================"

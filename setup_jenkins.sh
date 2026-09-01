#!/usr/bin/env bash
# ==============================================================================
# All-in-One Codespace: Automated Jenkins Setup Script
# Launches official Jenkins LTS container on Port 8080
# ==============================================================================

echo "========================================================"
echo "          🏗️ Setting up Jenkins in Codespaces           "
echo "========================================================"

# 1. Verify Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Starting Docker daemon..."
    sudo service docker start 2>/dev/null || sudo systemctl start docker 2>/dev/null
    sleep 3
fi

# 2. Check if Jenkins container already exists
if docker ps -a --format '{{.Names}}' | grep -Eq "^jenkins$"; then
    echo "⚠️  Jenkins container already exists. Ensuring it is running..."
    docker start jenkins >/dev/null 2>&1
else
    echo "📦 Pulling and starting official Jenkins LTS container on port 8080..."
    docker run -d \
        --name jenkins \
        --restart unless-stopped \
        -p 8080:8080 \
        -p 50000:50000 \
        -v jenkins_home:/var/jenkins_home \
        jenkins/jenkins:lts-jdk17
fi

echo "⏳ Waiting for Jenkins to initialize (15-20 seconds)..."
for i in {1..30}; do
    if docker exec jenkins test -f /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null; then
        break
    fi
    sleep 2
done

# 3. Retrieve Initial Admin Password
if docker exec jenkins test -f /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null; then
    ADMIN_PWD=$(docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
    echo ""
    echo "========================================================"
    echo "✅ Jenkins is UP and RUNNING on Port 8080!"
    echo "========================================================"
    echo "🌐 Jenkins URL:    http://localhost:8080"
    echo "👤 Admin Username: admin"
    echo "🔑 Initial Password:"
    echo "--------------------------------------------------------"
    echo "$ADMIN_PWD"
    echo "--------------------------------------------------------"
    echo "💡 Note: You can open Port 8080 in the VS Code 'Ports' tab"
    echo "========================================================"
else
    echo "⚠️  Jenkins is still initializing. Check logs with: docker logs -f jenkins"
fi

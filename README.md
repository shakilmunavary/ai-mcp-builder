# 🚀 AI MCP Builder & Secured Gateway

An enterprise-grade, high-performance **Model Context Protocol (MCP) Gateway and Server Management Suite** designed for autonomous AI agents, developer tooling, and automated DevOps workflows.

---

## 🌟 Overview & Highlights

**AI MCP Builder** bridges the gap between Large Language Models (LLMs) and mission-critical enterprise engineering platforms (GitHub, Jenkins, AWS, Kubernetes, etc.) by providing:

* 🌐 **Dual-Port Architecture**:
  * **Port 5000 (`Web UI & Architect`)**: Interactive visual dashboard, AI server generator, real-time tool explorer, and schema validator.
  * **Port 5001 (`Secured MCP Gateway`)**: High-throughput JSON-RPC 2.0 reverse proxy routing tool invocations to local and remote MCP servers with bearer token authentication.
* 🛠️ **Pre-Integrated Enterprise Connectors**:
  * **GitHub MCP Server**: 40+ production tools supporting repository management, branching, commits, pull requests, issue tracking, and advanced pagination.
  * **Jenkins MCP Server**: 20+ CI/CD automation tools for triggering builds, reading console logs, inspecting build queues, managing plugins, and inspecting nodes.
* 🔒 **Security & Governance**:
  * Token-based bearer authentication on all JSON-RPC endpoints.
  * Resilient headless credential management with fallback protection.
  * Real-time tool dynamic reloading from disk without server downtime.
* 🤖 **AI-Assisted Server Generation**: Integrated Mistral AI engine to synthesize and scaffold new custom MCP tool definitions on the fly.

---

## 📐 System Architecture

```mermaid
graph TD
    Client[AI Agent / IDE / cURL Client]
    
    subgraph "AI MCP Builder Platform"
        UI["Web Dashboard & Architect (:5000)"]
        Gateway["Secured MCP JSON-RPC Gateway (:5001)"]
        Auth["Bearer Token Auth Engine"]
        Manager["Gateway Manager & Tool Loader"]
    end
    
    subgraph "Connected MCP Tool Servers"
        GH["GitHub Server (40+ Tools)"]
        JK["Jenkins Server (20+ Tools)"]
        Custom["Custom Stdio/SSE Servers"]
    end
    
    subgraph "External Cloud & Infra"
        GitHubCloud["GitHub REST / GraphQL API"]
        JenkinsHost["Jenkins CI/CD Automation Server"]
    end
    
    Client -->|HTTP / JSON-RPC| Gateway
    Client -->|Web Browser| UI
    Gateway --> Auth
    Auth --> Manager
    Manager --> GH
    Manager --> JK
    Manager --> Custom
    GH --> GitHubCloud
    JK --> JenkinsHost
```

---

## 📂 Directory Structure

```text
ai-mcp-builder/
├── app.py                     # Main Flask Application & Web Dashboard (:5000)
├── gateway_manager.py         # Secured JSON-RPC 2.0 MCP Gateway (:5001)
├── mistral_service.py         # AI Prompt & Server Generation Engine
├── platform_specs.py          # Platform specs & tool templates
├── config.json                # Server registry & configuration store
├── requirements.txt           # Python dependency specifications
├── start.sh                   # 1-Click Background Daemon Start Script
├── stop.sh                    # Graceful Shutdown Script
├── app.pid                    # Daemon process tracker
├── app.log                    # Server execution logs
├── templates/                 # Web Dashboard UI templates
└── mcp_servers/               # Modular MCP Server Implementations
    ├── github/                # GitHub MCP Server (server.py, .env)
    └── jenkins_mcp/           # Jenkins MCP Server (server.py, .env)
```

---

## ⚡ Quick Start

### 1. Prerequisites
* Python 3.10 or higher
* Ubuntu / WSL2 / Linux / macOS / Windows
* Git

### 2. Start in Background
Run the startup script:
```bash
./start.sh
```

**Output**:
```text
========================================================
          🚀 Starting MCP Gateway Daemon                
========================================================
▶️  Launching app.py in background...
✅ MCP Gateway started successfully in background!
🆔 PID:     582
📄 Log:     ai-mcp-builder/app.log
🌐 Web UI:  http://localhost:5000
🔒 Gateway: http://localhost:5001
========================================================
```

### 3. Check Live Logs
```bash
tail -f app.log
```

### 4. Stop the Daemon
```bash
./stop.sh
```

---

## 📡 API & Usage Examples

### 1. Health Check
```bash
curl -s http://localhost:5001/health
```
**Response**:
```json
{
  "gateway": "AI MCP Server Kit Gateway",
  "status": "online",
  "port": 5001,
  "auth_required": true,
  "protocol": "mcp/jsonrpc-2.0"
}
```

### 2. List All Active MCP Servers & Tools
```bash
curl -s http://localhost:5000/api/servers
```

### 3. Invoke GitHub Tool (`list_repos`) with Pagination
```bash
curl -s -X POST http://localhost:5001/mcp/github \
  -H "Authorization: Bearer mcp_live_key_dev_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "list_repos",
      "arguments": {
        "per_page": 10,
        "page": 1,
        "sort": "updated",
        "direction": "desc"
      }
    }
  }'
```

### 4. Trigger Jenkins Job (`trigger_build`)
```bash
curl -s -X POST http://localhost:5001/mcp/jenkins_mcp \
  -H "Authorization: Bearer mcp_live_key_dev_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "trigger_build",
      "arguments": {
        "job_name": "devops-vsp-sample-app-build",
        "parameters": {
          "ENVIRONMENT": "production"
        }
      }
    }
  }'
```

---

## 🔐 Configuration & Secrets

Each MCP server contains its own isolated `.env` configuration inside `mcp_servers/<server_name>/.env`:

* **GitHub Server** (`mcp_servers/github/.env`):
  ```env
  GITHUB_TOKEN=your_github_personal_access_token
  GITHUB_ORG=your_username_or_org
  GITHUB_BASE_URL=https://api.github.com
  ```

* **Jenkins Server** (`mcp_servers/jenkins_mcp/.env`):
  ```env
  BASE_URL=http://localhost:8080
  USERNAME=admin
  AUTH_HEADER=your_jenkins_api_token
  ```

---

## 📄 License
This project is licensed under the MIT License.

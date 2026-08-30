# 🌐 AI DevOps Value Stream Portal
### *Autonomous SRE AI Agent Platform with Model Context Protocol (MCP) & Mistral AI*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-JSON--RPC%202.0-8b5cf6.svg)](https://modelcontextprotocol.io/)
[![Mistral AI](https://img.shields.io/badge/LLM-Mistral%20AI-orange.svg)](https://mistral.ai/)
[![ServiceNow](https://img.shields.io/badge/ITSM-ServiceNow%20Table%20API-green.svg)](https://www.servicenow.com/)
[![Docker](https://img.shields.io/badge/Containers-Docker%20Engine-2496ED.svg)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/CI%2FCD-Jenkins%20Automation-D24939.svg)](https://www.jenkins.io/)
[![GitHub](https://img.shields.io/badge/VCS-GitHub%20Enterprise-181717.svg)](https://github.com/)

---

## 📖 Table of Contents
1. [🌟 Executive Summary & Vision](#-executive-summary--vision)
2. [📐 System Architecture & Data Flow](#-system-architecture--data-flow)
3. [🚀 Key Features & Capabilities](#-key-features--capabilities)
4. [🖼️ Visual Walkthrough & System Tour](#️-visual-walkthrough--system-tour)
5. [🔬 Case Study: Autonomous Incident Detection, RCA & Self-Healing](#-case-study-autonomous-incident-detection-rca--self-healing)
6. [💻 Installation & Quickstart](#-installation--quickstart)
7. [⚙️ Configuration & Environment Setup](#️-configuration--environment-setup)
8. [🔒 Security, Governance & Extensibility](#-security-governance--extensibility)
9. [🗺️ Roadmap & Future Enhancements](#️-roadmap--future-enhancements)

---

## 🌟 Executive Summary & Vision

Modern Site Reliability Engineering (SRE) and DevOps teams face severe **alert fatigue**, **fragmented monitoring silos**, and **high Mean Time to Resolution (MTTR)**. When an application in production or staging encounters a database violation or runtime crash, engineers are forced to manually:
1. SSH into servers or pull container logs.
2. Triage complex, multi-page stack traces.
3. Cross-reference recent Git commits and Jenkins pipeline runs.
4. Manually open and update IT Service Management (ITSM) tickets in ServiceNow.

**AI DevOps Value Stream Portal** revolutionizes this workflow by combining Anthropic's open **Model Context Protocol (MCP)**, **Mistral AI Large Language Models**, and **Autonomous Agent Orchestration**. The platform automatically detects exceptions, performs deterministic root-cause analysis (RCA), deduplicates incidents, updates ServiceNow work notes with remediation code, and resolves tickets autonomously without human intervention.

---

## 📐 System Architecture & Data Flow

```mermaid
flowchart TD
    subgraph "Target Infrastructure & Workloads"
        DockerApp["🐳 Containerized App (devops-vsp-sample-app)"]
        JenkinsHost["🏗️ Jenkins CI/CD (devops-vsp-pipeline)"]
        GitHubRepo["🐙 GitHub Repository (devops-vsp-sample-app)"]
        SNOWHost["📋 ServiceNow ITSM (dev392242)"]
    end

    subgraph "AI DevOps Value Stream Portal Platform"
        UI["🌐 Web UI & Builder Dashboard (:5000)"]
        Gateway["🔒 High-Throughput JSON-RPC MCP Gateway (:5001)"]
        
        subgraph "Modular MCP Server Drivers"
            MCP_Docker["🐳 Docker MCP Driver (UNIX Socket)"]
            MCP_GH["🐙 GitHub MCP Driver (PAT / REST)"]
            MCP_JK["🏗️ Jenkins MCP Driver (API / Crumb)"]
            MCP_SNOW["📋 ServiceNow Driver (Table API & Journal)"]
        end

        subgraph "AI Core & Autonomous Engine"
            Architect["🤖 Mistral Interactive Bot Architect"]
            AgentRunner["⚡ Autonomous Workflow Engine"]
            DedupEngine["🛡️ Stateful SHA-256 Error Deduplication"]
            MistralRCA["🧠 Mistral AI Root Cause Analyzer"]
        end
    end

    DockerApp -->|Logs Stream| AgentRunner
    AgentRunner -->|Check Hash| DedupEngine
    AgentRunner -->|Request Context| Gateway
    Gateway --> MCP_Docker
    Gateway --> MCP_GH
    Gateway --> MCP_JK
    Gateway --> MCP_SNOW

    MCP_Docker --> DockerApp
    MCP_GH --> GitHubRepo
    MCP_JK --> JenkinsHost
    MCP_SNOW --> SNOWHost

    AgentRunner -->|Raw Stack Trace| MistralRCA
    MistralRCA -->|Structured RCA Report| AgentRunner
    AgentRunner -->|Create & Update Ticket (Work Notes)| MCP_SNOW
```

---

## 🚀 Key Features & Capabilities

### 1. 🤖 Interactive Natural Language Bot Architect
* **Zero Hardcoding**: Create customized autonomous bots dynamically through interactive conversations with Mistral AI.
* **Live Blueprint Synthesis**: Real-time extraction of target containers, GitHub repositories, Jenkins jobs, intervals, and trigger rules into executable Python workflows (`workflow.py`).

### 2. 🛡️ Stateful SHA-256 Error Deduplication
* **Anti-Flooding Protection**: Automatically fingerprints stack traces using normalized SHA-256 hashing.
* **Persistent Memory**: Historical errors across container restarts or continuous polling cycles are tracked to ensure ServiceNow is never spammed with duplicate tickets.

### 3. 🧠 Precision Error Stripping & Mistral AI RCA
* **Token-Efficient Log Truncation**: Isolates root database exceptions (e.g. `SqlExceptionHelper: Value too long for column NAME (VARCHAR 255)`) from multi-hundred-line Spring Boot stack traces.
* **Actionable Remediation**: Produces structured RCA reports including *Incident Title*, *Root Cause*, *Affected Entity/Component*, *Severity*, and *Step-by-step JPA/Schema Code Corrections*.

### 4. 📋 Native ServiceNow Table API & Work Notes Enrichment
* Direct integration with ServiceNow's native Table API (`/api/now/table/incident/{sys_id}`).
* Writes non-intrusive progress updates into `work_notes` journal fields:
  * **Phase 1**: Initial triage notice (*"SRE AI agent is analyzing the issue"* + stripped error block).
  * **Phase 2**: Full Mistral AI RCA audit report + automatic closure transition (`state: 6`, `close_code: Solution Provided`).

### 5. 💬 Platform AI Assistant (Universal MCP Chat)
* Real-time conversational interface connected to your live MCP Gateway.
* Query across all tools instantly: *"List my GitHub repositories"*, *"Show active Docker containers"*, *"Inspect Jenkins pipeline status"*, or *"Query recent ServiceNow incidents"*.

---

## 🖼️ Visual Walkthrough & System Tour

### 1. 📊 AI DevOps Value Stream Portal Dashboard
*The central command center displaying connected MCP servers (**Docker**, **GitHub**, **Jenkins**, **ServiceNow**), active transports, live Gateway endpoint routes, credential vaults, and tool function schemas with instant cURL test commands:*

<p align="center">
  <img src="docs/images/01_portal_mcp_servers.png" alt="AI DevOps Value Stream Portal Dashboard" width="95%" />
</p>

---

### 2. 🤖 Interactive Conversational MCP Server Architect
*Prompting Mistral AI interactively to scaffold custom enterprise MCP server suites with natural language:*

<p align="center">
  <img src="docs/images/02_interactive_architect_prompt.png" alt="Interactive MCP Architect Prompt" width="90%" />
</p>

---

### 3. ⚡ Automated Tool Synthesis & Schema Generation
*Mistral AI analyzes platform specifications and automatically synthesizes functional tools (Query, Action, Monitoring, Admin) with complete parameter definitions and toggle controls:*

<p align="center">
  <img src="docs/images/03_jenkins_tools_synthesized.png" alt="Jenkins Tools Synthesized" width="90%" />
</p>

---

### 4. 🚀 1-Click FastMCP Deployment & Credential Vault Setup
*Reviewing generated parameters, auto-configuring `.env` credentials, and deploying the newly generated FastMCP server directly onto the live Gateway (:5001):*

<p align="center">
  <img src="docs/images/04_deploy_fastmcp_server.png" alt="Deploy FastMCP Server" width="90%" />
</p>

---

### 5. 🔑 Secure Mistral AI Configuration
*Configuring enterprise LLM credentials securely to empower interactive bot synthesis and precision Root Cause Analysis:*

<p align="center">
  <img src="docs/images/05_mistral_key_config.png" alt="Mistral AI API Key Configuration" width="80%" />
</p>

---

### 6. 💬 Platform AI Assistant in Action (Real-Time MCP Query)
*Interacting with the universal conversational assistant to inspect live container status and runtime diagnostics via the Docker MCP driver:*

<p align="center">
  <img src="docs/images/06_platform_assistant_chat.png" alt="Platform AI Assistant Chat" width="90%" />
</p>

---

### 7. 🤖 Autonomous Bots Dashboard
*Monitoring active autonomous watchdogs, executed workflow counters, registered SRE bots, and one-click execution controls:*

<p align="center">
  <img src="docs/images/07_autonomous_bots_dashboard.png" alt="DevOps Autonomous Bots Dashboard" width="95%" />
</p>

---

### 8. 📜 Real-Time Execution Telemetry & Health Checks
*Live execution modal tracking continuous background health checks, container log inspection, error signature isolation, and AI RCA reports:*

<p align="center">
  <img src="docs/images/08_bot_execution_telemetry.png" alt="Bot Execution Telemetry" width="90%" />
</p>

---

### 9. 🧠 Interactive AI Bot Builder (Discovery & Validation)
*Building brand new autonomous SRE workflows through conversational discovery and live MCP tool capability validation:*

<p align="center">
  <img src="docs/images/09_bot_architect_modal.png" alt="Interactive AI Bot Architect Modal" width="90%" />
</p>

---

## 🔬 Case Study: Autonomous Incident Detection, RCA & Self-Healing

### The Scenario:
A user submitted a long dashboard URL (`http://localhost:7000/dashboard...` with 651 characters) into a Spring Boot user management application (`devops-vsp-sample-app`), triggering an unhandled database exception:

```text
2026-08-30T12:37:40.571Z ERROR 1 --- [nio-7000-exec-4] o.h.engine.jdbc.spi.SqlExceptionHelper : 
Value too long for column "NAME CHARACTER VARYING(255)": "'http://localhost:7000/dashboard...' (651)"; 
SQL statement: insert into "user" (email,name,id) values (?,?,default) [22001-214]
```

### The Autonomous SRE Loop:
1. 🔍 **Log Capture**: Bot stripped the core error signature from 350+ lines of container logs.
2. 🛡️ **Deduplication Check**: Computed SHA-256 fingerprint and checked ServiceNow for duplicate open tickets.
3. 🐙 **Correlation**: Identified linked GitHub repo `shakilmunavary/devops-vsp-sample-app` and Jenkins build `devops-vsp-pipeline`.
4. 📋 **Ticket Creation**: Created ServiceNow Incident `INC0010062` with initial status:
   * **Work Notes**: `SRE AI agent is analyzing the issue. === STRIPPED ERROR LOG ===`
5. 🧠 **Mistral AI RCA**: Synthesized root cause and recommended code fix:
   * **Root Cause**: Field length constraint violation on column `NAME` (`VARCHAR(255)`).
   * **Recommended Fix**: Add `@Size(max=255)` validation annotation to `User.java` and expand column schema to `VARCHAR(1000)`.
6. 🏁 **Auto-Resolution**: Updated `INC0010062` work notes with the complete RCA markdown and resolved the incident (`state: 6`).

---

## 💻 Installation & Quickstart

### Prerequisites
* **OS**: Linux, Ubuntu, macOS, or Windows (via WSL2)
* **Python**: `3.10` or higher
* **Docker Engine**: Installed and running
* **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/shakilmunavary/ai-mcp-builder.git
cd ai-mcp-builder
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Credentials (`.env`)
Create per-server credentials under `mcp_servers/<server_name>/.env` or export environment variables:
```bash
# Mistral AI Key
export MISTRAL_API_KEY="your-mistral-api-key"

# ServiceNow Instance
export BASE_URL="https://your-instance.service-now.com"
export USERNAME="mcp_admin"
export PASSWORD="your-password"

# GitHub Enterprise / Cloud
export ACCESS_TOKEN="github_pat_your_token"
export ORGANIZATION="your-org-or-username"

# Jenkins Server
export JENKINS_URL="http://localhost:8080"
export JENKINS_USERNAME="admin"
export JENKINS_API_TOKEN="your-jenkins-token"
```

### 4. Launch Background Daemon
```bash
chmod +x start.sh stop.sh
./start.sh
```

**Output**:
```text
========================================================
          🚀 Starting MCP Gateway Daemon                
========================================================
▶️  Launching app.py in background...
✅ MCP Gateway started successfully in background!
🆔 PID:     12783
📄 Log:     app.log
🌐 Web UI:  http://localhost:5000
🔒 Gateway: http://localhost:5001
========================================================
```

---

## ⚙️ Configuration & Environment Setup

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `MISTRAL_API_KEY` | *(Required)* | API key for Mistral AI LLM synthesis and RCA generation. |
| `GATEWAY_PORT` | `5001` | High-throughput JSON-RPC 2.0 reverse proxy port for MCP tools. |
| `WEB_UI_PORT` | `5000` | Web dashboard & interactive bot builder interface. |
| `DOCKER_HOST_URL` | `unix:///var/run/docker.sock` | Docker daemon socket URI. |
| `GATEWAY_API_KEY` | `mcp-gateway-secret-key-2026` | Bearer token required for all JSON-RPC `:5001` requests. |

---

## 🔒 Security, Governance & Extensibility

* **Token-Based Gateway Authentication**: All MCP tool executions require an `Authorization: Bearer <KEY>` or `X-API-Key` header.
* **Per-Server Isolation**: Each MCP server is encapsulated with its own credential context and tool scope.
* **Zero Hot-Reload Downtime**: Add or update tool drivers on disk without restarting the Gateway daemon.
* **Journal Integrity in ITSM**: Uses non-destructive work notes updates rather than overwriting original customer ticket descriptions.

---

## 🗺️ Roadmap & Future Enhancements

- [x] **Universal MCP Reverse Proxy** (`:5001`) with FastMCP JSON-RPC support.
- [x] **Interactive Conversational Bot Architect** with Mistral AI.
- [x] **ServiceNow Table API & Journal Field Integration**.
- [x] **SHA-256 Stateful Deduplication** for alert storm suppression.
- [ ] **Kubernetes MCP Driver**: Pod log monitoring, automated rollbacks, and crash-loop triage.
- [ ] **AWS & CloudWatch Integration**: Automatic Lambda and ECS anomaly correlation.
- [ ] **Slack / MS Teams Webhooks**: Direct incident resolution notifications with interactive approval buttons.

---

## 🤝 Contributing
Contributions, feedback, and feature requests are welcome! Feel free to check the [Issues page](https://github.com/shakilmunavary/ai-mcp-builder/issues) or submit a Pull Request.

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  <b>Built with ❤️ for modern Site Reliability Engineers and DevOps teams.</b>
</p>

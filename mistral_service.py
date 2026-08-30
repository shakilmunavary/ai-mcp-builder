"""
Mistral AI Service - Interactive Multi-Turn MCP Architect with Context & Memory
Provides deterministic tool synthesis, multi-turn design conversations, and schema customization.
"""

import os
import json
import logging
import uuid
import httpx
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv



logger = logging.getLogger("mistral_service")

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
# Using codestral-latest or mistral-large-latest for optimal code and tool synthesis
DEFAULT_MISTRAL_MODEL = os.environ.get("MISTRAL_MODEL", "codestral-latest")

AUTH_CREDENTIAL_PARAM_NAMES = {
    "token", "api_token", "github_token", "jenkins_token", "password", "passwd",
    "secret", "api_key", "secret_key", "base_url", "url", "jenkins_url",
    "instance_url", "crumb", "csrf_crumb", "access_key", "secret_access_key",
    "bearer_token", "private_key", "pat", "client_secret"
}


def get_mistral_api_key() -> Optional[str]:
    load_dotenv(override=True)
    return os.environ.get("MISTRAL_API_KEY", "").strip() or None


def set_mistral_api_key(api_key: str) -> None:
    api_key = api_key.strip()
    os.environ["MISTRAL_API_KEY"] = api_key
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MISTRAL_API_KEY="):
                    lines.append(f"MISTRAL_API_KEY={api_key}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"MISTRAL_API_KEY={api_key}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    logger.info("Updated MISTRAL_API_KEY in environment and .env")


SYSTEM_ARCHITECT_PROMPT = """You are the Lead Enterprise Model Context Protocol (MCP) Architect.
You collaborate with developers to dynamically architect, review, synthesize, and continuously self-evaluate COMPREHENSIVE, END-TO-END production-grade FastMCP servers for ANY platform, tool, or API (e.g. Datadog, Splunk, Jira, ServiceNow, GitHub, GitLab, Kubernetes, Cloudflare, PagerDuty, Salesforce, or proprietary REST APIs).

YOUR ARCHITECTURAL & SELF-EVALUATION MANDATES:

1. AUTONOMOUS SELF-EVALUATION ON EVERY PROMPT:
   - On EVERY user prompt or question, self-evaluate all requirements:
     * Check if the service operates under an Organization, Workspace, Project, Tenant, or Account (e.g. GitHub Org/Owner, Jira Domain/Project, ServiceNow Instance URL, AWS Region/Account, Datadog Site). If so, MANDATE it in "fields".
     * Check if the tool suite is comprehensive (16 to 25 tools) covering all 4 core layers (Query, Action, Monitoring, Admin).
     * Check that all tool HTTP methods and endpoints match real-world API specifications.
     * Check that connection credentials (Tokens, Passwords, Keys, Base URLs) are strictly isolated in "fields" and NEVER in tool "params".
   - In your conversational "reply", explicitly share the self-evaluation summary and explain your design choices.

2. COMPREHENSIVE END-TO-END TOOL SUITES (16 TO 25 TOOLS):
   - You MUST cover all 4 functional pillars:
     * 🔍 Query & Read (6-8 tools): list collections with filters/pagination, get single item details by ID, search by query string, inspect metadata, filter by state/tag.
     * ⚡ Action & Mutation (6-8 tools): create entities, update records, delete/archive items, execute actions, batch operations, assign ownership, trigger workflows.
     * 📊 Monitoring & Observability (3-5 tools): stream/fetch logs, check service health/status, pull performance metrics, audit event history, inspect alerts.
     * 🛡️ Admin & Governance (2-4 tools): manage user roles/permissions, inspect system info/version, validate licenses, update configurations.

3. CONTINUOUS TWO-WAY CONVERSATION AT ANY STAGE:
   - Always be ready to interact, explain, answer questions, or refine fields and tools at ANY point in the lifecycle.
   - When the user asks a question (e.g. "you did not ask organization", "why do we need this field?", "add a tool for X"), address their concern directly in "reply" and update the JSON specification accordingly.
   - When modifying tools or fields, preserve the existing suite and apply exact modifications without dropping valid tools.

OUTPUT FORMAT (STRICT VALID JSON ONLY):
{
  "is_valid": true,
  "reply": "Conversational architectural reply explaining your self-evaluation, answering the developer's question, and detailing the full suite.",
  "platform_id": "snake_case_id",
  "platform_name": "Human Readable Platform Name",
  "category": "Domain Category (e.g. Observability, Security, ITSM, CI/CD, Source Control, Cloud)",
  "description": "Comprehensive description of this enterprise MCP server",
  "fields": [
    {
      "key": "field_key_name",
      "label": "Human Readable Label",
      "prompt": "Conversational prompt asking for this value",
      "placeholder": "https://api.service.com or organization name or token...",
      "default": "",
      "secret": true,
      "required": true
    }
  ],
  "tools": [
    {
      "name": "snake_case_tool_name",
      "category": "Query | Action | Monitoring | Admin",
      "description": "Clear description of what this tool accomplishes",
      "method": "GET | POST | PUT | DELETE | PATCH",
      "endpoint": "/exact/api/endpoint/path",
      "params": {
        "domain_param_name": "type (required/optional) - parameter description"
      },
      "sample_args": {
        "domain_param_name": "sample_value"
      },
      "example_call": "tool_name(domain_param_name='sample_value')"
    }
  ]
}

When user input is completely invalid / random gibberish:
{
  "is_valid": false,
  "reply": "I could not recognize '**<input>**' as a known software platform, service, or API. Please specify a valid system or provide your API schema.",
  "tools": [],
  "fields": []
}
"""


def sanitize_tool_parameters(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Strips accidental connection credentials from tool schemas.
    """
    cleaned_tools = []
    for t in tools:
        t_copy = dict(t)
        raw_params = t_copy.get("params", {}) or {}
        raw_sample = t_copy.get("sample_args", {}) or {}

        clean_params = {}
        clean_sample = {}

        if isinstance(raw_params, dict):
            for p_name, p_desc in raw_params.items():
                p_lower = p_name.lower()
                if p_lower in AUTH_CREDENTIAL_PARAM_NAMES or any(k in p_lower for k in ["_token", "_password", "_url", "_crumb", "_secret", "api_key", "_api_key"]):
                    continue
                clean_params[p_name] = p_desc

        if isinstance(raw_sample, dict):
            for s_name, s_val in raw_sample.items():
                s_lower = s_name.lower()
                if s_lower in AUTH_CREDENTIAL_PARAM_NAMES or any(k in s_lower for k in ["_token", "_password", "_url", "_crumb", "_secret", "api_key", "_api_key"]):
                    continue
                clean_sample[s_name] = s_val

        t_copy["params"] = clean_params
        t_copy["sample_args"] = clean_sample
        cleaned_tools.append(t_copy)
    return cleaned_tools


class ArchitectSession:
    """Represents an active multi-turn design session with state and memory."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[Dict[str, str]] = []
        self.current_spec: Optional[Dict[str, Any]] = None

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Keep last 12 messages for rich context
        if len(self.messages) > 12:
            self.messages = self.messages[-12:]

    def get_state(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "spec": self.current_spec,
            "message_count": len(self.messages)
        }


class SessionManager:
    """In-memory session registry for persistent multi-turn conversations."""
    def __init__(self):
        self._sessions: Dict[str, ArchitectSession] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> ArchitectSession:
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())[:8]
            self._sessions[new_id] = ArchitectSession(new_id)
            return self._sessions[new_id]
        return self._sessions[session_id]

    def reset(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


session_mgr = SessionManager()


def chat_with_mcp_architect(session_id: Optional[str], user_message: str) -> Dict[str, Any]:
    """
    100% Dynamic Live Mistral AI Architect:
    - NO hardcoded intercepts or cached blueprints.
    - Every user request goes directly to Mistral AI (Codestral / Mistral Large) to reason and synthesize bespoke, comprehensive end-to-end tool schemas.
    - Manages multi-turn conversation memory per session_id.
    """
    session = session_mgr.get_or_create(session_id)
    user_message = user_message.strip()
    session.add_message("user", user_message)

    api_key = get_mistral_api_key()
    if not api_key:
        return {
            "session_id": session.session_id,
            "reply": "⚠️ **Mistral API Key Required**: Please click the **🔑 Mistral API Key** button in the top navigation bar to configure your key. Once added, I will dynamically architect your full server in real-time.",
            "spec": session.current_spec,
            "is_valid": False
        }

    # Multi-turn prompt assembly for Mistral LLM
    context_prompt = ""
    if session.current_spec:
        context_prompt = (
            f"\n\nCURRENT WORKING SPECIFICATION:\n"
            f"Platform: {session.current_spec.get('platform_name')} ({session.current_spec.get('platform_id')})\n"
            f"Category: {session.current_spec.get('category')}\n"
            f"Current Fields: {json.dumps(session.current_spec.get('fields', []))}\n"
            f"Current Tools ({len(session.current_spec.get('tools', []))}): {json.dumps(session.current_spec.get('tools', []))}\n\n"
            f"INSTRUCTION: Apply the user's feedback to the current specification. "
            f"Preserve existing tools unless the user explicitly asks to remove or change them. "
            f"Explain your changes clearly in 'reply'."
        )

    messages = [
        {"role": "system", "content": SYSTEM_ARCHITECT_PROMPT + context_prompt}
    ]

    for m in session.messages:
        messages.append(m)

    payload = {
        "model": DEFAULT_MISTRAL_MODEL,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.1  # Low temperature ensures deterministic, repeatable schemas
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            res = client.post(MISTRAL_API_URL, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                parsed_spec = json.loads(content)

                if not parsed_spec.get("is_valid", True):
                    return {
                        "session_id": session.session_id,
                        "reply": parsed_spec.get("reply", "Could not recognize platform."),
                        "spec": session.current_spec,
                        "is_valid": False
                    }

                if parsed_spec.get("tools"):
                    parsed_spec["tools"] = sanitize_tool_parameters(parsed_spec["tools"])

                session.current_spec = parsed_spec
                reply_text = parsed_spec.get("reply") or f"Updated specification for **{parsed_spec.get('platform_name')}** ({len(parsed_spec.get('tools', []))} tools)."
                session.add_message("assistant", reply_text)

                return {
                    "session_id": session.session_id,
                    "reply": reply_text,
                    "spec": parsed_spec,
                    "is_valid": True
                }
            else:
                # Fallback to mistral-small-latest if model unavailable
                if "model" in res.text.lower() and DEFAULT_MISTRAL_MODEL != "mistral-small-latest":
                    payload["model"] = "mistral-small-latest"
                    res2 = client.post(MISTRAL_API_URL, json=payload, headers=headers)
                    if res2.status_code == 200:
                        data = res2.json()
                        parsed_spec = json.loads(data["choices"][0]["message"]["content"])
                        session.current_spec = parsed_spec
                        return {
                            "session_id": session.session_id,
                            "reply": parsed_spec.get("reply", "Updated specification."),
                            "spec": parsed_spec,
                            "is_valid": True
                        }

                logger.error(f"Mistral API error {res.status_code}: {res.text}")
                return {
                    "session_id": session.session_id,
                    "reply": f"⚠️ Error communicating with Mistral AI ({res.status_code}).",
                    "spec": session.current_spec,
                    "is_valid": False
                }
    except Exception as e:
        logger.error(f"Mistral execution failed: {e}")
        return {
            "session_id": session.session_id,
            "reply": f"⚠️ Exception connecting to AI Architect: {str(e)}",
            "spec": session.current_spec,
            "is_valid": False
        }


def call_mistral_mcp_architect(user_message: str, history: List[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """Legacy wrapper maintained for backward compatibility."""
    result = chat_with_mcp_architect(None, user_message)
    return result.get("spec")


AGENT_SYSTEM_PROMPT = """You are an Enterprise AI Agent connected directly to live MCP Servers via a secured Model Context Protocol Gateway.
You assist developers and DevOps engineers by executing queries, actions, observability checks, and automated tasks across all registered MCP servers.

AVAILABLE LIVE MCP SERVERS & TOOLS:
{server_catalog}

YOUR INSTRUCTIONS:
1. UNDERSTAND INTENT & SELECT TOOL:
   - Match the user's natural language request to the appropriate MCP server and tool.
   - Example 1: "list my github repos" -> server_id: "github", tool_name: "list_repositories"
   - Example 2: "show servicenow incidents" -> server_id: "servicenow", tool_name: "list_incidents"
   - Example 3: "trigger jenkins job" -> server_id: "jenkins", tool_name: "build_job"

2. CONVERSATIONAL PARAMETER COLLECTION (ASK ONE-BY-ONE):
   - If a tool requires MANDATORY arguments (e.g. `repo`, `job_name`, `incident_id`, `issue_id`) that the user has NOT provided yet, DO NOT guess or fail.
   - Prompt the user conversationally and politely for the missing parameter with a friendly example.
   - Return output with type "ask_user".

3. ACCURATE TOOL CALLING:
   - If all required arguments are known, or if the tool can run with default/optional arguments or empty arguments `{{}}`, return output with type "tool_call".
   - Pass clean, accurate arguments matching the tool's parameter schema.

4. GENERAL CONVERSATION:
   - If the user is asking a general question, greeting you, or asking what tools you have access to, return output with type "message" and summarize your live connected servers.

OUTPUT FORMAT (STRICT JSON ONLY):
For tool call:
{{
  "type": "tool_call",
  "server_id": "github",
  "tool_name": "list_repositories",
  "arguments": {{}},
  "thought": "User wants to list repositories."
}}

For asking missing parameters:
{{
  "type": "ask_user",
  "missing_param": "parameter_name",
  "reply": "Conversational question asking for the parameter with an example."
}}

For direct messages:
{{
  "type": "message",
  "reply": "Markdown response to user."
}}
"""


def chat_with_mcp_agent(
    user_message: str,
    history: List[Dict[str, str]],
    servers: Dict[str, Any],
    gateway_url: str = "http://localhost:5001",
    gateway_key: str = "mcp_live_key_dev_2026"
) -> Dict[str, Any]:
    """
    Agentic Chatbot: Uses Mistral AI to converse with the user, collect missing arguments,
    and execute live MCP tools via the Secured Gateway.
    """
    api_key = get_mistral_api_key()
    if not api_key:
        return {
            "type": "message",
            "reply": "⚠️ **Mistral API Key Missing**. Please click **Mistral AI Key** at the top right to configure your API key."
        }

    # Format server catalog
    catalog_lines = []
    for s_id, s_data in servers.items():
        s_name = s_data.get("name", s_id)
        tools = s_data.get("all_tools") or s_data.get("tools") or []
        enabled_tools = s_data.get("enabled_tools") or [t.get("name") for t in tools]
        
        catalog_lines.append(f"\n📦 Server ID: `{s_id}` ({s_name})")
        for t in tools:
            t_name = t.get("name")
            if t_name not in enabled_tools:
                continue
            desc = t.get("description", "")
            params = t.get("params", {})
            catalog_lines.append(f"  - Tool: `{t_name}` | Description: {desc}")
            if params:
                catalog_lines.append(f"    Parameters: {json.dumps(params)}")

    catalog_str = "\n".join(catalog_lines) if catalog_lines else "No active servers currently registered."
    system_prompt = AGENT_SYSTEM_PROMPT.format(server_catalog=catalog_str)

    # Build conversation messages
    messages = [{"role": "system", "content": system_prompt}]
    for msg in (history or []):
        role = msg.get("role", "user")
        if role in ["user", "assistant"]:
            messages.append({"role": role, "content": msg.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": DEFAULT_MISTRAL_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=45.0) as client:
            res = client.post(MISTRAL_API_URL, json=payload, headers=headers)
            if res.status_code != 200:
                # Try fallback model
                payload["model"] = "mistral-small-latest"
                res = client.post(MISTRAL_API_URL, json=payload, headers=headers)

            if res.status_code != 200:
                return {
                    "type": "message",
                    "reply": f"⚠️ Mistral AI error ({res.status_code}): {res.text[:200]}"
                }

            data = res.json()
            raw_content = data["choices"][0]["message"]["content"]
            agent_decision = json.loads(raw_content)

            d_type = agent_decision.get("type", "message")

            if d_type == "ask_user":
                return {
                    "type": "ask_user",
                    "missing_param": agent_decision.get("missing_param"),
                    "reply": agent_decision.get("reply", "Please provide the required parameter.")
                }
            elif d_type == "message":
                return {
                    "type": "message",
                    "reply": agent_decision.get("reply", "How can I assist you with your MCP servers?")
                }
            elif d_type == "tool_call":
                target_server = agent_decision.get("server_id")
                target_tool = agent_decision.get("tool_name")
                tool_args = agent_decision.get("arguments") or {}

                # Fuzzy match tool name if exact name is slightly off (e.g. list_repositories vs list_repos)
                server_tools = [t.get("name") for t in (servers.get(target_server, {}).get("all_tools") or servers.get(target_server, {}).get("tools") or [])]
                if target_tool not in server_tools:
                    for st in server_tools:
                        if ("repo" in st and "repo" in target_tool) and ("list" in st and "list" in target_tool):
                            target_tool = st
                            break
                        elif st.replace("_", "")[:7] == target_tool.replace("_", "")[:7]:
                            target_tool = st
                            break

                # Execute tool call on Gateway
                gateway_ep = f"{gateway_url.rstrip('/')}/mcp/{target_server}"
                gw_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": target_tool,
                        "arguments": tool_args
                    }
                }
                gw_headers = {
                    "Authorization": f"Bearer {gateway_key}",
                    "Content-Type": "application/json"
                }

                try:
                    gw_res = client.post(gateway_ep, json=gw_payload, headers=gw_headers, timeout=30.0)
                    gw_data = gw_res.json()
                    
                    # Extract text or error from JSON-RPC
                    result_content = ""
                    if "result" in gw_data and "content" in gw_data["result"]:
                        for item in gw_data["result"]["content"]:
                            if item.get("type") == "text":
                                result_content += item.get("text", "")
                    elif "error" in gw_data:
                        result_content = json.dumps(gw_data["error"])
                    else:
                        result_content = json.dumps(gw_data)

                    # Synthesize clean human-readable response with Mistral
                    synth_prompt = f"""You are presenting the output of an MCP tool execution to the user.
User Request: "{user_message}"
Executed Tool: `{target_server}.{target_tool}` with arguments: {json.dumps(tool_args)}
Raw Tool Output:
{result_content[:4000]}

Format this into a clean, concise, beautiful Markdown response (use tables, bullet points, or status badges where appropriate).
Explain the result directly to the user."""

                    synth_res = client.post(
                        MISTRAL_API_URL,
                        json={
                            "model": DEFAULT_MISTRAL_MODEL,
                            "messages": [{"role": "user", "content": synth_prompt}],
                            "temperature": 0.2
                        },
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if synth_res.status_code == 200:
                        synth_reply = synth_res.json()["choices"][0]["message"]["content"]
                    else:
                        synth_reply = f"```json\n{result_content}\n```"

                    return {
                        "type": "tool_result",
                        "tool_call": {
                            "server_id": target_server,
                            "tool_name": target_tool,
                            "arguments": tool_args,
                            "raw_output": result_content[:1000]
                        },
                        "reply": synth_reply
                    }

                except Exception as gwe:
                    return {
                        "type": "message",
                        "reply": f"⚠️ Error executing `{target_server}.{target_tool}` via MCP Gateway: {str(gwe)}"
                    }

            return {
                "type": "message",
                "reply": agent_decision.get("reply", "Processed request.")
            }

    except Exception as e:
        logger.error(f"Agent chat exception: {e}")
        return {
            "type": "message",
            "reply": f"⚠️ Agent encountered an error: {str(e)}"
        }


# ==============================================================================
# Conversational AI Bot Architect Engine
# ==============================================================================

BOT_ARCHITECT_SYSTEM_PROMPT = """You are the Senior Lead DevOps & SRE Autonomous Bot Architect.
Your role is to conduct a collaborative, conversational interview with the user to architect an autonomous DevOps workflow bot using their currently connected MCP servers and built-in system capabilities.

BUILT-IN PLATFORM CAPABILITIES (Always available out-of-the-box — do NOT treat as missing MCP servers):
- Container / Docker Log Inspection (server: 'system', tool: 'log_inspector'): Reads container logs, monitors exceptions, detects error signatures.
- Mistral AI Root Cause Analysis (server: 'system', tool: 'ai_rca'): Principal SRE diagnostics, stack trace RCA, and remediation synthesis.
- Incident Deduplication Engine (server: 'system', tool: 'dedup_checker'): Automatically checks for existing open tickets before creating duplicates.
- Automatic Ticket Resolution & Closure: Enriches tickets with work notes and transitions state to Resolved/Closed.

CURRENT CONNECTED EXTERNAL MCP SERVERS & AVAILABLE TOOLS:
{mcp_catalog}

CORE PRINCIPLES:
1. UNDERSTAND & REPEAT:
   - Always summarize what you understood from the user's requirement clearly in 2-3 bullet points.
2. VALIDATE CAPABILITIES:
   - Recognize that Docker container monitoring, AI RCA, and Deduplication are built-in system features.
   - For external systems (e.g. ServiceNow, Jenkins, GitHub), validate against the connected MCP servers in the catalog above.
   - If an external tool is NOT available (e.g. user asks for Datadog, Prometheus, Slack, or AWS, but no such MCP server is connected), explicitly state:
     "⚠️ Capability Missing: I checked your active MCP servers, and you do not have an MCP server connected for [Tool/Service]. You would need to add an MCP server for [Tool] first, or we can build this workflow using your available servers ({available_server_names})."
3. DYNAMIC PARAMETER ELICITATION (ZERO HARDCODING):
   - Never assume static fields like GitHub repo or Jenkins job unless the user's workflow actually uses them.
   - If the bot only uses ServiceNow + Docker, only extract Container Name and SNOW details (do NOT ask for GitHub or Jenkins).
   - If all necessary information is already provided in the prompt, synthesize the complete blueprint immediately and set status="ready".
4. RESPONSE FORMAT:
   Always respond in STRICT JSON matching this schema:
   {
     "status": "ready" or "clarification_needed" or "capability_missing",
     "reply": "Markdown explanation with understanding summary, capability validation badges, and any follow-up questions",
     "validation": {
       "supported": true,
       "servers_used": ["servicenow"],
       "tools_mapped": ["system.log_inspector", "system.ai_rca", "servicenow.create_incident", "servicenow.update_incident"],
       "missing_servers": []
     },
     "blueprint": {
       "id": "bot_snake_case_id",
       "name": "Short Professional Bot Name",
       "category": "SRE & Incident Automation" or "CI/CD Orchestration" or "Security & Compliance",
       "description": "1-2 sentence description of bot mission",
       "trigger_type": "interval",
       "interval_seconds": 120,
       "instructions": "Full natural language instructions",
       "tools_required": ["servicenow"],
       "context_config": {
         "container_name": "devops-vsp-sample-app",
         "snow_urgency": "2"
       },
       "workflow_steps": [
         {"step": 1, "action": "Monitor Docker container logs", "server": "system", "tool": "log_inspector"},
         {"step": 2, "action": "Check active incident deduplication", "server": "system", "tool": "dedup_checker"},
         {"step": 3, "action": "Diagnose failure with Mistral AI RCA", "server": "system", "tool": "ai_rca"},
         {"step": 4, "action": "Create ServiceNow Incident", "server": "servicenow", "tool": "create_incident"},
         {"step": 5, "action": "Enrich ticket with RCA & Auto-Resolve", "server": "servicenow", "tool": "update_incident"}
       ]
     }
   }
"""


def chat_with_bot_architect(user_message: str, history: List[Dict[str, str]], servers: Dict[str, Any]) -> Dict[str, Any]:
    """Conducts a multi-turn conversation to understand requirements, validate MCP capabilities, and build a bot blueprint."""
    api_key = get_mistral_api_key()
    if not api_key:
        return {
            "status": "clarification_needed",
            "reply": "⚠️ Mistral API Key is missing. Please configure your key in the top header.",
            "validation": {"supported": False, "servers_used": [], "tools_mapped": [], "missing_servers": []},
            "blueprint": None
        }

    # Format available MCP catalog
    catalog_lines = []
    available_names = []
    for s_id, s_data in servers.items():
        s_name = s_data.get("name", s_id)
        available_names.append(s_name)
        tools = s_data.get("all_tools") or s_data.get("tools") or []
        t_names = [t.get("name") for t in tools[:12]]
        catalog_lines.append(f"- Server ID '{s_id}' ({s_name}): Tools [{', '.join(t_names)}]")
    
    mcp_catalog = "\n".join(catalog_lines) if catalog_lines else "No active MCP servers connected yet."
    available_server_names = ", ".join(available_names) if available_names else "None"

    system_prompt = BOT_ARCHITECT_SYSTEM_PROMPT.replace("{mcp_catalog}", mcp_catalog).replace("{available_server_names}", available_server_names)

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-8:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": DEFAULT_MISTRAL_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=35.0) as client:
            res = client.post(MISTRAL_API_URL, json=payload, headers=headers)
            if res.status_code == 429 or res.status_code >= 500:
                payload["model"] = "mistral-small-latest"
                res = client.post(MISTRAL_API_URL, json=payload, headers=headers)

            if res.status_code != 200:
                return {
                    "status": "clarification_needed",
                    "reply": f"⚠️ Mistral AI returned status {res.status_code}: {res.text[:200]}",
                    "validation": {"supported": False, "servers_used": [], "tools_mapped": [], "missing_servers": []},
                    "blueprint": None
                }

            data = res.json()
            raw_json = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_json)

            # Ensure consistent fields
            if "blueprint" in parsed and isinstance(parsed["blueprint"], dict):
                bp = parsed["blueprint"]
                if not bp.get("id"):
                    bp["id"] = f"bot_{int(time.time())}"
                if not bp.get("status"):
                    bp["status"] = "active"
                if not bp.get("trigger_type"):
                    bp["trigger_type"] = "interval"
                if not bp.get("interval_seconds"):
                    bp["interval_seconds"] = 120

            return parsed

    except Exception as e:
        logger.error(f"Bot architect error: {e}")
        return {
            "status": "clarification_needed",
            "reply": f"⚠️ Architect exception: {str(e)}",
            "validation": {"supported": False, "servers_used": [], "tools_mapped": [], "missing_servers": []},
            "blueprint": None
        }

"""
Mistral AI Service - Interactive Multi-Turn MCP Architect with Context & Memory
Provides deterministic tool synthesis, multi-turn design conversations, and schema customization.
"""

import os
import json
import logging
import uuid
import httpx
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from platform_specs import find_platform_by_query, PLATFORM_SPECS

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
You collaborate with developers to architect, review, and synthesize COMPREHENSIVE, END-TO-END production-grade FastMCP servers for ANY platform, tool, or API (e.g. Datadog, Splunk, Jira, ServiceNow, GitLab, Kubernetes, Cloudflare, PagerDuty, Salesforce, or proprietary REST APIs).

YOUR ARCHITECTURAL MANDATES:

1. COMPREHENSIVE END-TO-END TOOL SUITES (MANDATORY 16 TO 25 TOOLS):
   - Never generate lazy, minimal (2-3 tool) mockups. Every platform request MUST result in a complete, 360-degree tool suite of 16 to 25 specialized, production-ready tools.
   - You MUST cover all 4 functional pillars:
     * 🔍 Query & Read (6-8 tools): list collections with filters/pagination, get single item details by ID, search by query string, inspect metadata, filter by state/tag.
     * ⚡ Action & Mutation (6-8 tools): create entities, update records, delete/archive items, execute actions, batch operations, assign ownership, trigger workflows.
     * 📊 Monitoring & Observability (3-5 tools): stream/fetch logs, check service health/status, pull performance metrics, audit event history, inspect alerts.
     * 🛡️ Admin & Governance (2-4 tools): manage user roles/permissions, inspect system info/version, validate licenses, update configurations.

2. REAL-WORLD API CONTRACTS (METHOD & ENDPOINTS):
   - For every tool, specify the exact real HTTP method (GET, POST, PUT, DELETE, PATCH).
   - Specify the real REST API path (e.g. `/api/v2/series`, `/services/collector/event`, `/api/v4/projects`, `/api/now/table/incident`, `/v1/query`).
   - Use URL path placeholders when referencing IDs (e.g. `/repos/{owner}/{repo}/issues/{issue_number}` or `/api/v1/hosts/{host_id}`).

3. CREDENTIAL ISOLATION:
   - Base URLs, API Tokens, Passwords, and Secrets belong exclusively in "fields" configured ONCE at startup.
   - NEVER place connection credentials into tool "params" or "sample_args".

4. CONVERSATIONAL COLLABORATION WITH PERSISTENT MEMORY:
   - Talk to the developer as an expert enterprise architect.
   - Explain your design rationale, explain why tools are grouped as they are, and explain parameter usage.
   - When modifying tools upon user request, preserve the full existing suite and apply exact modifications/additions without dropping tools.

OUTPUT FORMAT (STRICT VALID JSON ONLY):
{
  "is_valid": true,
  "reply": "Conversational architectural reply explaining the 360-degree tool suite designed for the platform.",
  "platform_id": "snake_case_id",
  "platform_name": "Human Readable Platform Name",
  "category": "Domain Category (e.g. Observability, Security, ITSM, CI/CD, Cloud Infrastructure)",
  "description": "Comprehensive description of this enterprise MCP server",
  "fields": [
    {
      "key": "field_key_name",
      "label": "Human Readable Label",
      "prompt": "Conversational prompt asking for this value",
      "placeholder": "https://api.service.com or API Token...",
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
  "reply": "I could not recognize '**<input>**' as a known software platform, service, or API. Please specify a valid system (e.g. Datadog, Splunk, Jira, ServiceNow, GitLab, Cloudflare, PagerDuty, Kubernetes) or provide your API schema.",
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
        with httpx.Client(timeout=60.0) as client:
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

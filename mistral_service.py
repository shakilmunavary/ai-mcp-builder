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


SYSTEM_ARCHITECT_PROMPT = """You are the Senior Enterprise Model Context Protocol (MCP) Architect.
You are collaborating with a developer in an interactive multi-turn design session to plan, review, and customize an MCP Server.

YOUR CORE RESPONSIBILITIES:
1. DETERMINISM & CONSISTENCY:
   - Provide a comprehensive, professional tool suite covering:
     * Query & Read Tools (inspect, list, get, search)
     * Action & Mutation Tools (create, update, execute, trigger)
     * Monitoring & Audit Tools (logs, status, history, metrics)
     * Admin & Configuration Tools (settings, health, plugins)
   - When modifying tools based on user feedback, DO NOT randomly change or drop existing unmentioned tools. Preserve the existing suite and apply exact delta changes.

2. CREDENTIAL ISOLATION:
   - Connection credentials (Base URL, Instance URL, Tokens, Passwords, API Keys) belong in "fields" configured ONCE at server startup.
   - NEVER place connection credentials into tool "params" or "sample_args".

3. INTERACTIVE CONVERSATION:
   - Talk to the developer like an expert solutions architect.
   - Explain your design choices, explain parameter requirements, and explain why certain tools are included or modified.

OUTPUT FORMAT (STRICT VALID JSON):
{
  "is_valid": true,
  "reply": "Conversational reply to the developer explaining your actions, answers, or design rationale.",
  "platform_id": "snake_case_id",
  "platform_name": "Human Readable Platform Name",
  "category": "Domain Category (e.g. ITSM, CI/CD, Cloud Storage)",
  "description": "Comprehensive description of this MCP server",
  "fields": [
    {
      "key": "field_key_name",
      "label": "Human Readable Label",
      "prompt": "Conversational prompt asking for this value",
      "placeholder": "example placeholder",
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
      "params": {
        "domain_param_name": "type (required/optional) - description"
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
  "reply": "I could not recognize '**<input>**' as a known software platform, service, or API. Please specify a valid system (e.g. ServiceNow, Jenkins, AWS S3, GitHub, Jira, PostgreSQL) or provide API documentation.",
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
    Main multi-turn interactive architect engine:
    1. Manages session memory.
    2. Uses canonical deterministic blueprints for recognized enterprise tools.
    3. Handles multi-turn conversational refinements with Codestral / Mistral Large.
    """
    session = session_mgr.get_or_create(session_id)
    user_message = user_message.strip()
    session.add_message("user", user_message)

    api_key = get_mistral_api_key()

    # If first turn in session and message matches a canonical enterprise suite
    if not session.current_spec:
        canonical = find_platform_by_query(user_message)
        if canonical:
            session.current_spec = {
                "is_valid": True,
                "platform_id": canonical["id"],
                "platform_name": canonical["name"],
                "category": canonical["category"],
                "description": canonical["description"],
                "fields": canonical["fields"],
                "tools": canonical["tools"]
            }
            tool_count = len(canonical["tools"])
            reply = (
                f"👋 I have initialized the **{canonical['name']}** enterprise MCP suite with "
                f"**{tool_count} standardized tools** across Queries, Actions, and Admin workflows.\n\n"
                f"You can review the tools below, ask questions about specific parameters, request additional tools, "
                f"or click **Proceed to Build** when ready."
            )
            session.add_message("assistant", reply)
            return {
                "session_id": session.session_id,
                "reply": reply,
                "spec": session.current_spec,
                "is_valid": True
            }

    # If no Mistral API key is configured, provide deterministic fallback
    if not api_key:
        canonical = find_platform_by_query(user_message)
        if canonical:
            session.current_spec = {
                "is_valid": True,
                "platform_id": canonical["id"],
                "platform_name": canonical["name"],
                "category": canonical["category"],
                "description": canonical["description"],
                "fields": canonical["fields"],
                "tools": canonical["tools"]
            }
            reply = f"Initialized standard {canonical['name']} suite with {len(canonical['tools'])} tools."
            return {"session_id": session.session_id, "reply": reply, "spec": session.current_spec, "is_valid": True}
        else:
            return {
                "session_id": session.session_id,
                "reply": "⚠️ MISTRAL_API_KEY is not configured in Settings. Please add your key to enable dynamic AI customization.",
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

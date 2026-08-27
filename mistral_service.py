"""
Mistral AI Service - Dynamic Real-Time MCP Specification & Tool Architect
Powered by Mistral AI LLM for interactive tool synthesis with strict entity validation & server-side credential isolation.
"""

import os
import json
import re
import logging
import httpx
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("mistral_service")

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# List of parameter names that represent server connection credentials and MUST NOT be exposed in tool schemas
AUTH_CREDENTIAL_PARAM_NAMES = {
    "url", "base_url", "instance_url", "jenkins_url", "server_url", "host", "endpoint",
    "token", "api_token", "jenkins_token", "access_token", "bearer_token", "pat",
    "password", "secret", "secret_key", "aws_secret_access_key", "api_key",
    "username", "user", "jenkins_username", "caller", "client_id", "aws_access_key_id",
    "crumb", "jenkins_crumb", "csrf_token", "auth_header", "credentials_id"
}


def get_mistral_api_key() -> str:
    return os.environ.get("MISTRAL_API_KEY", "").strip()


def set_mistral_api_key(new_key: str) -> None:
    os.environ["MISTRAL_API_KEY"] = new_key.strip()
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MISTRAL_API_KEY="):
                    lines.append(f"MISTRAL_API_KEY={new_key.strip()}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"MISTRAL_API_KEY={new_key.strip()}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    logger.info("Updated MISTRAL_API_KEY in environment and .env")


SYSTEM_PROMPT = """You are the World-Class AI Model Context Protocol (MCP) Architect.
Your task is to analyze user requests and synthesize rich FastMCP tool specifications for REAL developer tools, cloud providers, APIs, databases, CI/CD systems, and enterprise services.

CRITICAL RULES:
1. REALITY & VALIDITY CHECK (NO HALLUCINATIONS):
   - You MUST verify if the requested platform is a real, existing software, developer tool, cloud service, API, database, or technology.
   - If the user provides made-up words, random characters, gibberish (e.g. "bimbikili", "asdfghjk", "foobaz123", "blabla"), or non-existent tools, you MUST NOT hallucinate fake tools.
   - For invalid/unknown platforms, return JSON with `"is_valid": false`, `"tools": []`, `"fields": []`, and a friendly response:
     `{"is_valid": false, "response": "I could not recognize '**<input>**' as a known software, platform, or API. Please specify a valid tool (e.g., Jenkins, AWS S3, GitHub, ServiceNow, PostgreSQL, Terraform, Jira) or provide its API details.", "tools": [], "fields": []}`

2. STRICT CREDENTIAL ISOLATION:
   - Connection credentials (Base URL, Instance URL, API Tokens, Passwords, Secrets, Usernames, CSRF Crumbs) are configured ONCE at the server level in "fields" (to be saved in `.env`).
   - DO NOT put connection credentials into tool "params" or "sample_args"!
   - Tool "params" must ONLY contain domain/functional inputs needed for that operation (e.g. for Jenkins: job_name, build_number; for S3: bucket_name, object_key; for ServiceNow: incident_number, short_description).
   - Status, version, and global listing tools must have EMPTY params `{}` and empty sample_args `{}`!

3. TOOL SCOPING & QUALITY:
   - Pay strict attention to user scoping (e.g. if the user says "AWS S3 alone", ONLY produce AWS S3 tools, do NOT include EC2 or Lambda).
   - Produce 12-25 comprehensive tools covering queries, actions, execution, and monitoring.

OUTPUT FORMAT (STRICT VALID JSON):

When Valid:
{
  "is_valid": true,
  "response": "Conversational summary explaining what you formulated for the user",
  "platform_id": "unique_snake_case_id",
  "platform_name": "Human Readable Platform Name",
  "category": "Domain Category (e.g. CI/CD, Cloud Storage, ITSM, Database)",
  "description": "Comprehensive description of this MCP suite",
  "fields": [
    {
      "key": "field_key_name",
      "label": "Human Readable Label",
      "prompt": "Conversational prompt asking for this value",
      "placeholder": "example placeholder",
      "default": "",
      "secret": true_or_false,
      "required": true_or_false
    }
  ],
  "tools": [
    {
      "name": "snake_case_tool_name",
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

When Invalid / Unknown / Gibberish:
{
  "is_valid": false,
  "response": "I could not recognize '**<input>**' as a known platform or API. Please specify a valid tool (e.g. Jenkins, GitHub, ServiceNow, AWS S3, Terraform, Datadog) or provide its API documentation.",
  "tools": [],
  "fields": []
}
"""


def sanitize_tool_parameters(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Strips accidental connection credentials (urls, tokens, passwords, usernames, crumbs)
    from tool function schemas so only clean functional arguments remain.
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
                if p_lower in ["username", "jenkins_username"] and "auth" in str(p_desc).lower():
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


def call_mistral_mcp_architect(user_message: str, history: List[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
    """
    Calls Mistral AI chat completion to dynamically synthesize the MCP server specification.
    """
    api_key = get_mistral_api_key()
    if not api_key:
        logger.warning("No MISTRAL_API_KEY configured.")
        return None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for h in history[-4:]:
            role = "user" if h.get("role") == "user" else "assistant"
            content = h.get("content", "")
            if content and isinstance(content, str):
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": "mistral-small-latest",
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.1
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
                
                # If invalid/gibberish, return without tools
                if not parsed_spec.get("is_valid", True):
                    return parsed_spec

                # Sanitize tools to ensure credentials are never leaked as arguments
                if parsed_spec.get("tools"):
                    parsed_spec["tools"] = sanitize_tool_parameters(parsed_spec["tools"])

                logger.info(f"Mistral AI successfully synthesized {len(parsed_spec.get('tools', []))} tools for '{parsed_spec.get('platform_name')}'.")
                return parsed_spec
            else:
                logger.error(f"Mistral API returned error {res.status_code}: {res.text}")
                return None
    except Exception as e:
        logger.error(f"Failed to communicate with Mistral AI API: {e}")
        return None

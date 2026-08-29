"""
AI MCP Server Kit - Universal Multi-Turn Conversational AI Architect & Dynamic Generator
Powered by Mistral AI LLM for Dynamic Real-Time Tool & Schema Discovery.
"""

import os
import sys
import json
import re
import logging
import subprocess
import httpx
import base64
from datetime import datetime
import keyring
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load root environment variables
load_dotenv()

from platform_specs import get_all_platforms, get_platform_spec, find_platform_by_query
from gateway_manager import gateway_mgr, get_current_gateway_api_key, set_current_gateway_api_key
from mistral_service import (
    get_mistral_api_key, set_mistral_api_key, call_mistral_mcp_architect,
    sanitize_tool_parameters, chat_with_mcp_architect, chat_with_mcp_agent, session_mgr
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_JSON_PATH = os.path.join(BASE_DIR, "config.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("app")

app = Flask(__name__, template_folder="templates")


def load_server_registry() -> dict:
    if not os.path.exists(CONFIG_JSON_PATH):
        return {"servers": {}}
    try:
        with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for s_id, s_data in (data.get("servers", {}) or {}).items():
                env_file = os.path.join(BASE_DIR, "mcp_servers", s_id, ".env")
                scopes = {}
                if os.path.exists(env_file):
                    try:
                        with open(env_file, "r", encoding="utf-8") as ef:
                            for line in ef:
                                line = line.strip()
                                if line and not line.startswith("#") and "=" in line:
                                    k, v = line.split("=", 1)
                                    k_l = k.strip().lower()
                                    if any(w in k_l for w in ["owner", "org", "organization", "username", "user", "project", "workspace", "account"]):
                                        scopes[k_l] = v.strip()
                                        if "owner" in k_l or "org" in k_l:
                                            scopes["org"] = v.strip()
                                            scopes["owner"] = v.strip()
                    except Exception:
                        pass
                s_data["scope"] = scopes
                # Ensure all server tools are sanitized from accidental credentials
                if "all_tools" in s_data:
                    s_data["all_tools"] = sanitize_tool_parameters(s_data["all_tools"])
                if "tools" in s_data:
                    s_data["tools"] = sanitize_tool_parameters(s_data["tools"])
            return data
    except Exception as e:
        logger.error(f"Error reading config.json: {e}")
        return {"servers": {}}


def save_server_registry(data: dict) -> None:
    with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def write_server_env_file(platform_id: str, config_values: dict) -> str:
    server_dir = os.path.join(BASE_DIR, "mcp_servers", platform_id)
    os.makedirs(server_dir, exist_ok=True)
    env_file_path = os.path.join(server_dir, ".env")

    lines = [f"# MCP Server Credentials for {platform_id}\n"]
    for k, v in config_values.items():
        env_var_name = k.upper()
        lines.append(f"{env_var_name}={v}\n")

    with open(env_file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    logger.info(f"Wrote local credentials into {env_file_path}")
    return env_file_path


def generate_dynamic_mcp_server_script(server_id: str, server_name: str, base_url: str, auth_header: str, tools: list = None) -> str:
    """
    Universal, 100% Platform-Agnostic FastMCP Server Generator:
    Generates dynamic FastMCP servers for ANY service (Datadog, Splunk, ServiceNow, GitHub, GitLab, Jira, etc.)
    using universal REST/JSON-RPC parameter binding, path variable substitution, and multi-auth resolution.
    """
    tools = tools or [
        {"name": "query_endpoint", "description": f"Send dynamic GET request to {server_name}", "endpoint": "/status", "method": "GET"},
        {"name": "post_endpoint", "description": f"Send dynamic POST payload to {server_name}", "endpoint": "/action", "method": "POST"}
    ]

    code = f'''"""
Dynamic FastMCP Server for {server_name} ({server_id})
Generated automatically by AI MCP Server Kit & Mistral AI Architect.
"""

import os
import sys
import httpx
import base64
import keyring
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH, override=True)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except ImportError:
        from mcp.server import Server as FastMCP

mcp = FastMCP("{server_id}-server")
SERVICE_NAME = "mcp_{server_id}"

def get_credentials() -> Dict[str, str]:
    creds = {{
        "base_url": "{base_url}",
        "auth_val": "{auth_header}",
        "username": ""
    }}
    for k, v in os.environ.items():
        k_upper = k.upper()
        if any(w in k_upper for w in ["URL", "HOST", "ENDPOINT"]) and v:
            creds["base_url"] = v
        elif any(w in k_upper for w in ["TOKEN", "API_KEY", "SECRET", "PASSWORD", "AUTH"]) and v:
            creds["auth_val"] = v
        elif any(w in k_upper for w in ["USERNAME", "USER_ID", "CLIENT_ID", "ACCESS_KEY"]) and v and k_upper not in ["USER", "LOGNAME"]:
            creds["username"] = v
        else:
            creds[k.lower()] = v

    base_url = os.environ.get("INSTANCE_URL") or os.environ.get("BASE_URL") or creds.get("base_url", "")
    auth_val = os.environ.get("PASSWORD") or os.environ.get("TOKEN") or os.environ.get("API_KEY") or os.environ.get("AUTH_HEADER") or creds.get("auth_val", "")
    username = os.environ.get("USERNAME") or creds.get("username", "")
    
    creds["base_url"] = base_url.rstrip("/")
    creds["auth_val"] = auth_val
    creds["username"] = username
    return creds

def get_headers_and_auth(creds: Dict[str, str]):
    headers = {{
        "Accept": "application/json, application/vnd.github.v3+json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "MCP-Gateway-Universal/2.0"
    }}
    auth = None
    u = creds.get("username")
    p = creds.get("auth_val")

    if u and p:
        auth = (u, p)
        try:
            b64_val = base64.b64encode(f"{{u}}:{{p}}".encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {{b64_val}}"
        except Exception:
            pass
    elif p:
        if any(prefix in p for prefix in ["Bearer ", "Basic ", "token ", "ApiKey "]):
            headers["Authorization"] = p
        elif p.startswith("ghp_") or p.startswith("github_pat_") or len(p) == 40 or len(p) > 30:
            headers["Authorization"] = f"Bearer {{p}}"
        else:
            headers["Authorization"] = f"Bearer {{p}}"
            
    return headers, auth
'''

    for t in tools:
        fn_name = re.sub(r'[^a-zA-Z0-9_]', '_', t.get("name", "custom_call"))
        desc = t.get("description", f"Execute {fn_name}").replace('"', '\\"')
        method = t.get("method", "POST" if any(k in fn_name for k in ["create", "trigger", "post", "update", "delete", "add", "merge", "cancel", "lock", "start", "stop", "abort", "apply", "patch", "upload", "deploy", "submit", "close", "reopen", "put"]) else "GET").upper()
        
        endpoint = t.get("endpoint") or t.get("path") or f"/{fn_name}"

        code += f'''

@mcp.tool()
def {fn_name}(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """{desc}"""
    creds = get_credentials()
    base = creds["base_url"]
    headers, auth = get_headers_and_auth(creds)
    
    args = dict(kwargs)
    if isinstance(path_or_params, dict):
        args.update(path_or_params)
        
    target_endpoint = "{endpoint}"
    if " or " in target_endpoint:
        target_endpoint = target_endpoint.split(" or ")[0].strip()
    if " OR " in target_endpoint:
        target_endpoint = target_endpoint.split(" OR ")[0].strip()
    if "," in target_endpoint:
        target_endpoint = target_endpoint.split(",")[0].strip()
    if target_endpoint.strip("/") in ["repos", "repositories", "list_repos", "list_repositories", "get_repos"]:
        target_endpoint = "/user/repos"

    # Substitute parameters passed in tool call
    for k, v in list(args.items()):
        tag = "{{{" + str(k) + "}}}"
        if tag in target_endpoint:
            target_endpoint = target_endpoint.replace(tag, str(v))
            args.pop(k, None)

    # Auto-substitute configured scope values (org, owner, workspace, project, etc.)
    scope_mappings = {{
        "org": ["{{org}}", "{{organization}}", "{{owner}}"],
        "organization": ["{{organization}}", "{{org}}", "{{owner}}"],
        "owner": ["{{owner}}", "{{org}}", "{{organization}}", "{{user}}", "{{username}}"],
        "username": ["{{username}}", "{{user}}", "{{owner}}"],
        "workspace": ["{{workspace}}", "{{ws}}"],
        "project": ["{{project}}", "{{project_id}}", "{{project_key}}"],
        "account": ["{{account}}", "{{account_id}}"],
        "region": ["{{region}}"]
    }}
    for k, v in list(creds.items()):
        if not v or k in ["base_url", "auth_val"]:
            continue
        k_clean = str(k).lower()
        tag = "{{{" + k_clean + "}}}"
        if tag in target_endpoint:
            target_endpoint = target_endpoint.replace(tag, str(v))
        for pattern in scope_mappings.get(k_clean, []):
            if pattern in target_endpoint:
                target_endpoint = target_endpoint.replace(pattern, str(v))

    if target_endpoint.startswith("http://") or target_endpoint.startswith("https://"):
        url = target_endpoint
    else:
        url = f"{{base}}/{{target_endpoint.lstrip('/')}}"
    
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=20.0, follow_redirects=True) as client:
            if "{method}" == "GET":
                res = client.get(url, params=args)
                if res.status_code == 404 and "/orgs/" in url:
                    alt_url = url.replace("/orgs/", "/users/")
                    res2 = client.get(alt_url, params=args)
                    if res2.status_code in [200, 201, 202, 204]:
                        res = res2
                    else:
                        res3 = client.get(f"{{base}}/user/repos", params=args)
                        if res3.status_code in [200, 201, 202, 204]:
                            res = res3
            elif "{method}" == "DELETE":
                res = client.delete(url, params=args)
            elif "{method}" == "PUT":
                res = client.put(url, json=args)
            elif "{method}" == "PATCH":
                res = client.patch(url, json=args)
            else:
                res = client.post(url, json=args)

            if res.status_code in [200, 201, 202, 204]:
                out = res.text
                if len(out) > 4000:
                    out = out[:3900] + "\\n... [truncated for token efficiency] ..."
                return f"**{fn_name} ({{res.status_code}}):**\\n```json\\n{{out}}\\n```"
            else:
                return f"API Response ({{res.status_code}}): {{res.text[:500]}}"
    except Exception as e:
        return f"Error executing {fn_name}: {{e}}"
'''

    code += '''
if __name__ == "__main__":
    mcp.run(transport="stdio")
'''
    return code


def ensure_server_script(platform_id: str, config_values: dict = None, tools: list = None) -> str:
    server_dir = os.path.join(BASE_DIR, "mcp_servers", platform_id)
    os.makedirs(server_dir, exist_ok=True)
    server_script = os.path.join(server_dir, "server.py")

    spec = get_platform_spec(platform_id)
    name = spec.get("name", platform_id) if spec else platform_id.capitalize()
    base_url = (config_values or {}).get("base_url", (config_values or {}).get("instance_url", "https://api.service.com"))
    auth_header = (config_values or {}).get("auth_header", (config_values or {}).get("password", (config_values or {}).get("api_token", "")))
    tools_list = tools or (spec.get("tools", []) if spec else [])

    # Always generate fresh server script with all active tools
    code = generate_dynamic_mcp_server_script(platform_id, name, base_url, auth_header, tools_list)
    with open(server_script, "w", encoding="utf-8") as f:
        f.write(code)

    logger.info(f"Generated server script at {server_script} with {len(tools_list)} tools.")
    return server_script


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/mistral/key", methods=["GET", "POST"])
def manage_mistral_key():
    if request.method == "POST":
        data = request.get_json() or {}
        new_key = data.get("api_key", "").strip()
        set_mistral_api_key(new_key)
        return jsonify({"success": True, "has_key": bool(new_key)})
    
    current_key = get_mistral_api_key()
    return jsonify({
        "has_key": bool(current_key),
        "masked_key": f"{current_key[:4]}...{current_key[-4:]}" if len(current_key) > 8 else ("Set" if current_key else "")
    })


@app.route("/api/gateway/key", methods=["GET", "POST"])
def manage_gateway_key():
    if request.method == "POST":
        data = request.get_json() or {}
        new_key = data.get("api_key", "").strip()
        if not new_key:
            return jsonify({"success": False, "error": "API Key cannot be empty"}), 400
        saved_key = set_current_gateway_api_key(new_key)
        return jsonify({"success": True, "api_key": saved_key})
    
    return jsonify({"api_key": get_current_gateway_api_key()})


@app.route("/api/platforms", methods=["GET"])
def list_platforms():
    return jsonify(get_all_platforms())


@app.route("/api/servers", methods=["GET"])
def list_servers():
    registry = load_server_registry()
    return jsonify(registry)


@app.route("/api/gateway/status", methods=["GET"])
def gateway_status():
    status = gateway_mgr.get_status()
    return jsonify(status)


def evaluate_server_health(platform_id: str, server_script: str, tools: list) -> dict:
    """
    Direct HTTP Pre-Flight Probe Test (Equivalent to running a single curl command):
    Reads credentials from .env and executes a fast, direct HTTP request against upstream service.
    """
    server_dir = os.path.dirname(server_script)
    env_file = os.path.join(server_dir, ".env")
    creds = {}
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    creds[k.strip().lower()] = v.strip()

    # Extract base URL and Auth dynamically from any field names
    base_url = ""
    token = ""
    username = ""
    org = ""

    for k, v in creds.items():
        k_lower = k.lower()
        if any(w in k_lower for w in ["url", "host", "endpoint"]) and v:
            base_url = v
        elif any(w in k_lower for w in ["token", "pat", "key", "password", "secret", "auth"]) and v:
            token = v
        elif any(w in k_lower for w in ["username", "user_id", "client_id"]) and v:
            username = v
        elif any(w in k_lower for w in ["owner", "org", "organization", "workspace", "project", "account"]) and v:
            org = v

    if not base_url:
        if "github" in platform_id.lower():
            base_url = "https://api.github.com"
        elif "gitlab" in platform_id.lower():
            base_url = "https://gitlab.com/api/v4"
        elif "slack" in platform_id.lower():
            base_url = "https://slack.com/api"
        else:
            base_url = "https://api.service.com"

    # Choose best probe endpoint from tools or fallback to root
    endpoint = ""
    probe_name = "health_probe"
    for t in (tools or []):
        t_name = t.get("name", "")
        t_ep = t.get("endpoint") or t.get("path") or ""
        if any(k in t_name for k in ["list", "repo", "incident", "job", "health", "status", "get", "query"]) and t_ep:
            endpoint = t_ep
            probe_name = t_name
            break

    if not endpoint:
        endpoint = (tools[0].get("endpoint") if tools else "") or "/status"

    # Universal normalization
    if endpoint.strip("/") in ["repos", "repositories"]:
        endpoint = "/user/repos"
    
    # Auto-substitute {org}, {owner}, {username} if in endpoint
    if org:
        endpoint = endpoint.replace("{org}", org).replace("{organization}", org).replace("{owner}", org).replace("{user}", org).replace("{username}", org)
    if username:
        endpoint = endpoint.replace("{username}", username).replace("{user}", username)

    # Build full probe URL
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        probe_url = endpoint
    else:
        probe_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    # Build headers & auth
    headers = {
        "Accept": "application/json, application/vnd.github.v3+json, text/plain, */*",
        "User-Agent": "MCP-Gateway-PreFlight/1.0"
    }
    auth = None
    if username and token:
        auth = (username, token)
        b64_val = base64.b64encode(f"{username}:{token}".encode("utf-8")).decode("utf-8")
        headers["Authorization"] = f"Basic {b64_val}"
    elif token:
        if any(prefix in token for prefix in ["Bearer ", "Basic ", "token ", "ApiKey "]):
            headers["Authorization"] = token
        else:
            headers["Authorization"] = f"Bearer {token}"

    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=12.0, follow_redirects=True) as client:
            res = client.get(probe_url)
            status = res.status_code
            text_preview = res.text[:400]

            if status in [200, 201, 202, 204, 301, 302]:
                return {
                    "passed": True,
                    "probe": probe_name,
                    "preview": f"HTTP {status} OK: {text_preview}"
                }
            elif status == 401:
                return {
                    "passed": False,
                    "probe": probe_name,
                    "reason": "Authentication Failed (401): Upstream service rejected credentials/token.",
                    "preview": text_preview
                }
            elif status == 403:
                return {
                    "passed": False,
                    "probe": probe_name,
                    "reason": "Permission Denied (403): Token/user lacks required permissions.",
                    "preview": text_preview
                }
            elif status == 404:
                # Smart generic fallback: If /orgs/<name> returned 404 because <name> is a User account, try /users/ or /user/repos
                if "/orgs/" in probe_url:
                    for alt_url in [probe_url.replace("/orgs/", "/users/"), f"{base_url.rstrip('/')}/user/repos"]:
                        try:
                            alt_res = client.get(alt_url)
                            if alt_res.status_code in [200, 201, 202, 204]:
                                return {
                                    "passed": True,
                                    "probe": probe_name,
                                    "preview": f"HTTP {alt_res.status_code} OK (verified via user account): {alt_res.text[:300]}"
                                }
                        except Exception:
                            pass

                return {
                    "passed": False,
                    "probe": probe_name,
                    "reason": f"Endpoint Not Found (404) at {probe_url}. Check instance URL or path.",
                    "preview": text_preview
                }
            else:
                return {
                    "passed": False,
                    "probe": probe_name,
                    "reason": f"HTTP {status} Error from upstream API.",
                    "preview": text_preview
                }
    except Exception as e:
        return {
            "passed": False,
            "probe": probe_name,
            "reason": f"Connection Error: {str(e)}",
            "preview": str(e)
        }


@app.route("/api/servers/<platform_id>/evaluate", methods=["POST"])
def evaluate_existing_server(platform_id: str):
    registry = load_server_registry()
    servers = registry.get("servers", {})
    if platform_id not in servers:
        return jsonify({"success": False, "error": f"Server {platform_id} not found"}), 404
    
    s = servers[platform_id]
    server_script = os.path.join(BASE_DIR, "mcp_servers", platform_id, "server.py")
    tools = s.get("tools", [])
    eval_result = evaluate_server_health(platform_id, server_script, tools)
    return jsonify({"success": True, "evaluation": eval_result})


@app.route("/api/build", methods=["POST"])
def build_server():
    payload = request.get_json() or {}
    platform_id = payload.get("platform_id", "").lower().strip()
    config_values = payload.get("config", {})
    enabled_tools = payload.get("enabled_tools", None)
    dynamic_tools = payload.get("tools", None)

    spec = get_platform_spec(platform_id)
    server_name = (spec.get("name") if spec else "") or config_values.get("custom_name", "").strip() or platform_id.replace("_", " ").title()
    server_key = re.sub(r'[^a-zA-Z0-9_]', '_', platform_id or server_name.lower())
    base_url = config_values.get("base_url", config_values.get("instance_url", config_values.get("jenkins_url", "https://api.service.com")))
    auth_header = config_values.get("auth_header", config_values.get("api_token", config_values.get("token", config_values.get("password", config_values.get("jenkins_password", "")))))
    
    raw_tools = dynamic_tools or (spec.get("tools") if spec else []) or [
        {"name": "query_endpoint", "description": f"Send dynamic GET request to {server_name}", "endpoint": "/status", "method": "GET"},
        {"name": "post_endpoint", "description": f"Send dynamic POST payload to {server_name}", "endpoint": "/action", "method": "POST"}
    ]
    tools_list = sanitize_tool_parameters(raw_tools)

    server_dir = os.path.join(BASE_DIR, "mcp_servers", server_key)
    os.makedirs(server_dir, exist_ok=True)
    server_script = os.path.join(server_dir, "server.py")

    code = generate_dynamic_mcp_server_script(server_key, server_name, base_url, auth_header, tools_list)
    with open(server_script, "w", encoding="utf-8") as f:
        f.write(code)

    write_server_env_file(server_key, config_values)

    if enabled_tools is None:
        enabled_tools = [t["name"] for t in tools_list]

    filtered_tools = [t for t in tools_list if t["name"] in enabled_tools]

    server_entry = {
        "id": server_key,
        "name": server_name,
        "description": spec.get("description") if spec else f"Dynamically synthesized FastMCP Server for {server_name}",
        "category": spec.get("category") if spec else "AI Synthesized Tool",
        "transport": "stdio",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "all_tools": tools_list,
        "enabled_tools": enabled_tools,
        "tools": filtered_tools
    }
    platform_id = server_key

    # Step: Run Self-Evaluation Pre-Flight Smoke Test before publishing
    eval_result = evaluate_server_health(platform_id, server_script, filtered_tools)
    server_entry["last_evaluation"] = eval_result

    if not eval_result.get("passed", False):
        # Do not activate broken server; report evaluation failure
        return jsonify({
            "success": False,
            "evaluation_failed": True,
            "error": eval_result.get("reason", "Pre-flight self-evaluation failed."),
            "evaluation": eval_result,
            "server": server_entry
        }), 400

    # Passed Self-Evaluation: Register in gateway
    python_exec = sys.executable
    gateway_mgr.add_target(
        name=platform_id,
        command=python_exec,
        args=[server_script]
    )

    registry = load_server_registry()
    servers = registry.get("servers", {})
    servers[platform_id] = server_entry
    registry["servers"] = servers
    save_server_registry(registry)

    gateway_res = gateway_mgr.restart_gateway()

    return jsonify({
        "success": True,
        "server": server_entry,
        "evaluation": eval_result,
        "gateway": gateway_res
    })


@app.route("/api/servers/<platform_id>/tools", methods=["POST"])
def update_server_tools(platform_id: str):
    platform_id = platform_id.lower()
    data = request.get_json() or {}
    enabled_tools = data.get("enabled_tools", [])

    registry = load_server_registry()
    servers = registry.get("servers", {})
    if platform_id not in servers:
        return jsonify({"success": False, "error": f"Server {platform_id} not found"}), 404

    s = servers[platform_id]
    all_tools = s.get("all_tools") or s.get("tools", [])
    s["all_tools"] = all_tools
    s["enabled_tools"] = enabled_tools
    s["tools"] = [t for t in all_tools if t["name"] in enabled_tools]

    servers[platform_id] = s
    registry["servers"] = servers
    save_server_registry(registry)

    # Regenerate server.py with active tools and restart gateway
    ensure_server_script(platform_id, tools=s["tools"])
    gateway_mgr.restart_gateway()

    return jsonify({"success": True, "server": s})


@app.route("/api/servers/<platform_id>", methods=["DELETE"])
def delete_server(platform_id: str):
    platform_id = platform_id.lower()
    spec = get_platform_spec(platform_id)
    service_name = f"mcp_{platform_id}"

    gateway_mgr.remove_target(platform_id)

    env_file = os.path.join(BASE_DIR, "mcp_servers", platform_id, ".env")
    if os.path.exists(env_file):
        try:
            os.remove(env_file)
        except Exception:
            pass

    if spec:
        for field in spec["fields"]:
            try:
                keyring.delete_password(service_name, field["key"])
            except Exception:
                pass

    registry = load_server_registry()
    if "servers" in registry and platform_id in registry["servers"]:
        del registry["servers"][platform_id]
        save_server_registry(registry)

    gateway_mgr.restart_gateway()
    return jsonify({"success": True, "message": f"Server {platform_id} deleted."})


@app.route("/api/servers/<platform_id>/reload", methods=["POST"])
def reload_server(platform_id: str):
    res = gateway_mgr.restart_gateway()
    return jsonify({"success": True, "gateway": res})


def synthesize_custom_platform_suite(raw_name: str) -> dict:
    """Fallback local generator if Mistral API key is not configured."""
    cleaned_name = re.sub(r'(?i)\b(i\s+want\s+to\s+build\s+mcp\s+server\s+for|i\s+want\s+to\s+connect|i\s+want\s+mcp\s+for|connect|build|create|mcp|server|for|to|my|our|an|a|\s+)\b', ' ', raw_name).strip()
    if not cleaned_name:
        cleaned_name = "Custom Tool API"
    else:
        cleaned_name = cleaned_name.title()

    server_id = re.sub(r'[^a-zA-Z0-9_]', '_', cleaned_name.lower())

    tools = [
        {"name": "get_status", "description": f"Check connectivity and health of {cleaned_name}.", "params": {}},
        {"name": "get_system_info", "description": f"Retrieve system version, uptime, and cluster details for {cleaned_name}.", "params": {}},
        {"name": "list_records", "description": f"List active items, resources, and records in {cleaned_name}.", "params": {"limit": "integer (default: 20)", "offset": "integer"}},
        {"name": "get_record_details", "description": f"Retrieve detailed metadata for a specific record in {cleaned_name}.", "params": {"record_id": "string (required)"}},
        {"name": "create_record", "description": f"Create or provision a new record in {cleaned_name}.", "params": {"payload": "object (required)"}},
        {"name": "update_record", "description": f"Update an existing record in {cleaned_name}.", "params": {"record_id": "string", "payload": "object"}},
        {"name": "delete_record", "description": f"Delete or archive a record in {cleaned_name}.", "params": {"record_id": "string (required)"}},
        {"name": "search_records", "description": f"Execute search queries across {cleaned_name}.", "params": {"query": "string (required)"}},
        {"name": "trigger_action", "description": f"Trigger automated execution, sync, or workflow in {cleaned_name}.", "params": {"action_name": "string", "params": "object"}},
        {"name": "get_action_status", "description": f"Check status and execution log of a triggered task in {cleaned_name}.", "params": {"task_id": "string"}},
        {"name": "list_events", "description": f"Fetch audit trail and event stream from {cleaned_name}.", "params": {"since": "string (ISO timestamp)"}},
        {"name": "list_metrics", "description": f"Get performance metrics and telemetry from {cleaned_name}.", "params": {"metric_name": "string"}},
        {"name": "query_endpoint", "description": f"Send dynamic GET request to any sub-path of {cleaned_name}.", "params": {"path": "string", "params": "object"}},
        {"name": "post_endpoint", "description": f"Send dynamic POST payload to any sub-path of {cleaned_name}.", "params": {"path": "string", "body": "object"}}
    ]

    return {
        "id": server_id,
        "name": cleaned_name,
        "category": "Enterprise Tooling & API",
        "description": f"Universal FastMCP Server for {cleaned_name} with comprehensive CRUD, monitoring, and workflow automation suite.",
        "icon": "zap",
        "fields": [
            {"key": "base_url", "label": "Server / API Base URL", "prompt": f"Enter the base URL for {cleaned_name} (e.g. https://{server_id}.company.internal):", "placeholder": f"https://api.{server_id}.internal", "default": "", "secret": False, "required": True},
            {"key": "username", "label": "Username / Client ID", "prompt": f"Enter username, client ID, or service account:", "placeholder": "admin", "default": "", "secret": False, "required": False},
            {"key": "api_token", "label": "API Token / Secret Key", "prompt": f"Enter API Token, Bearer Token, or Secret:", "placeholder": "••••••••••••", "default": "", "secret": True, "required": True}
        ],
        "tools": tools
    }


@app.route("/api/architect/chat", methods=["POST"])
def interactive_architect_chat():
    """
    Multi-Turn Interactive MCP Architect with Persistent Memory:
    - Retains conversation context per session_id.
    - Deterministically seeds canonical suites for common tools.
    - Dynamically modifies, adds, and removes tools based on user instructions.
    - Explains parameters and architectures interactively.
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({
            "success": False,
            "error": "Empty message provided."
        }), 400

    result = chat_with_mcp_architect(session_id, message)
    return jsonify({
        "success": True,
        "session_id": result.get("session_id"),
        "reply": result.get("reply"),
        "spec": result.get("spec"),
        "is_valid": result.get("is_valid", True)
    })


@app.route("/api/architect/reset", methods=["POST"])
def interactive_architect_reset():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if session_id:
        session_mgr.reset(session_id)
    return jsonify({"success": True, "message": "Session reset successfully."})


@app.route("/api/chat", methods=["POST"])
def conversational_ai_architect():
    """
    Mistral AI-Powered Conversational Architect:
    - Calls Mistral AI to dynamically synthesize schemas and tools.
    - Handles user confirmations and credential collection.
    """
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()
    history = data.get("history", [])
    current_platform = data.get("current_platform", None)
    collected_config = data.get("collected_config", {})
    is_confirmed = data.get("is_confirmed", False)

    if not message:
        return jsonify({
            "type": "text",
            "response": "👋 Hello! Tell me the platform or service you want to build an MCP server for."
        })

    lower_msg = message.lower()

    # 1. User says "Yes" / "Proceed" / "Build" to confirm discovery
    if current_platform and (is_confirmed or any(w in lower_msg for w in ["yes", "proceed", "confirm", "build", "ok", "go ahead", "sure", "continue"])):
        missing = [fld for fld in current_platform.get("fields", []) if fld["key"] not in collected_config or not collected_config[fld["key"]]]
        if missing:
            next_f = missing[0]
            return jsonify({
                "type": "field_prompt",
                "collected_config": collected_config,
                "platform": current_platform,
                "field": next_f,
                "response": f"Great! Let's connect **{current_platform.get('name')}**.\n\nPlease enter the **{next_f['label']}**:\n_{next_f.get('prompt') or 'Enter value:'}_"
            })
        else:
            return jsonify({
                "type": "ready_to_build",
                "collected_config": collected_config,
                "platform": current_platform,
                "response": f"🎉 All credentials configured for **{current_platform.get('name')}**!\nClick below to generate the FastMCP server and save credentials into `mcp_servers/{current_platform.get('id')}/.env`."
            })

    # 2. Check if user is supplying credentials in text
    if current_platform and not any(w in lower_msg for w in ["yes", "proceed", "confirm"]):
        missing = [fld for fld in current_platform.get("fields", []) if fld["key"] not in collected_config or not collected_config[fld["key"]]]
        if missing:
            curr_field = missing[0]
            collected_config[curr_field["key"]] = message
            remaining = [fld for fld in current_platform.get("fields", []) if fld["key"] not in collected_config or not collected_config[fld["key"]]]
            if remaining:
                next_f = remaining[0]
                return jsonify({
                    "type": "field_prompt",
                    "collected_config": collected_config,
                    "platform": current_platform,
                    "field": next_f,
                    "response": f"✅ Recorded **{curr_field['label']}**.\n\nPlease enter **{next_f['label']}**:\n_{next_f.get('prompt') or 'Enter value:'}_"
                })
            else:
                return jsonify({
                    "type": "ready_to_build",
                    "collected_config": collected_config,
                    "platform": current_platform,
                    "response": f"🎉 All credentials configured for **{current_platform.get('name')}**!\nYou have **{len(current_platform.get('tools', []))} tools** ready to expose. Click below to generate the FastMCP server and save credentials into `mcp_servers/{current_platform.get('id')}/.env`."
                })

    # 3. Live Mistral AI LLM Synthesis (if API Key is configured)
    mistral_key = get_mistral_api_key()
    if mistral_key:
        try:
            logger.info(f"Calling Mistral AI to synthesize spec for '{message}'...")
            mistral_spec = call_mistral_mcp_architect(message, history)
            if mistral_spec:
                # If Mistral detects that this is NOT a valid platform / random gibberish:
                if not mistral_spec.get("is_valid", True) or not mistral_spec.get("tools"):
                    return jsonify({
                        "type": "error",
                        "response": mistral_spec.get("response") or f"❌ I could not recognize '**{message}**' as a known software, developer tool, or API.\n\nPlease specify a valid platform (e.g. *Jenkins*, *GitHub*, *ServiceNow*, *AWS S3*, *Terraform*, *Jira*, *PostgreSQL*) or provide its API endpoints."
                    })

                platform_obj = {
                    "id": mistral_spec.get("platform_id") or re.sub(r'[^a-zA-Z0-9_]', '_', mistral_spec.get("platform_name", "custom").lower()),
                    "name": mistral_spec.get("platform_name", "Custom Service"),
                    "category": mistral_spec.get("category", "Custom Service"),
                    "description": mistral_spec.get("description", ""),
                    "fields": mistral_spec.get("fields", [
                        {"key": "base_url", "label": "Base URL", "placeholder": "https://api.service.com", "secret": False, "required": True},
                        {"key": "api_token", "label": "API Token / Key", "placeholder": "••••••••••••", "secret": True, "required": True}
                    ]),
                    "tools": mistral_spec.get("tools", [])
                }
                return jsonify({
                    "type": "discovery_confirmation",
                    "source": "mistral_ai",
                    "platform": platform_obj,
                    "response": mistral_spec.get("response") or f"🤖 **Mistral AI** dynamically formulated the comprehensive specification for **{platform_obj['name']}** with **{len(platform_obj['tools'])} tools**!\n\nPlease review the available tools below and click **Proceed to Build**."
                })
        except Exception as e:
            logger.error(f"Mistral AI call failed, falling back to local resolver: {e}")

    # 4. Fallback to Local Platform Registry & Sub-Service Scoping
    matched_spec = find_platform_by_query(message)
    if matched_spec:
        return jsonify({
            "type": "discovery_confirmation",
            "source": "local_registry",
            "platform": matched_spec,
            "response": f"🔍 I discovered the comprehensive enterprise specification for **{matched_spec['name']}** with **{len(matched_spec['tools'])} tools**!\n\nPlease review the available tools below. Click **Proceed to Build** to configure credentials and generate the server."
        })

    # 5. Unknown Platform - Ask for valid tool name rather than hallucinating fake tools
    return jsonify({
        "type": "error",
        "response": f"❓ I could not identify '**{message}**' as a recognized software, platform, or API service.\n\nPlease enter a valid tool or platform name (e.g. *AWS S3 alone*, *Jenkins*, *GitHub*, *ServiceNow*, *Terraform*, *PostgreSQL*, *Jira*, *Datadog*)."
    })


@app.route("/api/chat/tester", methods=["POST"])
def agent_chat_tester():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"type": "message", "reply": "Please type a message or instruction."}), 400

    registry = load_server_registry()
    servers = registry.get("servers", {})
    gateway_key = get_current_gateway_api_key()

    result = chat_with_mcp_agent(
        user_message=message,
        history=history,
        servers=servers,
        gateway_url="http://localhost:5001",
        gateway_key=gateway_key
    )

    return jsonify(result)


def main():
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1"]

    logger.info(f"Starting AI MCP Server Kit Web App on http://{host}:{port}")
    gateway_mgr.start_gateway()
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    main()

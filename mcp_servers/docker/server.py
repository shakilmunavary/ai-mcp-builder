"""
Docker FastMCP Server (with Unix Domain Socket & Docker CLI support)
Generated automatically for AI MCP Server Kit.
"""

import os
import sys
import json
import httpx
import subprocess
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except ImportError:
        from mcp.server import Server as FastMCP

mcp = FastMCP("docker-server")
SERVICE_NAME = "mcp_docker"


def get_credentials() -> Dict[str, str]:
    return {
        "base_url": os.environ.get("DOCKER_HOST_URL") or "unix:///var/run/docker.sock",
        "api_version": os.environ.get("DOCKER_API_VERSION") or "v1.41"
    }


def call_docker_api(method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> str:
    creds = get_credentials()
    base_url = creds["base_url"]

    # 1. UNIX Domain Socket via httpx HTTPTransport
    if base_url.startswith("unix://"):
        sock_path = base_url.replace("unix://", "")
        if os.path.exists(sock_path):
            try:
                transport = httpx.HTTPTransport(uds=sock_path)
                with httpx.Client(transport=transport, timeout=20.0) as client:
                    url = f"http://localhost{endpoint}"
                    res = client.request(method, url, params=params, json=json_data)
                    if res.status_code in [200, 201, 204]:
                        return f"**Docker API ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
                    else:
                        return f"Docker API ({res.status_code}): {res.text[:400]}"
            except Exception as e:
                pass

    # 2. Local / WSL Docker CLI fallback
    try:
        if "/containers/json" in endpoint:
            proc = subprocess.run(["docker", "ps", "-a", "--format", "{{json .}}"], capture_output=True, text=True, timeout=8.0)
            if proc.returncode == 0:
                lines = [json.loads(line) for line in proc.stdout.strip().splitlines() if line]
                return f"**list_containers (200):**\n```json\n{json.dumps(lines, indent=2)}\n```"
        elif "/images/json" in endpoint:
            proc = subprocess.run(["docker", "images", "--format", "{{json .}}"], capture_output=True, text=True, timeout=8.0)
            if proc.returncode == 0:
                lines = [json.loads(line) for line in proc.stdout.strip().splitlines() if line]
                return f"**list_images (200):**\n```json\n{json.dumps(lines, indent=2)}\n```"
        elif "/version" in endpoint or "/info" in endpoint:
            proc = subprocess.run(["docker", "version", "--format", "{{json .}}"], capture_output=True, text=True, timeout=8.0)
            if proc.returncode == 0:
                return f"**get_docker_version (200):**\n```json\n{proc.stdout}\n```"
    except Exception as e:
        return f"Docker CLI error: {e}"

    return f"Unable to reach Docker socket at {base_url}."


@mcp.tool()
def list_containers(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """List Docker containers (active and stopped)."""
    return call_docker_api("GET", "/containers/json?all=true")


@mcp.tool()
def list_images(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """List Docker images available on the host."""
    return call_docker_api("GET", "/images/json")


@mcp.tool()
def inspect_container(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Inspect container details and status by container name or id."""
    params = {}
    if isinstance(path_or_params, dict):
        params.update(path_or_params)
    params.update(kwargs)
    c_id = params.get("id") or params.get("container_name") or params.get("name") or "devops-vsp-sample-app"
    return call_docker_api("GET", f"/containers/{c_id}/json")


@mcp.tool()
def get_docker_version(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Get Docker daemon and server version."""
    return call_docker_api("GET", "/version")

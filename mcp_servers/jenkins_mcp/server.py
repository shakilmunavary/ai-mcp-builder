"""
Dynamic FastMCP Server for Jenkins Mcp (jenkins_mcp)
Generated automatically by AI MCP Server Kit & Mistral AI Architect.
"""

import os
import sys
import httpx
import keyring
from typing import Optional, Dict, Any
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

mcp = FastMCP("jenkins_mcp-server")
SERVICE_NAME = "mcp_jenkins_mcp"

def safe_get_keyring(service: str, key: str) -> str:
    try:
        return keyring.get_password(service, key) or ""
    except Exception:
        return ""

def get_credentials() -> Dict[str, str]:
    # Dynamic scan of environment variables
    base_url = "http://localhost:8080"
    auth_val = ""
    username = ""
    for k, v in os.environ.items():
        k_upper = k.upper()
        if any(w in k_upper for w in ["URL", "HOST", "ENDPOINT"]) and v:
            base_url = v
        elif any(w in k_upper for w in ["TOKEN", "API_KEY", "SECRET", "PASSWORD", "AUTH"]) and v:
            auth_val = v
        elif any(w in k_upper for w in ["USERNAME", "USER_ID", "CLIENT_ID", "ACCESS_KEY"]) and v:
            username = v

    base_url = os.environ.get("JENKINS_URL") or os.environ.get("BASE_URL") or base_url or safe_get_keyring(SERVICE_NAME, "base_url") or "http://localhost:8080"
    auth_val = os.environ.get("JENKINS_TOKEN") or os.environ.get("AUTH_HEADER") or auth_val or safe_get_keyring(SERVICE_NAME, "auth_header") or ""
    username = os.environ.get("JENKINS_USERNAME") or os.environ.get("USERNAME") or username or safe_get_keyring(SERVICE_NAME, "username") or "admin"
    return {
        "base_url": base_url.rstrip("/"),
        "auth_val": auth_val,
        "username": username
    }

def get_headers_and_auth(creds: Dict[str, str]):
    headers = {"Accept": "application/json", "User-Agent": "MCP-Gateway-Dynamic/1.0"}
    auth = None
    if creds.get("username") and creds.get("auth_val"):
        auth = (creds["username"], creds["auth_val"])
    elif creds.get("auth_val"):
        v = creds["auth_val"]
        headers["Authorization"] = v if ("Bearer" in v or "Basic" in v or "ApiKey" in v) else f"Bearer {v}"
    return headers, auth


@mcp.tool()
def get_jenkins_version(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve the version information of the Jenkins server"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                data = res.json()
                ver = res.headers.get("X-Jenkins", "Ready")
                return f"**Jenkins Status & Version:**\n- **Version:** `{ver}`\n- **URL:** {creds['base_url']}\n- **Active Jobs:** {len(data.get('jobs', []))}\n- **Mode:** {data.get('mode', 'NORMAL')}"
            return f"Jenkins API Error ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_jenkins_version: {e}"


@mcp.tool()
def get_system_info(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Get comprehensive system information including Jenkins version, Java version, and system properties"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                data = res.json()
                ver = res.headers.get("X-Jenkins", "Ready")
                return f"**Jenkins Status & Version:**\n- **Version:** `{ver}`\n- **URL:** {creds['base_url']}\n- **Active Jobs:** {len(data.get('jobs', []))}\n- **Mode:** {data.get('mode', 'NORMAL')}"
            return f"Jenkins API Error ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_system_info: {e}"


@mcp.tool()
def check_health(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Check the overall health status of the Jenkins instance"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**check_health ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing check_health: {e}"


@mcp.tool()
def list_jobs(folder: Optional[str] = None, recursive: Optional[bool] = False, path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """List all jobs in Jenkins with optional filtering by folder and job type"""
    creds = get_credentials()
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")]
        url = f"{creds['base_url']}/{'/'.join(parts)}/api/json?tree=jobs[name,color,url]"
    else:
        url = f"{creds['base_url']}/api/json?tree=jobs[name,color,url]"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                jobs = res.json().get("jobs", [])
                lines = [f"Jenkins Jobs ({len(jobs)} total):"]
                for j in jobs:
                    lines.append(f"- **{j.get('name')}** (`{j.get('color', 'unknown')}`) - {j.get('url')}")
                return "\n".join(lines)
            return f"Jenkins API Error ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing list_jobs: {e}"


@mcp.tool()
def get_job_details(job_name: Optional[str] = None, folder: Optional[str] = None, path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve detailed configuration and metadata for a specific Jenkins job"""
    creds = get_credentials()
    j_name = job_name or (path_or_params or {}).get("job_name", "AI_PR_Validation")
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")] + [f"job/{j_name}"]
    else:
        parts = [f"job/{p}" for p in j_name.strip("/").split("/")]
    url = f"{creds['base_url']}/{'/'.join(parts)}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                d = res.json()
                return f"**Job Details: `{j_name}`**\n- **URL:** {d.get('url')}\n- **Buildable:** {d.get('buildable')}\n- **Color:** `{d.get('color')}`\n- **Next Build #:** {d.get('nextBuildNumber')}"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_job_details: {e}"


@mcp.tool()
def create_freestyle_job(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Create a new freestyle Jenkins job with specified configuration"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**create_freestyle_job ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_freestyle_job: {e}"


@mcp.tool()
def create_pipeline_job(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Create a new pipeline Jenkins job with specified configuration"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**create_pipeline_job ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_pipeline_job: {e}"


@mcp.tool()
def update_job_config(job_name: Optional[str] = None, folder: Optional[str] = None, path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Update the configuration of an existing Jenkins job"""
    creds = get_credentials()
    j_name = job_name or (path_or_params or {}).get("job_name", "AI_PR_Validation")
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")] + [f"job/{j_name}"]
    else:
        parts = [f"job/{p}" for p in j_name.strip("/").split("/")]
    url = f"{creds['base_url']}/{'/'.join(parts)}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                d = res.json()
                return f"**Job Details: `{j_name}`**\n- **URL:** {d.get('url')}\n- **Buildable:** {d.get('buildable')}\n- **Color:** `{d.get('color')}`\n- **Next Build #:** {d.get('nextBuildNumber')}"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing update_job_config: {e}"


@mcp.tool()
def delete_job(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Delete a Jenkins job permanently"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**delete_job ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing delete_job: {e}"


@mcp.tool()
def trigger_build(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Trigger a new build for a specified Jenkins job with optional parameters"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**trigger_build ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing trigger_build: {e}"


@mcp.tool()
def get_build_info(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve detailed information about a specific build of a Jenkins job"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**get_build_info ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_build_info: {e}"


@mcp.tool()
def get_build_logs(job_name: Optional[str] = None, build_number: Optional[int] = 1, folder: Optional[str] = None, path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve the console output logs for a specific build"""
    creds = get_credentials()
    j_name = job_name or (path_or_params or {}).get("job_name", "AI_PR_Validation")
    b_num = build_number or (path_or_params or {}).get("build_number", 1)
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")] + [f"job/{j_name}", str(b_num), "consoleText"]
    else:
        parts = [f"job/{p}" for p in j_name.strip("/").split("/")] + [str(b_num), "consoleText"]
    url = f"{creds['base_url']}/{'/'.join(parts)}"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=20.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                txt = res.text
                if len(txt) > 4000:
                    txt = "... [truncated] ...\n" + txt[-3800:]
                return f"**Console Log for `{j_name} #{b_num}`:**\n```\n{txt}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_build_logs: {e}"


@mcp.tool()
def get_build_artifacts(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """List all artifacts generated by a specific build"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**get_build_artifacts ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_build_artifacts: {e}"


@mcp.tool()
def download_artifact(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Download a specific artifact from a build"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**download_artifact ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing download_artifact: {e}"


@mcp.tool()
def stop_build(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Stop a running Jenkins build"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**stop_build ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing stop_build: {e}"


@mcp.tool()
def get_build_queue(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve the current build queue with all queued items and their details"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**get_build_queue ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_build_queue: {e}"


@mcp.tool()
def list_nodes(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """List all Jenkins nodes (agents) with their status and details"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**list_nodes ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing list_nodes: {e}"


@mcp.tool()
def get_node_details(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve detailed information about a specific Jenkins node"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**get_node_details ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_node_details: {e}"


@mcp.tool()
def create_credential(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Create a new credential in Jenkins credential store"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**create_credential ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_credential: {e}"


@mcp.tool()
def delete_credential(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Delete a credential from Jenkins credential store"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**delete_credential ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing delete_credential: {e}"


@mcp.tool()
def list_plugins(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """List all installed Jenkins plugins with their versions and status"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**list_plugins ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing list_plugins: {e}"


@mcp.tool()
def install_plugin(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Install a Jenkins plugin by name"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**install_plugin ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing install_plugin: {e}"


@mcp.tool()
def uninstall_plugin(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Uninstall a Jenkins plugin by name"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**uninstall_plugin ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing uninstall_plugin: {e}"


@mcp.tool()
def restart_jenkins(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Safely restart the Jenkins instance"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**restart_jenkins ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing restart_jenkins: {e}"


@mcp.tool()
def get_system_logs(job_name: Optional[str] = None, build_number: Optional[int] = 1, folder: Optional[str] = None, path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve Jenkins system logs for troubleshooting"""
    creds = get_credentials()
    j_name = job_name or (path_or_params or {}).get("job_name", "AI_PR_Validation")
    b_num = build_number or (path_or_params or {}).get("build_number", 1)
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")] + [f"job/{j_name}", str(b_num), "consoleText"]
    else:
        parts = [f"job/{p}" for p in j_name.strip("/").split("/")] + [str(b_num), "consoleText"]
    url = f"{creds['base_url']}/{'/'.join(parts)}"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=20.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                txt = res.text
                if len(txt) > 4000:
                    txt = "... [truncated] ...\n" + txt[-3800:]
                return f"**Console Log for `{j_name} #{b_num}`:**\n```\n{txt}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_system_logs: {e}"


@mcp.tool()
def search_jobs(folder: Optional[str] = None, recursive: Optional[bool] = False, path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Search for Jenkins jobs matching a pattern"""
    creds = get_credentials()
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")]
        url = f"{creds['base_url']}/{'/'.join(parts)}/api/json?tree=jobs[name,color,url]"
    else:
        url = f"{creds['base_url']}/api/json?tree=jobs[name,color,url]"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                jobs = res.json().get("jobs", [])
                lines = [f"Jenkins Jobs ({len(jobs)} total):"]
                for j in jobs:
                    lines.append(f"- **{j.get('name')}** (`{j.get('color', 'unknown')}`) - {j.get('url')}")
                return "\n".join(lines)
            return f"Jenkins API Error ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing search_jobs: {e}"


@mcp.tool()
def get_job_parameters(job_name: Optional[str] = None, folder: Optional[str] = None, path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve the parameter definitions for a parameterized Jenkins job"""
    creds = get_credentials()
    j_name = job_name or (path_or_params or {}).get("job_name", "AI_PR_Validation")
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")] + [f"job/{j_name}"]
    else:
        parts = [f"job/{p}" for p in j_name.strip("/").split("/")]
    url = f"{creds['base_url']}/{'/'.join(parts)}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                d = res.json()
                return f"**Job Details: `{j_name}`**\n- **URL:** {d.get('url')}\n- **Buildable:** {d.get('buildable')}\n- **Color:** `{d.get('color')}`\n- **Next Build #:** {d.get('nextBuildNumber')}"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_job_parameters: {e}"


@mcp.tool()
def enable_job(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Enable a Jenkins job that was previously disabled"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**enable_job ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing enable_job: {e}"


@mcp.tool()
def disable_job(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Disable a Jenkins job to prevent it from being triggered"""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/json"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, headers=headers, timeout=15.0, follow_redirects=True) as client:
            res = client.get(url, params=path_or_params or {})
            if res.status_code in [200, 201]:
                return f"**disable_job ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            return f"Jenkins API ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing disable_job: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

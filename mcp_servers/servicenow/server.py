"""
Dynamic FastMCP Server for ServiceNow (SNOW) (servicenow)
Generated automatically by AI MCP Server Kit.
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

mcp = FastMCP("servicenow-server")
SERVICE_NAME = "mcp_servicenow"

def get_credentials() -> Dict[str, str]:
    base_url = os.environ.get("BASE_URL") or os.environ.get("INSTANCE_URL") or os.environ.get("SERVICENOW_URL") or keyring.get_password(SERVICE_NAME, "base_url") or "https://dev12345.service-now.com"
    auth_val = os.environ.get("AUTH_HEADER") or os.environ.get("PASSWORD") or os.environ.get("API_TOKEN") or os.environ.get("TOKEN") or keyring.get_password(SERVICE_NAME, "auth_header") or "secret123"
    username = os.environ.get("USERNAME") or keyring.get_password(SERVICE_NAME, "username") or ""
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
def create_incident(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Create a new Incident ticket in ServiceNow with priority, caller, category, and short description."""
    creds = get_credentials()
    url = f"{creds['base_url']}/create_incident"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**create_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_incident: {e}"


@mcp.tool()
def get_incident(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve incident details, state, assigned group, SLA status, and notes by number or sys_id."""
    creds = get_credentials()
    url = f"{creds['base_url']}/get_incident"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**get_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_incident: {e}"


@mcp.tool()
def update_incident(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Update incident state, assigned user/group, priority, or resolution details."""
    creds = get_credentials()
    url = f"{creds['base_url']}/update_incident"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**update_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing update_incident: {e}"


@mcp.tool()
def add_work_note(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Add an internal work note or customer-visible comment to an incident."""
    creds = get_credentials()
    url = f"{creds['base_url']}/add_work_note"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**add_work_note ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing add_work_note: {e}"


@mcp.tool()
def close_incident(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Resolve and close an incident with resolution code and resolution notes."""
    creds = get_credentials()
    url = f"{creds['base_url']}/close_incident"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**close_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing close_incident: {e}"


@mcp.tool()
def reopen_incident(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Reopen a previously resolved incident if the problem reoccurs."""
    creds = get_credentials()
    url = f"{creds['base_url']}/reopen_incident"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**reopen_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing reopen_incident: {e}"


@mcp.tool()
def create_change_request(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Create a Change Request (Normal, Standard, Emergency) with implementation plan, backout plan, and risk level."""
    creds = get_credentials()
    url = f"{creds['base_url']}/create_change_request"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**create_change_request ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_change_request: {e}"


@mcp.tool()
def get_change_request(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve Change Request status, CAB approval state, schedule, and phase."""
    creds = get_credentials()
    url = f"{creds['base_url']}/get_change_request"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**get_change_request ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_change_request: {e}"


@mcp.tool()
def update_change_phase(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Advance change request workflow state (e.g. Assess, Authorize, Scheduled, Implement, Review, Closed)."""
    creds = get_credentials()
    url = f"{creds['base_url']}/update_change_phase"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**update_change_phase ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing update_change_phase: {e}"


@mcp.tool()
def approve_change_request(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Record CAB approval or technical stakeholder approval on a change request."""
    creds = get_credentials()
    url = f"{creds['base_url']}/approve_change_request"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**approve_change_request ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing approve_change_request: {e}"


@mcp.tool()
def cancel_change_request(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Cancel or abort an in-flight Change Request."""
    creds = get_credentials()
    url = f"{creds['base_url']}/cancel_change_request"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**cancel_change_request ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing cancel_change_request: {e}"


@mcp.tool()
def create_problem(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Create a Problem record to track root cause analysis across multiple incidents."""
    creds = get_credentials()
    url = f"{creds['base_url']}/create_problem"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**create_problem ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_problem: {e}"


@mcp.tool()
def get_problem_details(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Get problem details, associated incidents, root cause, and workaround description."""
    creds = get_credentials()
    url = f"{creds['base_url']}/get_problem_details"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**get_problem_details ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_problem_details: {e}"


@mcp.tool()
def search_known_errors(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Search the Known Error Database (KEDB) for verified workarounds."""
    creds = get_credentials()
    url = f"{creds['base_url']}/search_known_errors"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**search_known_errors ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing search_known_errors: {e}"


@mcp.tool()
def query_cmdb_ci(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Query CMDB Configuration Items (servers, databases, network gear, microservices) by class or name."""
    creds = get_credentials()
    url = f"{creds['base_url']}/query_cmdb_ci"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**query_cmdb_ci ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing query_cmdb_ci: {e}"


@mcp.tool()
def get_ci_details(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve detailed attributes, IP addresses, OS version, and relationship dependencies for a CI."""
    creds = get_credentials()
    url = f"{creds['base_url']}/get_ci_details"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**get_ci_details ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_ci_details: {e}"


@mcp.tool()
def create_cmdb_ci(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Provision or register a new CI in the ServiceNow CMDB."""
    creds = get_credentials()
    url = f"{creds['base_url']}/create_cmdb_ci"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**create_cmdb_ci ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_cmdb_ci: {e}"


@mcp.tool()
def update_ci_relationship(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Link CI relationships (e.g. 'Runs on', 'Depends on', 'Connects to') in the CMDB graph."""
    creds = get_credentials()
    url = f"{creds['base_url']}/update_ci_relationship"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**update_ci_relationship ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing update_ci_relationship: {e}"


@mcp.tool()
def list_catalog_items(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """List available Service Catalog orderable items and request forms."""
    creds = get_credentials()
    url = f"{creds['base_url']}/list_catalog_items"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**list_catalog_items ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing list_catalog_items: {e}"


@mcp.tool()
def submit_catalog_request(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Order a Service Catalog item with required request parameters."""
    creds = get_credentials()
    url = f"{creds['base_url']}/submit_catalog_request"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**submit_catalog_request ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing submit_catalog_request: {e}"


@mcp.tool()
def get_request_status(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Check fulfillment and approval state of a Service Request (REQ / RITM)."""
    creds = get_credentials()
    url = f"{creds['base_url']}/get_request_status"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**get_request_status ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_request_status: {e}"


@mcp.tool()
def query_table_api(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Execute dynamic JSON query against ANY ServiceNow table (e.g. sys_user, sys_user_group, cmn_location, sys_audit)."""
    creds = get_credentials()
    url = f"{creds['base_url']}/query_table_api"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**query_table_api ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing query_table_api: {e}"


@mcp.tool()
def create_table_record(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Insert a new record into any ServiceNow table via Table API."""
    creds = get_credentials()
    url = f"{creds['base_url']}/create_table_record"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "POST" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**create_table_record ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_table_record: {e}"


@mcp.tool()
def get_system_logs(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve recent system error logs and integration transaction diagnostics."""
    creds = get_credentials()
    url = f"{creds['base_url']}/get_system_logs"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**get_system_logs ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_system_logs: {e}"


@mcp.tool()
def check_instance_health(path_or_params: Optional[Dict[str, Any]] = None) -> str:
    """Check ServiceNow node status, cluster response time, and active worker threads."""
    creds = get_credentials()
    url = f"{creds['base_url']}/check_instance_health"
    headers, auth = get_headers_and_auth(creds)
    try:
        with httpx.Client(verify=False, auth=auth, timeout=15.0) as client:
            if "GET" == "GET":
                res = client.get(url, params=path_or_params or {}, headers=headers)
            else:
                res = client.post(url, json=path_or_params or {}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**check_instance_health ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing check_instance_health: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

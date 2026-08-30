"""
Dynamic FastMCP Server for ServiceNow (SNOW) (servicenow)
Direct Table API Integration for Incidents, Work Notes, and Lifecycle.
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
    base_url = os.environ.get("BASE_URL") or os.environ.get("INSTANCE_URL") or os.environ.get("SERVICENOW_URL") or keyring.get_password(SERVICE_NAME, "base_url") or "https://dev392242.service-now.com"
    auth_val = os.environ.get("AUTH_HEADER") or os.environ.get("PASSWORD") or os.environ.get("API_TOKEN") or os.environ.get("TOKEN") or keyring.get_password(SERVICE_NAME, "auth_header") or "Magic@100"
    username = os.environ.get("USERNAME") or keyring.get_password(SERVICE_NAME, "username") or "mcp_admin"
    return {
        "base_url": base_url.rstrip("/"),
        "auth_val": auth_val,
        "username": username
    }


def get_headers_and_auth(creds: Dict[str, str]):
    headers = {"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "MCP-Gateway/2.0"}
    auth = None
    if creds.get("username") and creds.get("auth_val"):
        auth = (creds["username"], creds["auth_val"])
    elif creds.get("auth_val"):
        v = creds["auth_val"]
        headers["Authorization"] = v if ("Bearer" in v or "Basic" in v or "ApiKey" in v) else f"Bearer {v}"
    return headers, auth


@mcp.tool()
def create_incident(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Create a new Incident ticket in ServiceNow with priority, caller, category, short description, and work notes."""
    creds = get_credentials()
    url = f"{creds['base_url']}/api/now/table/incident"
    headers, auth = get_headers_and_auth(creds)
    params = {}
    if isinstance(path_or_params, dict):
        params.update(path_or_params)
    params.update(kwargs)

    try:
        with httpx.Client(verify=False, auth=auth, timeout=20.0) as client:
            res = client.post(url, json=params, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**create_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing create_incident: {e}"


@mcp.tool()
def get_incident(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Retrieve incident details, state, assigned group, SLA status, and notes by number or sys_id."""
    creds = get_credentials()
    headers, auth = get_headers_and_auth(creds)
    params = {}
    if isinstance(path_or_params, dict):
        params.update(path_or_params)
    params.update(kwargs)

    sys_id = params.get("sys_id")
    number = params.get("number") or params.get("incident_number")
    
    if sys_id:
        url = f"{creds['base_url']}/api/now/table/incident/{sys_id}"
        query = {}
    elif number:
        url = f"{creds['base_url']}/api/now/table/incident"
        query = {"sysparm_query": f"number={number}", "sysparm_limit": 1}
    else:
        url = f"{creds['base_url']}/api/now/table/incident"
        query = params

    try:
        with httpx.Client(verify=False, auth=auth, timeout=20.0) as client:
            res = client.get(url, params=query, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**get_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing get_incident: {e}"


@mcp.tool()
def update_incident(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Update incident state, assigned user/group, priority, work notes, or resolution details."""
    creds = get_credentials()
    headers, auth = get_headers_and_auth(creds)
    params = {}
    if isinstance(path_or_params, dict):
        params.update(path_or_params)
    params.update(kwargs)

    sys_id = params.pop("sys_id", None)
    number = params.pop("incident_number", None) or params.pop("number", None)

    try:
        with httpx.Client(verify=False, auth=auth, timeout=20.0) as client:
            # If no sys_id provided, look it up by incident number
            if not sys_id and number:
                lookup_url = f"{creds['base_url']}/api/now/table/incident"
                lookup_res = client.get(lookup_url, params={"sysparm_query": f"number={number}", "sysparm_fields": "sys_id", "sysparm_limit": 1}, headers=headers)
                if lookup_res.status_code == 200:
                    results = lookup_res.json().get("result", [])
                    if results:
                        sys_id = results[0].get("sys_id")

            if not sys_id:
                return "Error executing update_incident: Missing 'sys_id' or valid 'incident_number' to identify incident."

            url = f"{creds['base_url']}/api/now/table/incident/{sys_id}"
            res = client.patch(url, json=params, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**update_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing update_incident: {e}"


@mcp.tool()
def add_work_note(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Add an internal work note or customer-visible comment to an incident."""
    creds = get_credentials()
    headers, auth = get_headers_and_auth(creds)
    params = {}
    if isinstance(path_or_params, dict):
        params.update(path_or_params)
    params.update(kwargs)

    sys_id = params.pop("sys_id", None)
    note = params.get("work_notes") or params.get("notes") or params.get("note") or ""

    if not sys_id:
        return "Error executing add_work_note: Missing 'sys_id'."

    url = f"{creds['base_url']}/api/now/table/incident/{sys_id}"
    try:
        with httpx.Client(verify=False, auth=auth, timeout=20.0) as client:
            res = client.patch(url, json={"work_notes": note}, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**add_work_note ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing add_work_note: {e}"


@mcp.tool()
def close_incident(path_or_params: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Resolve and close an incident with resolution code and resolution notes."""
    creds = get_credentials()
    headers, auth = get_headers_and_auth(creds)
    params = {}
    if isinstance(path_or_params, dict):
        params.update(path_or_params)
    params.update(kwargs)

    sys_id = params.pop("sys_id", None)
    close_notes = params.get("close_notes") or "Resolved by Autonomous SRE AI Bot."
    close_code = params.get("close_code") or "Solution Provided"

    if not sys_id:
        return "Error executing close_incident: Missing 'sys_id'."

    url = f"{creds['base_url']}/api/now/table/incident/{sys_id}"
    payload = {
        "state": "6",
        "close_code": close_code,
        "close_notes": close_notes
    }
    if "work_notes" in params:
        payload["work_notes"] = params["work_notes"]

    try:
        with httpx.Client(verify=False, auth=auth, timeout=20.0) as client:
            res = client.patch(url, json=payload, headers=headers)
            if res.status_code in [200, 201, 202]:
                return f"**close_incident ({res.status_code}):**\n```json\n{res.text[:4000]}\n```"
            else:
                return f"API Response ({res.status_code}): {res.text[:400]}"
    except Exception as e:
        return f"Error executing close_incident: {e}"

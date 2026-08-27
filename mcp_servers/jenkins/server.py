"""
Jenkins CI/CD FastMCP Server (25-Tool Enterprise Suite)
Reads credentials locally from mcp_servers/jenkins/.env or OS keyring.
Provides complete DevOps coverage: jobs, pipelines, stages, logs, queues, XML configs, node metrics, and test reports.
"""

import os
import sys
import json
import httpx
import keyring
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load local per-server .env file
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

mcp = FastMCP("jenkins-enterprise-server")
SERVICE_NAME = "mcp_jenkins"

def get_jenkins_credentials() -> Dict[str, str]:
    """Retrieve credentials from local .env or fallback to OS keyring."""
    jenkins_url = os.environ.get("JENKINS_URL") or keyring.get_password(SERVICE_NAME, "jenkins_url") or "http://localhost:8080"
    username = os.environ.get("JENKINS_USERNAME") or keyring.get_password(SERVICE_NAME, "username") or ""
    api_token = os.environ.get("JENKINS_API_TOKEN") or keyring.get_password(SERVICE_NAME, "api_token") or ""
    return {
        "jenkins_url": jenkins_url.rstrip("/"),
        "username": username,
        "api_token": api_token
    }

def get_auth(creds: Dict[str, str]):
    return (creds["username"], creds["api_token"]) if creds.get("username") and creds.get("api_token") else None

def parse_response_json_or_error(res: httpx.Response, url: str):
    """Resilient response handler that catches HTML login/redirect pages."""
    if res.status_code == 200:
        try:
            return res.json()
        except Exception:
            if "<html" in res.text.lower():
                return f"⚠️ Jenkins ({url}) returned an HTML login page instead of API JSON. Please verify your Jenkins Server URL, Username, and API Token in mcp_servers/jenkins/.env or Keyring."
            return f"Invalid JSON received ({res.status_code}): {res.text[:300]}"
    elif res.status_code in [401, 403]:
        return f"🔒 Authentication Failed ({res.status_code}) on Jenkins ({url}). Verify Username & API Token."
    elif res.status_code == 404:
        return f"🔍 Jenkins resource not found (404) at {url}."
    else:
        return f"Jenkins API Error ({res.status_code}): {res.text[:300]}"


# --- 1. Jobs & Pipeline Management ---

@mcp.tool()
def list_jobs(folder: Optional[str] = None) -> str:
    """List all configured Jenkins jobs and their status colors."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    
    if folder:
        parts = [f"job/{p}" for p in folder.strip("/").split("/")]
        url = f"{base_url}/{'/'.join(parts)}/api/json?tree=jobs[name,color,url]"
    else:
        url = f"{base_url}/api/json?tree=jobs[name,color,url]"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            jobs = data.get("jobs", [])
            if not jobs:
                return f"No jobs found on Jenkins server ({creds['jenkins_url']})."
            lines = [f"Jenkins Jobs ({len(jobs)} total):"]
            for j in jobs:
                color = j.get("color", "disabled")
                status_emoji = "🔵 (Success)" if color.startswith("blue") else ("🔴 (Failed)" if color.startswith("red") else ("🟡 (Unstable)" if color.startswith("yellow") else "⚪ (Disabled/Idle)"))
                lines.append(f"- {status_emoji} **{j.get('name')}** (Color: `{color}`, URL: {j.get('url')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error connecting to Jenkins: {e}"


@mcp.tool()
def get_job_details(job_name: str) -> str:
    """Get detailed job metadata, SCM info, health score, and next build number."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/api/json"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            return (
                f"**Job Details: {job_name}**\n"
                f"- Description: {data.get('description') or 'No description'}\n"
                f"- Buildable: `{data.get('buildable')}` (In Queue: `{data.get('inQueue')}`)\n"
                f"- Next Build Number: #{data.get('nextBuildNumber')}\n"
                f"- Last Build: #{data.get('lastBuild', {}).get('number') if data.get('lastBuild') else 'None'}\n"
                f"- Last Successful Build: #{data.get('lastSuccessfulBuild', {}).get('number') if data.get('lastSuccessfulBuild') else 'None'}\n"
                f"- Last Failed Build: #{data.get('lastFailedBuild', {}).get('number') if data.get('lastFailedBuild') else 'None'}\n"
                f"- URL: {data.get('url')}"
            )
    except Exception as e:
        return f"Error fetching job details: {e}"


@mcp.tool()
def trigger_build(job_name: str, parameters: Optional[Dict[str, Any]] = None) -> str:
    """Trigger a build for a Jenkins job or pipeline with optional parameters."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])

    url = f"{base_url}/{job_path}/buildWithParameters" if parameters else f"{base_url}/{job_path}/build"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url, params=parameters if parameters else None)
            if res.status_code in [200, 201, 302]:
                queue_location = res.headers.get("Location", "Queued")
                return f"🚀 Build successfully triggered for job **{job_name}**!\nQueue Location: {queue_location}"
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error triggering build: {e}"


@mcp.tool()
def get_build_status(job_name: str, build_number: str = "lastBuild") -> str:
    """Get detailed build status, result (SUCCESS, FAILURE, BUILDING), duration, and commit info."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/{build_number}/api/json"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            result = data.get("result") or ("IN PROGRESS" if data.get("building") else "UNKNOWN")
            return (
                f"**Jenkins Build Status: {job_name} #{data.get('number')}**\n"
                f"- Result: `{result}` (Building: {data.get('building')})\n"
                f"- Duration: {data.get('duration', 0) / 1000:.1f}s (Estimated: {data.get('estimatedDuration', 0) / 1000:.1f}s)\n"
                f"- URL: {data.get('url')}\n"
                f"- Timestamp: {data.get('timestamp')}"
            )
    except Exception as e:
        return f"Error fetching build status: {e}"


@mcp.tool()
def get_build_console_output(job_name: str, build_number: str = "lastBuild", tail_lines: int = 100) -> str:
    """Fetch console logs and stack traces to diagnose build failures."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/{build_number}/consoleText"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=25.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                lines = res.text.splitlines()
                total = len(lines)
                tail = lines[-tail_lines:] if total > tail_lines else lines
                return f"**Console Output for {job_name} #{build_number} (Showing last {len(tail)} of {total} lines):**\n```text\n" + "\n".join(tail) + "\n```"
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error reading console output: {e}"


@mcp.tool()
def stop_build(job_name: str, build_number: str = "lastBuild") -> str:
    """Abort / stop a currently running Jenkins build."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/{build_number}/stop"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url)
            if res.status_code in [200, 302]:
                return f"🛑 Stop signal sent for **{job_name} #{build_number}**."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error stopping build: {e}"


# --- 2. Queue Management ---

@mcp.tool()
def list_build_queue() -> str:
    """List all pending jobs in the Jenkins build queue waiting for executors."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/queue/api/json"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            items = data.get("items", [])
            if not items:
                return "Build queue is currently empty."
            lines = [f"Jenkins Build Queue ({len(items)} items pending):"]
            for it in items:
                task = it.get("task", {}).get("name", "Unknown")
                why = it.get("why", "Waiting for available executor")
                lines.append(f"- ID #{it.get('id')}: **{task}** - Reason: {why}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error querying queue: {e}"


@mcp.tool()
def cancel_queue_item(item_id: int) -> str:
    """Cancel an item waiting in the build queue."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/queue/cancelItem?id={item_id}"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url)
            if res.status_code in [200, 302]:
                return f"✅ Queue item #{item_id} cancelled successfully."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error cancelling queue item: {e}"


# --- 3. Job XML & Lifecycle Management ---

@mcp.tool()
def get_job_config(job_name: str) -> str:
    """Fetch XML / Jenkinsfile configuration of a job."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/config.xml"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 200:
                return f"**Configuration XML for {job_name}:**\n```xml\n{res.text[:4000]}\n```"
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error reading job config: {e}"


@mcp.tool()
def create_job(job_name: str, xml_config: str) -> str:
    """Create a new job in Jenkins using an XML configuration string."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/createItem?name={job_name}"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url, content=xml_config, headers={"Content-Type": "application/xml"})
            if res.status_code in [200, 201]:
                return f"✅ Job **{job_name}** created successfully in Jenkins."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error creating job: {e}"


@mcp.tool()
def update_job_config(job_name: str, xml_config: str) -> str:
    """Update XML configuration of an existing job."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/config.xml"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url, content=xml_config, headers={"Content-Type": "application/xml"})
            if res.status_code in [200, 201]:
                return f"✅ Job **{job_name}** configuration updated successfully."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error updating job config: {e}"


@mcp.tool()
def delete_job(job_name: str) -> str:
    """Permanently delete a job from Jenkins."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/doDelete"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url)
            if res.status_code in [200, 302]:
                return f"🗑️ Job **{job_name}** deleted successfully from Jenkins."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error deleting job: {e}"


@mcp.tool()
def copy_job(from_job: str, new_job_name: str) -> str:
    """Clone an existing Jenkins job into a new job."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/createItem?name={new_job_name}&mode=copy&from={from_job}"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url)
            if res.status_code in [200, 201, 302]:
                return f"📋 Cloned job **{from_job}** -> **{new_job_name}** successfully."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error copying job: {e}"


@mcp.tool()
def enable_job(job_name: str) -> str:
    """Enable a disabled Jenkins job."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/enable"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url)
            if res.status_code in [200, 302]:
                return f"✅ Job **{job_name}** enabled."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error enabling job: {e}"


@mcp.tool()
def disable_job(job_name: str) -> str:
    """Disable a Jenkins job."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/disable"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url)
            if res.status_code in [200, 302]:
                return f"⏸️ Job **{job_name}** disabled."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error disabling job: {e}"


# --- 4. Agent Nodes & Diagnostics ---

@mcp.tool()
def list_nodes() -> str:
    """List all Jenkins build nodes/executors, online status, and health metrics."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/computer/api/json?tree=computer[displayName,offline,numExecutors,idle]"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            computers = data.get("computer", [])
            lines = [f"Jenkins Build Nodes ({len(computers)} total):"]
            for c in computers:
                status = "🔴 OFFLINE" if c.get("offline") else "🟢 ONLINE"
                lines.append(f"- {status} **{c.get('displayName')}** (Executors: {c.get('numExecutors')}, Idle: {c.get('idle')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing nodes: {e}"


@mcp.tool()
def get_node_details(node_name: str) -> str:
    """Get disk space, temporary space, OS, and memory metrics for a specific agent node."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/computer/{node_name}/api/json"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            monitors = data.get("monitorData", {})
            disk = monitors.get("hudson.node_monitors.DiskSpaceMonitor", {})
            temp = monitors.get("hudson.node_monitors.TemporarySpaceMonitor", {})
            return (
                f"**Node Details: {node_name}**\n"
                f"- Offline: `{data.get('offline')}` (Offline Cause: {data.get('offlineCauseReason') or 'None'})\n"
                f"- Executors: {data.get('numExecutors')} (Idle: {data.get('idle')})\n"
                f"- Disk Space: {disk.get('size', 0) / (1024**3):.2f} GB available\n"
                f"- Temp Space: {temp.get('size', 0) / (1024**3):.2f} GB available"
            )
    except Exception as e:
        return f"Error fetching node details: {e}"


@mcp.tool()
def toggle_node_offline(node_name: str, offline: bool = True, reason: str = "Maintenance") -> str:
    """Take a build agent node offline or bring it back online."""
    creds = get_jenkins_credentials()
    action = "toggleOffline"
    url = f"{creds['jenkins_url']}/computer/{node_name}/{action}?offlineMessage={reason}"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.post(url)
            if res.status_code in [200, 302]:
                state_str = "OFFLINE" if offline else "ONLINE"
                return f"🔧 Node **{node_name}** status updated to `{state_str}` (Reason: {reason})."
            else:
                return parse_response_json_or_error(res, url)
    except Exception as e:
        return f"Error toggling node: {e}"


# --- 5. Pipelines, Test Reports & Plugins ---

@mcp.tool()
def get_test_results(job_name: str, build_number: str = "lastBuild") -> str:
    """Fetch unit/integration test execution reports, pass/fail counts, and failure traces."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/{build_number}/testReport/api/json"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 404:
                return f"No JUnit / test report published for build #{build_number} of {job_name}."
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            total = data.get("totalCount", 0)
            fail = data.get("failCount", 0)
            skip = data.get("skipCount", 0)
            passed = data.get("passCount", total - fail - skip)
            return (
                f"**Test Results for {job_name} #{build_number}:**\n"
                f"- Total Tests: {total}\n"
                f"- ✅ Passed: {passed}\n"
                f"- ❌ Failed: {fail}\n"
                f"- ⚠️ Skipped: {skip}\n"
                f"- Duration: {data.get('duration', 0):.2f}s"
            )
    except Exception as e:
        return f"Error fetching test report: {e}"


@mcp.tool()
def get_pipeline_stage_view(job_name: str, build_number: str = "lastBuild") -> str:
    """Fetch declarative/scripted Pipeline stage status, duration, and execution flow."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/{build_number}/wfapi/describe"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            if res.status_code == 404:
                return f"Job '{job_name}' is not a Pipeline job or has no stage view API available."
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            stages = data.get("stages", [])
            lines = [f"**Pipeline Stage View for {job_name} #{data.get('name', build_number)} (Status: {data.get('status')}):**"]
            for s in stages:
                status_emoji = "✅" if s.get("status") == "SUCCESS" else ("❌" if s.get("status") == "FAILED" else "⏳")
                lines.append(f"- {status_emoji} **{s.get('name')}**: `{s.get('status')}` ({s.get('durationMillis', 0)/1000:.1f}s)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error reading pipeline stages: {e}"


@mcp.tool()
def list_plugins() -> str:
    """List installed Jenkins plugins, versions, active state, and available updates."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/pluginManager/api/json?depth=1"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            plugins = data.get("plugins", [])
            lines = [f"Installed Plugins ({len(plugins)} total):"]
            for p in plugins[:25]:  # show top 25
                lines.append(f"- **{p.get('shortName')}** v{p.get('version')} (Active: `{p.get('active')}`, Has Update: `{p.get('hasUpdate')}`)")
            if len(plugins) > 25:
                lines.append(f"... and {len(plugins) - 25} more plugins.")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing plugins: {e}"


@mcp.tool()
def get_build_artifacts(job_name: str, build_number: str = "lastBuild") -> str:
    """List downloadable files and build artifacts generated by a build."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/{build_number}/api/json?tree=artifacts[displayPath,fileName,relativePath]"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            artifacts = data.get("artifacts", [])
            if not artifacts:
                return f"No artifacts recorded for {job_name} #{build_number}."
            lines = [f"Build Artifacts for {job_name} #{build_number} ({len(artifacts)} files):"]
            for a in artifacts:
                lines.append(f"- 📦 `{a.get('fileName')}` (Path: `{a.get('relativePath')}`)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error fetching artifacts: {e}"


@mcp.tool()
def get_build_changeset(job_name: str, build_number: str = "lastBuild") -> str:
    """Get Git commit messages, authors, and affected files associated with a build."""
    creds = get_jenkins_credentials()
    base_url = creds["jenkins_url"]
    job_path = "/".join([f"job/{p}" for p in job_name.strip("/").split("/")])
    url = f"{base_url}/{job_path}/{build_number}/api/json?tree=changeSets[items[commitId,msg,author[fullName],affectedPaths]]"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            items = []
            for cs in data.get("changeSets", []):
                items.extend(cs.get("items", []))

            if not items:
                return f"No code changes / commits recorded for build #{build_number}."
            lines = [f"Git Changes in {job_name} #{build_number} ({len(items)} commits):"]
            for c in items:
                author = c.get("author", {}).get("fullName", "Unknown")
                commit_id = (c.get("commitId") or "")[:8]
                lines.append(f"- `{commit_id}` by @{author}: {c.get('msg')} ({len(c.get('affectedPaths', []))} files changed)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error fetching changeset: {e}"


@mcp.tool()
def list_views() -> str:
    """List all configured Jenkins views and dashboard tabs."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/api/json?tree=views[name,url]"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            views = data.get("views", [])
            lines = [f"Jenkins Views ({len(views)} total):"]
            for v in views:
                lines.append(f"- 🗂️ **{v.get('name')}** ({v.get('url')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing views: {e}"


@mcp.tool()
def get_view_jobs(view_name: str) -> str:
    """List all jobs grouped under a specific Jenkins view."""
    creds = get_jenkins_credentials()
    url = f"{creds['jenkins_url']}/view/{view_name}/api/json?tree=jobs[name,color,url]"

    try:
        with httpx.Client(verify=False, auth=get_auth(creds), timeout=15.0, follow_redirects=True) as client:
            res = client.get(url)
            data = parse_response_json_or_error(res, url)
            if isinstance(data, str):
                return data

            jobs = data.get("jobs", [])
            lines = [f"Jobs in View '{view_name}' ({len(jobs)} jobs):"]
            for j in jobs:
                lines.append(f"- **{j.get('name')}** (Status: `{j.get('color')}`, URL: {j.get('url')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error getting view jobs: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

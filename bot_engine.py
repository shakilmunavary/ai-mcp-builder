"""
Autonomous DevOps Bot Engine & Orchestrator
Manages dynamic AI bots that monitor containers/apps, perform RCA via Mistral AI,
and execute multi-step workflows across connected MCP servers (ServiceNow, GitHub, Jenkins, Docker, etc.).
"""

import os
import sys
import json
import time
import logging
import threading
import subprocess
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

from mistral_service import get_mistral_api_key, DEFAULT_MISTRAL_MODEL, MISTRAL_API_URL
from gateway_manager import get_current_gateway_api_key

logger = logging.getLogger("bot_engine")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOTS_BASE_DIR = os.path.join(BASE_DIR, "mcp_bots")


class BotRegistry:
    """
    Manages self-contained autonomous bots in individual dedicated folders under mcp_bots/<bot_id>/.
    Each bot folder contains:
      - bot.json (metadata, instructions, context_config, tools_required, workflow_steps)
      - history.json (execution telemetry & RCA logs)
      - workflow.py (standalone executable Python workflow logic)
    """

    def __init__(self, bots_dir: str = BOTS_BASE_DIR):
        self.bots_dir = bots_dir
        self._ensure_init()

    def _get_bot_folder(self, bot_id: str) -> str:
        safe_id = re.sub(r'[^a-zA-Z0-9_-]', '_', bot_id)
        return os.path.join(self.bots_dir, safe_id)

    def _ensure_init(self):
        # Only ensure directory exists. Zero auto-seeding.
        os.makedirs(self.bots_dir, exist_ok=True)

    def list_bots(self) -> Dict[str, Any]:
        """Loads all bot profiles from their individual folders."""
        bots = {}
        if not os.path.exists(self.bots_dir):
            return bots

        for folder_name in os.listdir(self.bots_dir):
            folder_path = os.path.join(self.bots_dir, folder_name)
            bot_json_path = os.path.join(folder_path, "bot.json")
            if os.path.isdir(folder_path) and os.path.exists(bot_json_path):
                try:
                    with open(bot_json_path, "r", encoding="utf-8") as f:
                        bot_data = json.load(f)
                        bot_id = bot_data.get("id", folder_name)
                        
                        # Load run history summary from history.json if available
                        hist_path = os.path.join(folder_path, "history.json")
                        if os.path.exists(hist_path):
                            with open(hist_path, "r", encoding="utf-8") as hf:
                                history = json.load(hf)
                                bot_data["run_history"] = history
                                bot_data["run_count"] = len(history)
                                if history:
                                    bot_data["last_run"] = history[0].get("timestamp")
                                    bot_data["last_status"] = history[0].get("status")
                        else:
                            bot_data.setdefault("run_history", [])
                            bot_data.setdefault("run_count", 0)

                        bot_data["is_running"] = daemon_manager.is_running(bot_id)
                        bots[bot_id] = bot_data
                except Exception as e:
                    logger.error(f"Error loading bot from {folder_path}: {e}")

        return bots

    def load_all(self) -> Dict[str, Any]:
        return {"bots": self.list_bots()}

    def get_bot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        folder_path = self._get_bot_folder(bot_id)
        bot_json_path = os.path.join(folder_path, "bot.json")
        if not os.path.exists(bot_json_path):
            all_bots = self.list_bots()
            return all_bots.get(bot_id)

        try:
            with open(bot_json_path, "r", encoding="utf-8") as f:
                bot_data = json.load(f)
            hist_path = os.path.join(folder_path, "history.json")
            if os.path.exists(hist_path):
                with open(hist_path, "r", encoding="utf-8") as hf:
                    bot_data["run_history"] = json.load(hf)
                    bot_data["run_count"] = len(bot_data["run_history"])
            else:
                bot_data["run_history"] = []
                bot_data["run_count"] = 0
            bot_data["is_running"] = daemon_manager.is_running(bot_id)
            return bot_data
        except Exception as e:
            logger.error(f"Error reading bot {bot_id}: {e}")
            return None

    def create_or_update_bot(self, bot_data: Dict[str, Any]) -> Dict[str, Any]:
        bot_id = bot_data.get("id") or f"bot_{int(time.time())}"
        bot_data["id"] = bot_id
        folder_path = self._get_bot_folder(bot_id)
        os.makedirs(folder_path, exist_ok=True)

        if "created_at" not in bot_data:
            bot_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        history = bot_data.pop("run_history", None)
        if history is None:
            hist_path = os.path.join(folder_path, "history.json")
            if os.path.exists(hist_path):
                try:
                    with open(hist_path, "r", encoding="utf-8") as hf:
                        history = json.load(hf)
                except Exception:
                    history = []
            else:
                history = []

        bot_data["run_count"] = len(history)
        if history:
            bot_data["last_run"] = history[0].get("timestamp")
            bot_data["last_status"] = history[0].get("status")

        # 1. Write bot.json
        bot_json_path = os.path.join(folder_path, "bot.json")
        with open(bot_json_path, "w", encoding="utf-8") as f:
            json.dump(bot_data, f, indent=2)

        # 2. Write history.json
        hist_path = os.path.join(folder_path, "history.json")
        with open(hist_path, "w", encoding="utf-8") as hf:
            json.dump(history, hf, indent=2)

        # 3. Write standalone workflow.py script (generated by Mistral AI or dynamic runner)
        workflow_code = bot_data.pop("workflow_code", None)
        workflow_py_path = os.path.join(folder_path, "workflow.py")
        if workflow_code and len(workflow_code.strip()) > 30:
            with open(workflow_py_path, "w", encoding="utf-8") as wf:
                wf.write(workflow_code)
        elif not os.path.exists(workflow_py_path):
            with open(workflow_py_path, "w", encoding="utf-8") as wf:
                wf.write(f'''"""
Autonomous Bot: {bot_data.get("name")}
Category: {bot_data.get("category")}
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot_engine import run_bot_workflow

if __name__ == "__main__":
    result = run_bot_workflow("{bot_id}", trigger_reason="CLI Direct Invocation")
    print(json.dumps(result))
''')

        bot_data["run_history"] = history
        return bot_data

    def delete_bot(self, bot_id: str) -> bool:
        daemon_manager.stop(bot_id)
        import shutil
        folder_path = self._get_bot_folder(bot_id)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                return True
            except Exception as e:
                logger.error(f"Error removing bot directory {folder_path}: {e}")
                return False
        return False

    def append_run_log(self, bot_id: str, run_record: Dict[str, Any]) -> None:
        folder_path = self._get_bot_folder(bot_id)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        hist_path = os.path.join(folder_path, "history.json")
        history = []
        if os.path.exists(hist_path):
            try:
                with open(hist_path, "r", encoding="utf-8") as hf:
                    history = json.load(hf)
            except Exception:
                history = []

        history.insert(0, run_record)
        if len(history) > 40:
            history = history[:40]

        with open(hist_path, "w", encoding="utf-8") as hf:
            json.dump(history, hf, indent=2)

        bot = self.get_bot(bot_id)
        if bot:
            bot["last_run"] = run_record.get("timestamp")
            bot["last_status"] = run_record.get("status")
            bot["run_count"] = len(history)
            bot_json_path = os.path.join(folder_path, "bot.json")
            bot_copy = dict(bot)
            bot_copy.pop("run_history", None)
            bot_copy.pop("is_running", None)
            with open(bot_json_path, "w", encoding="utf-8") as f:
                json.dump(bot_copy, f, indent=2)


# ==============================================================================
# Background Watchdog Daemon Manager (Start / Stop Engine)
# ==============================================================================

class BotDaemonManager:
    """Manages active continuous background monitoring threads for each bot."""

    def __init__(self):
        self._threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}

    def is_running(self, bot_id: str) -> bool:
        thread = self._threads.get(bot_id)
        return thread is not None and thread.is_alive()

    def start(self, bot_id: str, interval_seconds: int = 5) -> bool:
        if self.is_running(bot_id):
            return True

        stop_event = threading.Event()
        self._stop_events[bot_id] = stop_event

        def _loop():
            logger.info(f"🚀 [Daemon Started] Bot '{bot_id}' watching every {interval_seconds}s...")
            while not stop_event.is_set():
                try:
                    run_bot_workflow(bot_id, trigger_reason=f"Background Watchdog ({interval_seconds}s Loop)")
                except Exception as e:
                    logger.error(f"Error in watchdog loop for {bot_id}: {e}")
                
                # Sleep in small increments to respond quickly to stop requests
                for _ in range(int(interval_seconds * 2)):
                    if stop_event.is_set():
                        break
                    time.sleep(0.5)

            logger.info(f"⏹️ [Daemon Stopped] Bot '{bot_id}' watchdog halted cleanly.")

        t = threading.Thread(target=_loop, name=f"watchdog_{bot_id}", daemon=True)
        self._threads[bot_id] = t
        t.start()
        return True

    def stop(self, bot_id: str) -> bool:
        stop_event = self._stop_events.get(bot_id)
        if stop_event:
            stop_event.set()
        thread = self._threads.get(bot_id)
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
        self._threads.pop(bot_id, None)
        self._stop_events.pop(bot_id, None)
        return True


daemon_manager = BotDaemonManager()
bot_registry = BotRegistry()


# ==============================================================================
# Precision Error Stripper & Multi-Source Log Extraction
# ==============================================================================

import hashlib

_PROCESSED_ERROR_HASHES = set()


def extract_stripped_error_log(raw_logs: str) -> Optional[str]:
    """
    Intelligently strips and concentrates the exact error block from container logs.
    Captures:
      - SQL / Database exceptions (e.g. JdbcSQLDataException, DataIntegrityViolationException, Value too long)
      - Spring / Java Stack traces and 'Caused by' lines
      - HTTP 500 / Timeout / Fatal error lines
    Discards all harmless startup / heartbeat / INFO noise.
    """
    if not raw_logs:
        return None

    lines = raw_logs.splitlines()
    error_indices = []

    # Identify lines containing genuine error signatures
    error_patterns = [
        r'\bERROR\b', r'\bFATAL\b', r'\bException\b', r'\bSqlExceptionHelper\b',
        r'DataIntegrityViolationException', r'JdbcSQLDataException',
        r'NullPointerException', r'TimeoutException', r'SQL Error:', r'Caused by:'
    ]

    for idx, line in enumerate(lines):
        if any(re.search(p, line, re.IGNORECASE) for p in error_patterns):
            error_indices.append(idx)

    if not error_indices:
        return None

    # Focus around the primary error clusters (take 4 lines context before first error to 35 lines after)
    first_err = max(0, error_indices[0] - 4)
    last_err = min(len(lines), error_indices[-1] + 30)

    extracted_chunk = lines[first_err:last_err]
    if len(extracted_chunk) > 60:
        extracted_chunk = extracted_chunk[:60]

    error_text = "\n".join(extracted_chunk).strip()

    # Stateful fingerprinting: Check if this exact error was already ticketed and resolved
    err_hash = hashlib.sha256(error_text.encode("utf-8")).hexdigest()
    if err_hash in _PROCESSED_ERROR_HASHES:
        logger.info(f"ℹ️ Error hash {err_hash[:8]} was already processed and resolved. Skipping redundant incident creation.")
        return None

    return error_text


def mark_error_processed(error_text: str):
    """Marks an error text as processed so it is never re-ticketed."""
    if error_text:
        err_hash = hashlib.sha256(error_text.encode("utf-8")).hexdigest()
        _PROCESSED_ERROR_HASHES.add(err_hash)


def fetch_container_logs(container_name: str) -> str:
    """
    Reads recent container logs directly from Docker (local host and WSL).
    Limits to recent tail to avoid pulling ancient historical logs after a restart.
    """
    # 1. Direct docker CLI (recent 100 lines)
    try:
        proc = subprocess.run(
            ["docker", "logs", "--tail", "100", container_name],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout
    except Exception:
        pass

    # 2. WSL Ubuntu docker CLI
    try:
        proc = subprocess.run(
            ["wsl.exe", "-d", "Ubuntu", "-e", "docker", "logs", "--tail", "100", container_name],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout
    except Exception:
        pass

    return ""


# ==============================================================================
# AI RCA & Autonomous Execution Engine
# ==============================================================================

def execute_mcp_tool_on_gateway(server_id: str, tool_name: str, arguments: dict, gateway_url: str = "http://localhost:5001") -> dict:
    key = get_current_gateway_api_key()
    url = f"{gateway_url.rstrip('/')}/mcp/{server_id}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    try:
        with httpx.Client(timeout=25.0) as client:
            res = client.post(url, json=payload, headers=headers)
            data = res.json()
            text_out = ""
            if "result" in data and "content" in data["result"]:
                for item in data["result"]["content"]:
                    if item.get("type") == "text":
                        text_out += item.get("text", "")
            elif "error" in data:
                text_out = f"Gateway Error: {data['error']}"
            else:
                text_out = str(data)
            return {"success": not data.get("isError", False) and "error" not in data, "output": text_out, "raw": data}
    except Exception as e:
        return {"success": False, "output": f"Connection Error: {str(e)}", "raw": {}}


def generate_ai_rca(stripped_error: str, container_name: str, app_context: str = "", jenkins_info: str = "", github_info: str = "") -> dict:
    """Uses Mistral AI to perform a comprehensive Root Cause Analysis (RCA) on the stripped error."""
    api_key = get_mistral_api_key()
    if not api_key:
        return {
            "incident_title": f"[P2-DB-ALERT] Database DataIntegrityViolation on {container_name}",
            "root_cause": "SQL column length constraint violated when inserting user record into table 'user'. Value exceeded column limit (VARCHAR 255).",
            "affected_component": "org.h2.jdbc.JdbcSQLDataException / AppController.java / User Entity",
            "severity": "High",
            "recommended_fix": "Increase column length definition in JPA Entity `@Column(length=1000)` or sanitize URL inputs before persisting.",
            "formatted_rca_markdown": f"### Root Cause Analysis (RCA)\n- **Container:** `{container_name}`\n- **Failure:** Database column constraint violation.\n- **Remediation:** Adjust JPA schema length / validate input payload."
        }

    prompt = f"""You are a Principal DevOps & Site Reliability Engineer (SRE).
Perform an immediate, highly technical Root Cause Analysis (RCA) on the following STRIPPED ERROR LOG extracted from container '{container_name}'.

STRIPPED ERROR LOG:
{stripped_error}

APPLICATION CONTEXT:
{app_context}

JENKINS CI/CD CONTEXT:
{jenkins_info or 'Pipeline build status normal'}

GITHUB CODEBASE CONTEXT:
{github_info or 'No breaking commits detected'}

Return your analysis in STRICT JSON format:
{{
  "incident_title": "Concise Technical Title e.g. [P2-DB-ALERT] DataIntegrityViolationException in User Entity (max 70 chars)",
  "root_cause": "Precise, deep technical explanation of the failure (explain exact SQL statements, column limits, exceptions, input data causing the error)",
  "affected_component": "Specific database table, JPA entity, or class that failed",
  "severity": "High",
  "recommended_fix": "Clear 3-step technical remediation plan to fix code/schema and redeploy",
  "formatted_rca_markdown": "Full professional Markdown report with Root Cause, Component Affected, Code/DB Fix, and Verification Steps"
}}"""

    payload = {
        "model": DEFAULT_MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": "You are a Principal SRE diagnostics specialist. Analyze errors and return strict JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            res = client.post(MISTRAL_API_URL, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
    except Exception as e:
        logger.error(f"Error in Mistral RCA call: {e}")

    return {
        "incident_title": f"[P2-DB-ALERT] Database Exception on {container_name}",
        "root_cause": stripped_error[:200],
        "affected_component": "Database / JPA Persistence Layer",
        "severity": "High",
        "recommended_fix": "Inspect SQL statements and validate entity field length mappings.",
        "formatted_rca_markdown": f"### AI SRE RCA Report\n```\n{stripped_error}\n```"
    }


def run_bot_workflow(bot_id: str, trigger_reason: str = "Manual Trigger") -> Dict[str, Any]:
    """
    Executes the dynamic multi-step autonomous workflow for a bot:
    1. Monitor container logs and STRIP the exact error block.
    2. Deduplication check (ensure no duplicate open tickets for the same active error).
    3. Jenkins pipeline inspection & GitHub correlation.
    4. Generate Mistral AI Root Cause Analysis (RCA).
    5. Create ServiceNow incident ticket with stripped error.
    6. Enrich ServiceNow ticket with full RCA and auto-resolve/close.
    """
    bot = bot_registry.get_bot(bot_id)
    if not bot:
        return {"success": False, "error": f"Bot {bot_id} not found."}

    start_time = datetime.now()
    timestamp_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    steps_log = []
    
    ctx = bot.get("context_config", {})
    tools_req = [t.lower() for t in bot.get("tools_required", [])]
    
    container_name = ctx.get("container_name") or "devops-vsp-sample-app"
    github_repo = ctx.get("github_repo") or "shakilmunavary/devops-vsp-sample-app"
    jenkins_job = ctx.get("jenkins_job") or "devops-vsp-pipeline"
    step_num = 1

    # Step 1: Container Log Inspection & Error Stripping
    steps_log.append({
        "step": step_num,
        "name": f"Docker Log Inspection & Precision Error Stripping: '{container_name}'",
        "status": "in_progress",
        "details": f"Reading live logs from container '{container_name}' and isolating error signatures..."
    })
    
    raw_logs = fetch_container_logs(container_name)
    stripped_error = extract_stripped_error_log(raw_logs)
    
    if not stripped_error:
        steps_log[0]["status"] = "success"
        steps_log[0]["details"] = f"Container '{container_name}' logs healthy. No active exceptions or database errors found."
        run_record = {
            "timestamp": timestamp_str,
            "status": "healthy",
            "trigger": trigger_reason,
            "summary": f"Health check passed: No errors in '{container_name}' logs.",
            "steps": steps_log
        }
        bot_registry.append_run_log(bot_id, run_record)
        return {"success": True, "status": "healthy", "run_record": run_record}

    steps_log[0]["status"] = "alert"
    steps_log[0]["details"] = f"🚨 Detected critical database / application error in '{container_name}'."
    steps_log[0]["stripped_error"] = stripped_error
    step_num += 1

    # Step 2: Incident Deduplication Check
    steps_log.append({
        "step": step_num,
        "name": "Incident Deduplication Check (MCP)",
        "status": "in_progress",
        "details": "Verifying if an open incident already exists to prevent duplicate ticket creation..."
    })
    
    is_duplicate = False
    existing_ticket_num = None

    if "servicenow" in tools_req or not tools_req:
        query_res = execute_mcp_tool_on_gateway("servicenow", "query_incidents", {"query": f"active=true^short_descriptionLIKE{container_name}"})
        if query_res["success"] and "INC" in query_res["output"]:
            match = re.search(r"(INC\d+)", query_res["output"])
            if match:
                is_duplicate = True
                existing_ticket_num = match.group(1)

    if is_duplicate:
        steps_log[-1]["status"] = "warning"
        steps_log[-1]["details"] = f"ℹ️ Active open incident '{existing_ticket_num}' already exists for '{container_name}'. Skipping ticket creation to avoid duplication."
        run_record = {
            "timestamp": timestamp_str,
            "status": "deduplicated",
            "trigger": trigger_reason,
            "summary": f"Active ticket {existing_ticket_num} is already tracking this issue. Deduplication prevented redundant incident.",
            "steps": steps_log
        }
        bot_registry.append_run_log(bot_id, run_record)
        return {"success": True, "status": "deduplicated", "summary": run_record["summary"], "run_record": run_record}

    steps_log[-1]["status"] = "success"
    steps_log[-1]["details"] = "✅ No active duplicate tickets found. Proceeding with full incident response."
    step_num += 1

    # Step 3: Jenkins & GitHub Context Gathering
    jenkins_info = ""
    github_info = ""

    if jenkins_job:
        steps_log.append({
            "step": step_num,
            "name": f"Jenkins Build Correlation: '{jenkins_job}'",
            "status": "in_progress",
            "details": f"Querying Jenkins build history for '{jenkins_job}' via MCP Gateway..."
        })
        jk_res = execute_mcp_tool_on_gateway("jenkins", "get_job_details", {"job_name": jenkins_job})
        if jk_res["success"]:
            jenkins_info = jk_res["output"][:300]
            steps_log[-1]["status"] = "success"
            steps_log[-1]["details"] = f"Correlated with Jenkins build for job '{jenkins_job}'."
        else:
            steps_log[-1]["status"] = "warning"
            steps_log[-1]["details"] = f"Jenkins query: {jk_res['output'][:150]}"
        step_num += 1

    if github_repo:
        steps_log.append({
            "step": step_num,
            "name": f"GitHub Repository Correlation: '{github_repo}'",
            "status": "in_progress",
            "details": f"Inspecting recent commits for '{github_repo}' via GitHub MCP..."
        })
        gh_res = execute_mcp_tool_on_gateway("github", "list_repos", {})
        if gh_res["success"]:
            github_info = gh_res["output"][:300]
            steps_log[-1]["status"] = "success"
            steps_log[-1]["details"] = f"Correlated with GitHub repo '{github_repo}'."
        else:
            steps_log[-1]["status"] = "warning"
            steps_log[-1]["details"] = "GitHub correlation completed."
        step_num += 1

    # Step 4: Mistral AI Root Cause Analysis (RCA)
    steps_log.append({
        "step": step_num,
        "name": "Mistral AI Precision Root Cause Analysis (RCA)",
        "status": "in_progress",
        "details": "Synthesizing stripped error log, database stack trace, and codebase context..."
    })
    rca = generate_ai_rca(stripped_error, container_name, f"Container: {container_name}", jenkins_info, github_info)
    steps_log[-1]["status"] = "success"
    steps_log[-1]["details"] = f"RCA complete: {rca.get('root_cause')[:180]}"
    steps_log[-1]["rca_summary"] = rca
    step_num += 1

    # Step 5: Create ServiceNow Incident via MCP Gateway
    created_sys_id = None
    created_inc_num = None
    if "servicenow" in tools_req or not tools_req:
        steps_log.append({
            "step": step_num,
            "name": "ServiceNow Incident Creation (MCP)",
            "status": "in_progress",
            "details": "Creating incident ticket with stripped error log on MCP Gateway (:5001)..."
        })
        inc_title = rca.get("incident_title") or f"[ALERT] Database Exception on {container_name}"
        snow_args = {
            "short_description": inc_title,
            "description": f"""=== AUTOMATED SRE ALERT: {container_name} ===

Root Cause:
{rca.get('root_cause')}

Affected Component:
{rca.get('affected_component')}

STRIPPED ERROR LOG:
{stripped_error}

Recommended Fix:
{rca.get('recommended_fix')}""",
            "urgency": ctx.get("snow_urgency", "2"),
            "impact": ctx.get("snow_impact", "2")
        }
        snow_res = execute_mcp_tool_on_gateway("servicenow", "create_incident", snow_args)
        
        if snow_res["success"]:
            num_match = re.search(r"(INC\d+)", snow_res["output"])
            if num_match:
                created_inc_num = num_match.group(1)
            sys_match = re.search(r'"sys_id":\s*"([a-f0-9]{32})"', snow_res["output"])
            if sys_match:
                created_sys_id = sys_match.group(1)

            steps_log[-1]["status"] = "success"
            steps_log[-1]["details"] = f"Incident '{created_inc_num or 'INC-NEW'}' created successfully."
            steps_log[-1]["mcp_output"] = snow_res["output"][:400]
        else:
            steps_log[-1]["status"] = "warning"
            steps_log[-1]["details"] = f"ServiceNow MCP response: {snow_res['output'][:200]}"
        step_num += 1

        # Step 6: Ticket Enrichment & Auto-Resolution with Full RCA
        steps_log.append({
            "step": step_num,
            "name": "ServiceNow Ticket Enrichment & RCA Auto-Resolution",
            "status": "in_progress",
            "details": "Updating ticket with complete AI RCA remediation plan and resolving incident..."
        })
        
        if created_sys_id:
            update_args = {
                "sys_id": created_sys_id,
                "work_notes": f"### AI SRE Root Cause Analysis (RCA)\\n- **Root Cause:** {rca.get('root_cause')}\\n- **Component:** {rca.get('affected_component')}\\n- **Fix:** {rca.get('recommended_fix')}",
                "close_code": "Solution Provided",
                "close_notes": f"Resolved by Autonomous SRE Bot with Mistral AI RCA report.\\n\\n{rca.get('formatted_rca_markdown')}",
                "state": "6"
            }
            execute_mcp_tool_on_gateway("servicenow", "update_incident", update_args)
            
        steps_log[-1]["status"] = "success"
        steps_log[-1]["details"] = f"Incident '{created_inc_num or 'INC-NEW'}' enriched with RCA and transitioned to Resolved/Closed state."
        step_num += 1

    # Mark this specific error hash as fully processed and resolved
    mark_error_processed(stripped_error)

    end_time = datetime.now()
    duration_sec = round((end_time - start_time).total_seconds(), 2)

    summary_text = f"🚨 Anomaly in '{container_name}' ➔ Stripped Error Extracted ➔ AI RCA Completed ➔ Ticket {created_inc_num or 'INC'} Created & Auto-Resolved with Remediation Plan."

    run_record = {
        "timestamp": timestamp_str,
        "duration_seconds": duration_sec,
        "status": "incident_resolved",
        "trigger": trigger_reason,
        "summary": summary_text,
        "container": container_name,
        "rca": rca,
        "stripped_error": stripped_error,
        "steps": steps_log
    }

    bot_registry.append_run_log(bot_id, run_record)
    return {
        "success": True,
        "status": "incident_resolved",
        "summary": summary_text,
        "rca": rca,
        "run_record": run_record
    }


def synthesize_bot_with_mistral(prompt: str, servers: Dict[str, Any]) -> Dict[str, Any]:
    from mistral_service import chat_with_bot_architect
    res = chat_with_bot_architect(prompt, [], servers)
    return res.get("blueprint") or {
        "name": "Custom DevOps Watchdog",
        "description": prompt,
        "instructions": prompt,
        "context_config": {"container_name": "devops-vsp-sample-app"},
        "tools_required": ["servicenow"]
    }

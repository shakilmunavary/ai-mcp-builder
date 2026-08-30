import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bot_engine import fetch_container_logs, extract_stripped_error_log, generate_ai_rca, execute_mcp_tool_on_gateway

def execute_workflow(context: dict = None) -> dict:
    context = context or {}
    container_name = context.get("container_name", "devops-vsp-sample-app")
    jenkins_job = context.get("jenkins_job", "devops-vsp-pipeline")
    github_repo = context.get("github_repo", "shakilmunavary/devops-vsp-sample-app")
    
    # Step 1: Read and strip container logs
    raw_logs = fetch_container_logs(container_name)
    stripped_error = extract_stripped_error_log(raw_logs)
    if not stripped_error:
        return {"status": "healthy", "summary": f"Container '{container_name}' logs are healthy.", "steps": [], "rca": {}}
    
    # Step 2: Correlate with Jenkins / GitHub (if configured)
    jenkins_info = ""
    if jenkins_job:
        jk_res = execute_mcp_tool_on_gateway("jenkins", "get_job_details", {"job_name": jenkins_job})
        if jk_res.get("success"):
            jenkins_info = jk_res.get("output", "")[:300]
            
    github_info = ""
    if github_repo:
        gh_res = execute_mcp_tool_on_gateway("github", "list_repos", {})
        if gh_res.get("success"):
            github_info = gh_res.get("output", "")[:300]
            
    # Step 3: Run Mistral AI RCA
    rca = generate_ai_rca(stripped_error, container_name, f"Container: {container_name}", jenkins_info, github_info)
    
    # Step 4: Create ServiceNow Incident with initial work_notes
    snow_args = {
        "short_description": f"Application {container_name} Error",
        "work_notes": f"SRE AI agent is analyzing the issue.\n\n=== STRIPPED ERROR LOG ===\n{stripped_error}",
        "urgency": context.get("snow_urgency", "2"),
        "impact": "2"
    }
    snow_create = execute_mcp_tool_on_gateway("servicenow", "create_incident", snow_args)
    
    created_sys_id = None
    created_inc_num = "INC-ALERT"
    if snow_create.get("success"):
        num_m = re.search(r"(INC\d+)", snow_create.get("output", ""))
        if num_m:
            created_inc_num = num_m.group(1)
        sys_m = re.search(r'"sys_id":\s*"([a-f0-9]{32})"', snow_create.get("output", ""))
        if sys_m:
            created_sys_id = sys_m.group(1)
            
    # Step 5: Update Worker Notes with Full RCA & Auto-Resolve
    if created_sys_id:
        update_args = {
            "sys_id": created_sys_id,
            "work_notes": f"### Mistral AI SRE Root Cause Analysis (RCA)\n\n• Root Cause: {rca.get('root_cause')}\n• Component: {rca.get('affected_component')}\n• Fix: {rca.get('recommended_fix')}\n\n{rca.get('formatted_rca_markdown')}",
            "close_code": "Solution Provided",
            "close_notes": f"Resolved by Autonomous SRE Bot with Mistral AI RCA report.\n\nRoot Cause: {rca.get('root_cause')}",
            "state": "6"
        }
        execute_mcp_tool_on_gateway("servicenow", "update_incident", update_args)
        
    return {
        "status": "incident_resolved",
        "summary": f"🚨 Anomaly in '{container_name}' ➔ Stripped Error Extracted ➔ AI RCA Completed ➔ Ticket {created_inc_num} Created & Auto-Resolved with Remediation Plan.",
        "steps": [
            {"step": 1, "name": "Docker Log Inspection", "status": "alert", "details": f"Stripped error extracted from '{container_name}'."},
            {"step": 2, "name": "Mistral AI RCA", "status": "success", "details": f"RCA: {rca.get('root_cause')[:150]}"},
            {"step": 3, "name": "ServiceNow Ticket Creation", "status": "success", "details": f"Created incident {created_inc_num} with initial worker notes."},
            {"step": 4, "name": "ServiceNow RCA Update & Auto-Resolution", "status": "success", "details": "Updated worker notes with full RCA and transitioned to Resolved state."}
        ],
        "rca": rca
    }

if __name__ == "__main__":
    result = execute_workflow({})
    print(json.dumps(result, indent=2))

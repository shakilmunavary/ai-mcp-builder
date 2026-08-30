"""
Autonomous Bot: Docker Log Monitor with AI RCA
Category: SRE & Incident Automation
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot_engine import run_bot_workflow

if __name__ == "__main__":
    result = run_bot_workflow("docker_log_monitor_snow_incident", trigger_reason="CLI Direct Invocation")
    print(f"Workflow status: {result.get('status')}")

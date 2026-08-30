"""
Autonomous Bot: Java Container SRE Watchdog
Category: SRE & Incident Automation
Instructions: 1. Monitor container 'devops-vsp-sample-app' logs for 'ERROR' or exceptions
2. Verify deduplication against active open ServiceNow incidents
3. Perform Mistral AI RCA from error snippet
4. Create ServiceNow ticket and update with RCA findings
5. Auto-resolve/close the ticket
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot_engine import run_bot_workflow

if __name__ == "__main__":
    result = run_bot_workflow("java_container_sre_watchdog", trigger_reason="CLI Direct Invocation")
    print(f"Workflow status: {result.get('status')}")

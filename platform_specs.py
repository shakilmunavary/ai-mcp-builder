"""
Platform Specifications Registry (Exhaustive Enterprise Suites with Deterministic Baselines)
"""

from typing import Dict, Any, List

GITHUB_ENTERPRISE_TOOLS = [
    {"name": "list_repos", "category": "Query", "description": "List repositories for configured org/user with visibility, forks, and stars.", "params": {"limit": "integer (default: 15)", "org": "string (optional)"}, "sample_args": {"limit": 10}, "example_call": "list_repos(limit=10)"},
    {"name": "get_repo_details", "category": "Query", "description": "Get detailed metadata for a repository (stars, forks, open issues count, default branch, language).", "params": {"repo": "string (required)"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "get_repo_details(repo='enterprise-backend')"},
    {"name": "create_repo", "category": "Action", "description": "Create a new repository in configured organization or user account.", "params": {"name": "string (required)", "private": "boolean", "description": "string"}, "sample_args": {"name": "microservice-auth", "private": True}, "example_call": "create_repo(name='microservice-auth', private=True)"},
    {"name": "fork_repo", "category": "Action", "description": "Fork a repository into your user or target organization.", "params": {"owner": "string", "repo": "string"}, "sample_args": {"owner": "octocat", "repo": "Spoon-Knife"}, "example_call": "fork_repo(owner='octocat', repo='Spoon-Knife')"},
    {"name": "delete_repo", "category": "Action", "description": "Delete a repository permanently.", "params": {"repo": "string"}, "sample_args": {"repo": "obsolete-test-repo"}, "example_call": "delete_repo(repo='obsolete-test-repo')"},
    {"name": "list_issues", "category": "Query", "description": "List repository issues filtered by state (open, closed), label, or assignee.", "params": {"repo": "string", "state": "string (open, closed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_issues(repo='enterprise-backend', state='open')"},
    {"name": "get_issue", "category": "Query", "description": "Get detailed issue author, labels, body, and status.", "params": {"repo": "string", "issue_number": "integer"}, "sample_args": {"repo": "enterprise-backend", "issue_number": 105}, "example_call": "get_issue(repo='enterprise-backend', issue_number=105)"},
    {"name": "create_issue", "category": "Action", "description": "Create a new issue with markdown body, assignees, and labels.", "params": {"repo": "string", "title": "string", "body": "string"}, "sample_args": {"repo": "enterprise-backend", "title": "Timeout", "body": "Observed 504 errors."}, "example_call": "create_issue(repo='enterprise-backend', title='Timeout', body='...')"},
    {"name": "add_issue_comment", "category": "Action", "description": "Add a comment to an existing issue or pull request.", "params": {"repo": "string", "issue_number": "integer", "comment_body": "string"}, "sample_args": {"repo": "enterprise-backend", "issue_number": 105, "comment_body": "Investigating connection pool limits."}, "example_call": "add_issue_comment(repo='enterprise-backend', issue_number=105, comment_body='...')"},
    {"name": "list_pull_requests", "category": "Query", "description": "List pull requests in a repository filtered by state and base branch.", "params": {"repo": "string", "state": "string (open, closed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_pull_requests(repo='enterprise-backend', state='open')"},
    {"name": "get_pr_status", "category": "Query", "description": "Get detailed PR status, CI checks, review approvals, and mergeability.", "params": {"repo": "string", "pr_number": "integer"}, "sample_args": {"repo": "enterprise-backend", "pr_number": 42}, "example_call": "get_pr_status(repo='enterprise-backend', pr_number=42)"},
    {"name": "create_pull_request", "category": "Action", "description": "Create a new PR between head and base branches.", "params": {"repo": "string", "title": "string", "head": "string", "base": "string"}, "sample_args": {"repo": "enterprise-backend", "title": "feat", "head": "feature/cache", "base": "main"}, "example_call": "create_pull_request(repo='enterprise-backend', title='feat', head='feat/cache', base='main')"},
    {"name": "merge_pull_request", "category": "Action", "description": "Merge PR using merge, squash, or rebase strategy.", "params": {"repo": "string", "pr_number": "integer", "merge_method": "string (squash, merge, rebase)"}, "sample_args": {"repo": "enterprise-backend", "pr_number": 42, "merge_method": "squash"}, "example_call": "merge_pull_request(repo='enterprise-backend', pr_number=42, merge_method='squash')"},
    {"name": "list_workflows", "category": "Query", "description": "List all GitHub Actions workflow YAML pipelines configured in a repo.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_workflows(repo='enterprise-backend')"},
    {"name": "trigger_workflow_dispatch", "category": "Action", "description": "Trigger a GitHub Actions workflow manually with branch ref and inputs.", "params": {"repo": "string", "workflow_id": "string", "ref": "string", "inputs": "object"}, "sample_args": {"repo": "enterprise-backend", "workflow_id": "deploy.yml", "ref": "main"}, "example_call": "trigger_workflow_dispatch(repo='enterprise-backend', workflow_id='deploy.yml', ref='main')"},
    {"name": "list_dependabot_alerts", "category": "Audit & Security", "description": "List open Dependabot dependency vulnerability alerts in a repository.", "params": {"repo": "string", "state": "string (open, fixed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_dependabot_alerts(repo='enterprise-backend', state='open')"},
    {"name": "list_code_scanning_alerts", "category": "Audit & Security", "description": "List CodeQL static analysis security alerts and severity levels.", "params": {"repo": "string", "state": "string (open, fixed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_code_scanning_alerts(repo='enterprise-backend', state='open')"},
    {"name": "list_secret_scanning_alerts", "category": "Audit & Security", "description": "List detected leaked tokens and secret scanning alerts.", "params": {"repo": "string", "state": "string (open, resolved)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_secret_scanning_alerts(repo='enterprise-backend', state='open')"},
    {"name": "list_environments", "category": "Query", "description": "List deployment environments (e.g. production, staging) and protection rules.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_environments(repo='enterprise-backend')"},
    {"name": "create_deployment", "category": "Action", "description": "Create a GitHub Deployment tracking deployment events.", "params": {"repo": "string", "ref": "string", "environment": "string"}, "sample_args": {"repo": "enterprise-backend", "ref": "main", "environment": "production"}, "example_call": "create_deployment(repo='enterprise-backend', ref='main', environment='production')"},
    {"name": "list_collaborators", "category": "Admin", "description": "List users and teams with access permissions to a repository.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_collaborators(repo='enterprise-backend')"},
    {"name": "list_branches", "category": "Query", "description": "List repository branches, protected status, and latest commit SHAs.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_branches(repo='enterprise-backend')"},
    {"name": "list_releases", "category": "Query", "description": "List published GitHub releases, tag names, assets, and changelogs.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_releases(repo='enterprise-backend')"},
    {"name": "search_code", "category": "Query", "description": "Search code strings, functions, or patterns across organization repositories.", "params": {"query": "string"}, "sample_args": {"query": "def calculate_metrics in:file"}, "example_call": "search_code(query='def calculate_metrics')"},
    {"name": "search_repositories", "category": "Query", "description": "Search repositories by keyword, language, or stars.", "params": {"query": "string"}, "sample_args": {"query": "microservice language:python"}, "example_call": "search_repositories(query='microservice language:python')"}
]

AWS_S3_TOOLS = [
    {"name": "list_buckets", "category": "Query", "description": "List all S3 storage buckets in account with creation dates and owner.", "params": {}, "sample_args": {}, "example_call": "list_buckets()"},
    {"name": "get_bucket_location", "category": "Query", "description": "Get the AWS region/location constraint for a specific S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_location(bucket='prod-data-lake')"},
    {"name": "list_objects_v2", "category": "Query", "description": "List objects, keys, file sizes, and storage class in an S3 bucket or sub-folder prefix.", "params": {"bucket": "string (required)", "prefix": "string (optional)", "max_keys": "integer (default: 50)"}, "sample_args": {"bucket": "prod-data-lake", "prefix": "backups/2026/"}, "example_call": "list_objects_v2(bucket='prod-data-lake', prefix='backups/')"},
    {"name": "get_object_metadata", "category": "Query", "description": "Retrieve HTTP headers, content-type, content-length, and ETag checksum for an S3 object.", "params": {"bucket": "string (required)", "key": "string (required)"}, "sample_args": {"bucket": "prod-data-lake", "key": "reports/q3_summary.pdf"}, "example_call": "get_object_metadata(bucket='prod-data-lake', key='reports/q3.pdf')"},
    {"name": "download_object", "category": "Query", "description": "Download or retrieve text/data contents of an object from S3.", "params": {"bucket": "string (required)", "key": "string (required)"}, "sample_args": {"bucket": "prod-data-lake", "key": "config.json"}, "example_call": "download_object(bucket='prod-data-lake', key='config.json')"},
    {"name": "upload_object", "category": "Action", "description": "Upload a file or string payload into an S3 bucket at a specified key.", "params": {"bucket": "string (required)", "key": "string (required)", "body": "string or base64 (required)", "content_type": "string"}, "sample_args": {"bucket": "prod-data-lake", "key": "logs/app.log", "body": "log data..."}, "example_call": "upload_object(bucket='prod-data-lake', key='logs/app.log', body='...')"},
    {"name": "delete_object", "category": "Action", "description": "Permanently delete an object key from an S3 bucket.", "params": {"bucket": "string (required)", "key": "string (required)"}, "sample_args": {"bucket": "prod-data-lake", "key": "temp/test.tmp"}, "example_call": "delete_object(bucket='prod-data-lake', key='temp/test.tmp')"},
    {"name": "delete_objects_batch", "category": "Action", "description": "Delete multiple S3 objects in a single batch request.", "params": {"bucket": "string (required)", "keys": "array of strings"}, "sample_args": {"bucket": "prod-data-lake", "keys": ["temp/1.tmp", "temp/2.tmp"]}, "example_call": "delete_objects_batch(bucket='prod-data-lake', keys=['1.tmp'])"},
    {"name": "generate_presigned_url", "category": "Action", "description": "Generate a time-limited pre-signed URL for temporary secure download or upload.", "params": {"bucket": "string (required)", "key": "string (required)", "expires_in_seconds": "integer (default: 3600)"}, "sample_args": {"bucket": "prod-data-lake", "key": "data.csv", "expires_in_seconds": 1800}, "example_call": "generate_presigned_url(bucket='prod-data-lake', key='data.csv')"},
    {"name": "get_bucket_policy", "category": "Admin", "description": "Retrieve the JSON IAM access policy attached to an S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_policy(bucket='prod-data-lake')"},
    {"name": "get_bucket_cors", "category": "Admin", "description": "Retrieve Cross-Origin Resource Sharing (CORS) rules for an S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_cors(bucket='prod-data-lake')"},
    {"name": "get_bucket_encryption", "category": "Admin", "description": "Get server-side encryption (SSE-S3 / SSE-KMS) configuration for a bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_encryption(bucket='prod-data-lake')"},
    {"name": "get_bucket_lifecycle", "category": "Admin", "description": "Get lifecycle transitions and expiration rules (e.g. Glacier archiving) for a bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_lifecycle(bucket='prod-data-lake')"},
    {"name": "get_bucket_tagging", "category": "Admin", "description": "List cost-allocation and environment tags assigned to an S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_tagging(bucket='prod-data-lake')"},
    {"name": "create_bucket", "category": "Action", "description": "Create a new S3 bucket in the configured AWS region.", "params": {"bucket": "string (required)", "region": "string (optional)"}, "sample_args": {"bucket": "new-microservice-assets"}, "example_call": "create_bucket(bucket='new-microservice-assets')"},
    {"name": "delete_bucket", "category": "Action", "description": "Delete an empty S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "old-temp-bucket"}, "example_call": "delete_bucket(bucket='old-temp-bucket')"}
]

SERVICENOW_SNOW_TOOLS = [
    {"name": "list_incidents", "category": "Query", "description": "List ServiceNow Incidents filtered by state, priority, assignment group, or assigned user.", "params": {"state": "string (optional: 1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed)", "limit": "integer (default: 20)"}, "sample_args": {"state": "2", "limit": 10}, "example_call": "list_incidents(state='2', limit=10)"},
    {"name": "get_incident", "category": "Query", "description": "Retrieve full incident details, caller, SLA timeline, assigned group, and resolution notes by number or sys_id.", "params": {"incident_number": "string (e.g. INC0010023)"}, "sample_args": {"incident_number": "INC0010023"}, "example_call": "get_incident(incident_number='INC0010023')"},
    {"name": "create_incident", "category": "Action", "description": "Create a new Incident ticket in ServiceNow with priority, caller, category, and short description.", "params": {"short_description": "string (required)", "urgency": "string (1=High, 2=Medium, 3=Low)", "impact": "string (1=High, 2=Medium, 3=Low)", "caller_id": "string (optional)", "category": "string (software, hardware, network)"}, "sample_args": {"short_description": "Payment Gateway Timeout", "urgency": "1", "impact": "1", "category": "software"}, "example_call": "create_incident(short_description='Payment Gateway Timeout', urgency='1')"},
    {"name": "update_incident", "category": "Action", "description": "Update incident state, assigned user/group, priority, or resolution details.", "params": {"incident_number": "string (required)", "state": "string (2=In Progress, 3=On Hold, 6=Resolved, 7=Closed)", "assigned_to": "string", "work_notes": "string"}, "sample_args": {"incident_number": "INC0010023", "state": "2", "work_notes": "Investigating load balancer logs."}, "example_call": "update_incident(incident_number='INC0010023', state='2')"},
    {"name": "add_work_note", "category": "Action", "description": "Add an internal work note or customer-visible comment to an incident.", "params": {"incident_number": "string (required)", "note": "string (required)", "is_customer_visible": "boolean (default: false)"}, "sample_args": {"incident_number": "INC0010023", "note": "Root cause identified as DNS propagation delay."}, "example_call": "add_work_note(incident_number='INC0010023', note='...')"},
    {"name": "close_incident", "category": "Action", "description": "Resolve and close an incident with resolution code and resolution notes.", "params": {"incident_number": "string (required)", "close_code": "string", "close_notes": "string (required)"}, "sample_args": {"incident_number": "INC0010023", "close_code": "Solved", "close_notes": "Restarted service and verified 200 OK."}, "example_call": "close_incident(incident_number='INC0010023', close_code='Solved')"},
    {"name": "reopen_incident", "category": "Action", "description": "Reopen a previously resolved incident if the problem reoccurs.", "params": {"incident_number": "string (required)", "reason": "string (required)"}, "sample_args": {"incident_number": "INC0010023", "reason": "Intermittent timeouts detected again."}, "example_call": "reopen_incident(incident_number='INC0010023', reason='...')"},
    {"name": "list_change_requests", "category": "Query", "description": "List Change Requests filtered by phase, type, or assignment group.", "params": {"type": "string (normal, standard, emergency)", "limit": "integer (default: 20)"}, "sample_args": {"type": "normal", "limit": 10}, "example_call": "list_change_requests(type='normal')"},
    {"name": "get_change_request", "category": "Query", "description": "Retrieve Change Request status, CAB approval state, schedule, and phase.", "params": {"change_number": "string (e.g. CHG0030012)"}, "sample_args": {"change_number": "CHG0030012"}, "example_call": "get_change_request(change_number='CHG0030012')"},
    {"name": "create_change_request", "category": "Action", "description": "Create a Change Request (Normal, Standard, Emergency) with implementation plan, backout plan, and risk level.", "params": {"type": "string (normal, standard, emergency)", "short_description": "string", "description": "string", "risk": "string"}, "sample_args": {"type": "normal", "short_description": "Deploy v2.4.0 to Production", "risk": "2"}, "example_call": "create_change_request(type='normal', short_description='Deploy v2.4.0')"},
    {"name": "update_change_phase", "category": "Action", "description": "Advance change request workflow state (e.g. Assess, Authorize, Scheduled, Implement, Review, Closed).", "params": {"change_number": "string (required)", "phase": "string (implement, review, closed)"}, "sample_args": {"change_number": "CHG0030012", "phase": "implement"}, "example_call": "update_change_phase(change_number='CHG0030012', phase='implement')"},
    {"name": "list_problems", "category": "Query", "description": "List known Problem tickets, root cause records, and associated incidents.", "params": {"limit": "integer"}, "sample_args": {"limit": 10}, "example_call": "list_problems()"},
    {"name": "create_problem", "category": "Action", "description": "Create a Problem record to track root cause analysis across multiple incidents.", "params": {"short_description": "string (required)", "description": "string"}, "sample_args": {"short_description": "Root Cause: Redis Connection Pool Exhaustion"}, "example_call": "create_problem(short_description='Root Cause: Redis Pool')"},
    {"name": "get_problem_details", "category": "Query", "description": "Get problem details, associated incidents, root cause, and workaround description.", "params": {"problem_number": "string (e.g. PRB0040001)"}, "sample_args": {"problem_number": "PRB0040001"}, "example_call": "get_problem_details(problem_number='PRB0040001')"},
    {"name": "query_cmdb_ci", "category": "Query", "description": "Query CMDB Configuration Items (servers, databases, network gear, microservices) by class or name.", "params": {"ci_class": "string", "query": "string"}, "sample_args": {"ci_class": "cmdb_ci_server", "query": "operational_status=1"}, "example_call": "query_cmdb_ci(ci_class='cmdb_ci_server')"},
    {"name": "get_ci_details", "category": "Query", "description": "Retrieve detailed attributes, IP addresses, OS version, and relationship dependencies for a CI.", "params": {"ci_sys_id": "string"}, "sample_args": {"ci_sys_id": "prod-app-server-01"}, "example_call": "get_ci_details(ci_sys_id='prod-app-server-01')"},
    {"name": "list_catalog_items", "category": "Query", "description": "List available Service Catalog orderable items and request forms.", "params": {}, "sample_args": {}, "example_call": "list_catalog_items()"},
    {"name": "submit_catalog_request", "category": "Action", "description": "Order a Service Catalog item with required request parameters.", "params": {"item_sys_id": "string", "variables": "object"}, "sample_args": {"item_sys_id": "item_12345"}, "example_call": "submit_catalog_request(item_sys_id='item_12345')"},
    {"name": "search_knowledge_base", "category": "Query", "description": "Search published articles, troubleshooting runbooks, and FAQs in ServiceNow Knowledge Base.", "params": {"query": "string (required)"}, "sample_args": {"query": "VPN troubleshooting"}, "example_call": "search_knowledge_base(query='VPN troubleshooting')"},
    {"name": "query_table_api", "category": "Admin", "description": "Execute dynamic JSON query against ANY ServiceNow table with filters and field selection.", "params": {"table_name": "string", "sysparm_query": "string"}, "sample_args": {"table_name": "sys_user_group", "sysparm_query": "active=true"}, "example_call": "query_table_api(table_name='sys_user_group')"}
]

JENKINS_TOOLS = [
    {"name": "list_jobs", "category": "Query", "description": "List all Jenkins jobs, multibranch pipelines, and folders with health status.", "params": {}, "sample_args": {}, "example_call": "list_jobs()"},
    {"name": "get_job_details", "category": "Query", "description": "Retrieve full configuration, parameters, and build history for a job.", "params": {"job_name": "string (required)"}, "sample_args": {"job_name": "backend-ci"}, "example_call": "get_job_details(job_name='backend-ci')"},
    {"name": "build_job", "category": "Action", "description": "Trigger a build for a standard or parameterized Jenkins job.", "params": {"job_name": "string (required)", "parameters": "object (optional key-value params)"}, "sample_args": {"job_name": "backend-ci", "parameters": {"BRANCH": "main"}}, "example_call": "build_job(job_name='backend-ci')"},
    {"name": "get_build_status", "category": "Query", "description": "Check status (SUCCESS, UNSTABLE, FAILURE, BUILDING) and duration of a build.", "params": {"job_name": "string", "build_number": "integer or 'lastBuild'"}, "sample_args": {"job_name": "backend-ci", "build_number": 42}, "example_call": "get_build_status(job_name='backend-ci', build_number=42)"},
    {"name": "get_build_console_output", "category": "Monitoring", "description": "Retrieve terminal log and console text for a specific build run.", "params": {"job_name": "string", "build_number": "integer", "tail_lines": "integer (default: 100)"}, "sample_args": {"job_name": "backend-ci", "build_number": 42, "tail_lines": 50}, "example_call": "get_build_console_output(job_name='backend-ci', build_number=42)"},
    {"name": "stop_build", "category": "Action", "description": "Abort or cancel an actively running build execution.", "params": {"job_name": "string", "build_number": "integer"}, "sample_args": {"job_name": "backend-ci", "build_number": 42}, "example_call": "stop_build(job_name='backend-ci', build_number=42)"},
    {"name": "get_pipeline_stages", "category": "Monitoring", "description": "Get visual pipeline stage breakdown, step timings, and individual stage outcomes.", "params": {"job_name": "string", "build_number": "integer"}, "sample_args": {"job_name": "backend-ci", "build_number": 42}, "example_call": "get_pipeline_stages(job_name='backend-ci', build_number=42)"},
    {"name": "get_build_queue", "category": "Monitoring", "description": "List queued jobs currently waiting for available build executors.", "params": {}, "sample_args": {}, "example_call": "get_build_queue()"},
    {"name": "cancel_queue_item", "category": "Action", "description": "Remove a pending build request from the build queue.", "params": {"queue_id": "integer"}, "sample_args": {"queue_id": 102}, "example_call": "cancel_queue_item(queue_id=102)"},
    {"name": "list_nodes", "category": "Admin", "description": "List Jenkins controller and build agents with online status and disk space.", "params": {}, "sample_args": {}, "example_call": "list_nodes()"},
    {"name": "get_node_status", "category": "Admin", "description": "Get detailed resource utilization and executor availability for a build node.", "params": {"node_name": "string"}, "sample_args": {"node_name": "docker-builder-01"}, "example_call": "get_node_status(node_name='docker-builder-01')"},
    {"name": "toggle_node_offline", "category": "Admin", "description": "Take a node offline for maintenance or bring it back online.", "params": {"node_name": "string", "offline": "boolean", "reason": "string"}, "sample_args": {"node_name": "agent-1", "offline": True, "reason": "Upgrading Docker"}, "example_call": "toggle_node_offline(node_name='agent-1', offline=True)"},
    {"name": "get_system_info", "category": "Admin", "description": "Check Jenkins controller version, uptime, and system health status.", "params": {}, "sample_args": {}, "example_call": "get_system_info()"},
    {"name": "list_plugins", "category": "Admin", "description": "List installed plugins, active versions, and pending updates.", "params": {}, "sample_args": {}, "example_call": "list_plugins()"},
    {"name": "create_job", "category": "Action", "description": "Create a new Jenkins job from XML configuration definition.", "params": {"job_name": "string", "config_xml": "string (XML string)"}, "sample_args": {"job_name": "new-pipeline", "config_xml": "<project>...</project>"}, "example_call": "create_job(job_name='new-pipeline', config_xml='...')"},
    {"name": "delete_job", "category": "Action", "description": "Delete a Jenkins job permanently.", "params": {"job_name": "string"}, "sample_args": {"job_name": "obsolete-job"}, "example_call": "delete_job(job_name='obsolete-job')"}
]

JIRA_TOOLS = [
    {"name": "create_issue", "category": "Action", "description": "Create a new Jira issue, task, bug, or story with summary, description, and issue type.", "params": {"project_key": "string", "summary": "string", "description": "string", "issue_type": "string (Task, Bug, Story, Epic)"}, "sample_args": {"project_key": "PROJ", "summary": "Fix auth error", "issue_type": "Bug"}, "example_call": "create_issue(project_key='PROJ', summary='Fix auth error')"},
    {"name": "get_issue", "category": "Query", "description": "Retrieve detailed issue metadata, status, assignee, priority, sprint, and comments.", "params": {"issue_key": "string (e.g. PROJ-101)"}, "sample_args": {"issue_key": "PROJ-101"}, "example_call": "get_issue(issue_key='PROJ-101')"},
    {"name": "update_issue", "category": "Action", "description": "Update Jira issue fields such as assignee, priority, description, or labels.", "params": {"issue_key": "string", "summary": "string", "assignee": "string", "priority": "string"}, "sample_args": {"issue_key": "PROJ-101", "priority": "High"}, "example_call": "update_issue(issue_key='PROJ-101', priority='High')"},
    {"name": "transition_issue", "category": "Action", "description": "Advance Jira issue workflow state (e.g. 'In Progress', 'In Review', 'Done').", "params": {"issue_key": "string", "transition_name": "string"}, "sample_args": {"issue_key": "PROJ-101", "transition_name": "In Progress"}, "example_call": "transition_issue(issue_key='PROJ-101', transition_name='In Progress')"},
    {"name": "add_comment", "category": "Action", "description": "Add a comment to an existing Jira ticket.", "params": {"issue_key": "string", "body": "string"}, "sample_args": {"issue_key": "PROJ-101", "body": "Patch deployed to staging for QA verification."}, "example_call": "add_comment(issue_key='PROJ-101', body='...')"},
    {"name": "search_issues_jql", "category": "Query", "description": "Search Jira issues using JQL (Jira Query Language).", "params": {"jql": "string", "limit": "integer (default: 25)"}, "sample_args": {"jql": "project = PROJ AND status = 'In Progress' ORDER BY updated DESC"}, "example_call": "search_issues_jql(jql='project = PROJ')"},
    {"name": "list_projects", "category": "Query", "description": "List all accessible Jira projects with keys, names, and project leads.", "params": {}, "sample_args": {}, "example_call": "list_projects()"},
    {"name": "get_project_details", "category": "Query", "description": "Get project metadata, issue types, components, and versions.", "params": {"project_key": "string"}, "sample_args": {"project_key": "PROJ"}, "example_call": "get_project_details(project_key='PROJ')"},
    {"name": "list_sprints", "category": "Query", "description": "List active and historical agile sprints in an agile board.", "params": {"board_id": "integer", "state": "string (active, closed, future)"}, "sample_args": {"board_id": 5, "state": "active"}, "example_call": "list_sprints(board_id=5, state='active')"},
    {"name": "assign_issue", "category": "Action", "description": "Assign an issue to a specific team member or set to Unassigned.", "params": {"issue_key": "string", "account_id": "string"}, "sample_args": {"issue_key": "PROJ-101", "account_id": "user_123"}, "example_call": "assign_issue(issue_key='PROJ-101', account_id='user_123')"}
]

KUBERNETES_TOOLS = [
    {"name": "list_pods", "category": "Query", "description": "List Kubernetes pods across all namespaces or a specific namespace with status and restart count.", "params": {"namespace": "string (default: 'default')"}, "sample_args": {"namespace": "production"}, "example_call": "list_pods(namespace='production')"},
    {"name": "get_pod_details", "category": "Query", "description": "Retrieve full YAML/JSON spec, conditions, container statuses, and IP for a pod.", "params": {"pod_name": "string", "namespace": "string"}, "sample_args": {"pod_name": "auth-svc-78f", "namespace": "production"}, "example_call": "get_pod_details(pod_name='auth-svc-78f', namespace='production')"},
    {"name": "get_pod_logs", "category": "Monitoring", "description": "Retrieve stdout/stderr logs from a specific pod and container.", "params": {"pod_name": "string", "namespace": "string", "tail_lines": "integer (default: 100)", "container": "string"}, "sample_args": {"pod_name": "auth-svc-78f", "namespace": "production", "tail_lines": 50}, "example_call": "get_pod_logs(pod_name='auth-svc-78f', namespace='production')"},
    {"name": "list_deployments", "category": "Query", "description": "List Deployments with desired vs ready replicas and image versions.", "params": {"namespace": "string"}, "sample_args": {"namespace": "production"}, "example_call": "list_deployments(namespace='production')"},
    {"name": "scale_deployment", "category": "Action", "description": "Scale replica count up or down for a Kubernetes deployment.", "params": {"deployment_name": "string", "namespace": "string", "replicas": "integer"}, "sample_args": {"deployment_name": "api-gateway", "namespace": "production", "replicas": 5}, "example_call": "scale_deployment(deployment_name='api-gateway', namespace='production', replicas=5)"},
    {"name": "restart_deployment", "category": "Action", "description": "Trigger rolling restart of a deployment by updating spec annotation.", "params": {"deployment_name": "string", "namespace": "string"}, "sample_args": {"deployment_name": "api-gateway", "namespace": "production"}, "example_call": "restart_deployment(deployment_name='api-gateway', namespace='production')"},
    {"name": "list_services", "category": "Query", "description": "List ClusterIP, NodePort, and LoadBalancer services and port mappings.", "params": {"namespace": "string"}, "sample_args": {"namespace": "production"}, "example_call": "list_services(namespace='production')"},
    {"name": "list_nodes", "category": "Admin", "description": "List Kubernetes cluster nodes, Ready conditions, CPU/Memory capacity, and roles.", "params": {}, "sample_args": {}, "example_call": "list_nodes()"},
    {"name": "get_cluster_events", "category": "Monitoring", "description": "List recent cluster warning events, OOMKilled alerts, and failed scheduling.", "params": {"namespace": "string"}, "sample_args": {"namespace": "production"}, "example_call": "get_cluster_events(namespace='production')"},
    {"name": "delete_pod", "category": "Action", "description": "Delete a pod to trigger eviction and restart by controller.", "params": {"pod_name": "string", "namespace": "string"}, "sample_args": {"pod_name": "stuck-pod-1", "namespace": "production"}, "example_call": "delete_pod(pod_name='stuck-pod-1', namespace='production')"}
]

PLATFORM_SPECS: Dict[str, Any] = {
    "servicenow": {
        "id": "servicenow",
        "aliases": ["snow", "service-now", "service now", "servicenow itsm", "service now itsm"],
        "name": "ServiceNow (SNOW)",
        "category": "ITSM & Enterprise Service Management",
        "description": "Comprehensive enterprise suite: Incidents, Change Requests, Problems, CMDB CIs, Service Catalog, Work Notes, User Roles, Knowledge Base, and Table APIs.",
        "icon": "layers",
        "fields": [
            {"key": "instance_url", "label": "ServiceNow Instance URL", "prompt": "Enter your ServiceNow instance URL (e.g. https://dev12345.service-now.com):", "placeholder": "https://devXXXXX.service-now.com", "default": "", "secret": False, "required": True},
            {"key": "username", "label": "Username / Integration Account", "prompt": "Enter your ServiceNow integration username:", "placeholder": "admin", "default": "", "secret": False, "required": True},
            {"key": "password", "label": "Password or API Token", "prompt": "Enter your ServiceNow password or API token:", "placeholder": "••••••••••••", "default": "", "secret": True, "required": True}
        ],
        "tools": SERVICENOW_SNOW_TOOLS
    },
    "aws_s3": {
        "id": "aws_s3",
        "aliases": ["s3", "aws s3", "amazon s3", "s3 alone", "s3 bucket", "s3 storage", "aws s3 alone"],
        "name": "AWS S3 Storage",
        "category": "Cloud Object Storage",
        "description": "Comprehensive 16-tool dedicated suite for AWS S3: Buckets, Objects, Pre-signed URLs, Policies, Versioning, Encryption, Lifecycle rules, and Bucket Tagging.",
        "icon": "database",
        "fields": [
            {"key": "aws_access_key_id", "label": "AWS Access Key ID", "prompt": "Enter AWS Access Key ID for S3:", "placeholder": "AKIAXXXXXXXXXXXXXXXX", "default": "", "secret": False, "required": True},
            {"key": "aws_secret_access_key", "label": "AWS Secret Access Key", "prompt": "Enter AWS Secret Access Key:", "placeholder": "••••••••••••••••••••••••••••••••", "default": "", "secret": True, "required": True},
            {"key": "aws_region", "label": "Default S3 Region", "prompt": "Default AWS Region for S3 (e.g. us-east-1, us-west-2):", "placeholder": "us-east-1", "default": "us-east-1", "secret": False, "required": True}
        ],
        "tools": AWS_S3_TOOLS
    },
    "github": {
        "id": "github",
        "aliases": ["gh", "github enterprise", "git hub", "github.com"],
        "name": "GitHub Enterprise",
        "category": "Source Control & DevOps",
        "description": "Massive 25-tool enterprise suite: Repos, Issues, PRs, Reviews, Actions CI/CD, Dependabot Alerts, Code Scanning, Secret Scanning, Deployments, Collaborators, and Global Search.",
        "icon": "github",
        "fields": [
            {"key": "base_url", "label": "Base API URL", "prompt": "What is the GitHub API base URL? (Default: https://api.github.com):", "placeholder": "https://api.github.com", "default": "https://api.github.com", "secret": False, "required": True},
            {"key": "org", "label": "Organization / Owner", "prompt": "What is your GitHub organization or owner account name?", "placeholder": "my-org or octocat", "default": "", "secret": False, "required": True},
            {"key": "token", "label": "Personal Access Token (PAT)", "prompt": "Please provide your GitHub Personal Access Token:", "placeholder": "ghp_xxxxxxxxxxxxxxxxxxxx", "default": "", "secret": True, "required": True}
        ],
        "tools": GITHUB_ENTERPRISE_TOOLS
    },
    "jenkins": {
        "id": "jenkins",
        "aliases": ["jenkins ci", "jenkins server", "localjenkins", "local jenkins"],
        "name": "Jenkins CI/CD",
        "category": "CI/CD & Automation",
        "description": "Complete 16-tool suite: Jobs, Builds, Parameterized triggers, Console Logs, Visual Pipeline Stages, Queue Management, Build Nodes, and Plugins.",
        "icon": "play-circle",
        "fields": [
            {"key": "jenkins_url", "label": "Jenkins Server URL", "prompt": "Enter Jenkins Server URL (e.g. http://localhost:8080):", "placeholder": "http://localhost:8080", "default": "http://localhost:8080", "secret": False, "required": True},
            {"key": "jenkins_username", "label": "Jenkins Username", "prompt": "Enter Jenkins username:", "placeholder": "admin", "default": "admin", "secret": False, "required": True},
            {"key": "jenkins_token", "label": "API Token / Password", "prompt": "Enter Jenkins API Token or Password:", "placeholder": "••••••••••••", "default": "", "secret": True, "required": True}
        ],
        "tools": JENKINS_TOOLS
    },
    "jira": {
        "id": "jira",
        "aliases": ["atlassian jira", "jira software", "jira cloud"],
        "name": "Jira Software",
        "category": "Project & Issue Tracking",
        "description": "Complete agile project management suite: Issues, JQL Queries, Workflow Transitions, Sprints, Epics, Comments, and Components.",
        "icon": "check-square",
        "fields": [
            {"key": "jira_url", "label": "Jira Domain URL", "prompt": "Enter Jira URL (e.g. https://yourcompany.atlassian.net):", "placeholder": "https://company.atlassian.net", "default": "", "secret": False, "required": True},
            {"key": "email", "label": "Atlassian Account Email", "prompt": "Enter your Jira user email:", "placeholder": "engineer@company.com", "default": "", "secret": False, "required": True},
            {"key": "api_token", "label": "Atlassian API Token", "prompt": "Enter Jira API Token:", "placeholder": "••••••••••••", "default": "", "secret": True, "required": True}
        ],
        "tools": JIRA_TOOLS
    },
    "kubernetes": {
        "id": "kubernetes",
        "aliases": ["k8s", "kube", "kubernetes cluster"],
        "name": "Kubernetes Cluster",
        "category": "Container Orchestration",
        "description": "Enterprise K8s suite: Pods, Deployments, Services, Rolling Restarts, Scaling, Node Status, Logs, and Cluster Warning Events.",
        "icon": "box",
        "fields": [
            {"key": "api_server_url", "label": "Kubernetes API Server URL", "prompt": "Enter K8s API Server URL (e.g. https://10.0.0.1:6443):", "placeholder": "https://10.0.0.1:6443", "default": "", "secret": False, "required": True},
            {"key": "service_account_token", "label": "Bearer Service Account Token", "prompt": "Enter K8s Service Account Bearer Token:", "placeholder": "••••••••••••", "default": "", "secret": True, "required": True}
        ],
        "tools": KUBERNETES_TOOLS
    }
}


def find_platform_by_query(query: str) -> Any:
    q = query.lower().strip()

    # 1. First check specific sub-service keywords (e.g. s3, snow, jenkins, k8s)
    if "s3" in q:
        return PLATFORM_SPECS["aws_s3"]
    if "snow" in q or "servicenow" in q or "service now" in q:
        return PLATFORM_SPECS["servicenow"]
    if "jenkins" in q:
        return PLATFORM_SPECS["jenkins"]
    if "jira" in q:
        return PLATFORM_SPECS["jira"]
    if "k8s" in q or "kubernetes" in q:
        return PLATFORM_SPECS["kubernetes"]
    if "github" in q or "git hub" in q:
        return PLATFORM_SPECS["github"]

    # 2. Direct ID Match
    if q in PLATFORM_SPECS:
        return PLATFORM_SPECS[q]
    
    # 3. Aliases Match
    for pid, spec in PLATFORM_SPECS.items():
        if q == pid or q == spec["name"].lower():
            return spec
        for a in spec.get("aliases", []):
            if a == q or a in q:
                return spec
        if pid in q or spec["name"].lower() in q:
            return spec
    return None


def get_platform_spec(platform_id: str) -> Dict[str, Any]:
    return PLATFORM_SPECS.get(platform_id.lower())


def get_all_platforms() -> List[Dict[str, Any]]:
    return list(PLATFORM_SPECS.values())

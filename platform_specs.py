"""
Platform Specifications Registry (Exhaustive Enterprise Suites with Sub-Service Scoping)
"""

from typing import Dict, Any, List

GITHUB_ENTERPRISE_TOOLS = [
    {"name": "list_repos", "description": "List repositories for configured org/user with visibility, forks, and stars.", "params": {"limit": "integer (default: 15)", "org": "string (optional)"}, "sample_args": {"limit": 10}, "example_call": "list_repos(limit=10)"},
    {"name": "get_repo_details", "description": "Get detailed metadata for a repository (stars, forks, open issues count, default branch, language).", "params": {"repo": "string (required)"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "get_repo_details(repo='enterprise-backend')"},
    {"name": "create_repo", "description": "Create a new repository in configured organization or user account.", "params": {"name": "string (required)", "private": "boolean", "description": "string"}, "sample_args": {"name": "microservice-auth", "private": True}, "example_call": "create_repo(name='microservice-auth', private=True)"},
    {"name": "fork_repo", "description": "Fork a repository into your user or target organization.", "params": {"owner": "string", "repo": "string"}, "sample_args": {"owner": "octocat", "repo": "Spoon-Knife"}, "example_call": "fork_repo(owner='octocat', repo='Spoon-Knife')"},
    {"name": "delete_repo", "description": "Delete a repository permanently.", "params": {"repo": "string"}, "sample_args": {"repo": "obsolete-test-repo"}, "example_call": "delete_repo(repo='obsolete-test-repo')"},
    {"name": "list_issues", "description": "List repository issues filtered by state (open, closed), label, or assignee.", "params": {"repo": "string", "state": "string (open, closed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_issues(repo='enterprise-backend', state='open')"},
    {"name": "get_issue", "description": "Get detailed issue author, labels, body, and status.", "params": {"repo": "string", "issue_number": "integer"}, "sample_args": {"repo": "enterprise-backend", "issue_number": 105}, "example_call": "get_issue(repo='enterprise-backend', issue_number=105)"},
    {"name": "create_issue", "description": "Create a new issue with markdown body, assignees, and labels.", "params": {"repo": "string", "title": "string", "body": "string"}, "sample_args": {"repo": "enterprise-backend", "title": "Timeout", "body": "Observed 504 errors."}, "example_call": "create_issue(repo='enterprise-backend', title='Timeout', body='...')"},
    {"name": "add_issue_comment", "description": "Add a comment to an existing issue or pull request.", "params": {"repo": "string", "issue_number": "integer", "comment_body": "string"}, "sample_args": {"repo": "enterprise-backend", "issue_number": 105, "comment_body": "Investigating connection pool limits."}, "example_call": "add_issue_comment(repo='enterprise-backend', issue_number=105, comment_body='...')"},
    {"name": "list_pull_requests", "description": "List pull requests in a repository filtered by state and base branch.", "params": {"repo": "string", "state": "string (open, closed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_pull_requests(repo='enterprise-backend', state='open')"},
    {"name": "get_pr_status", "description": "Get detailed PR status, CI checks, review approvals, and mergeability.", "params": {"repo": "string", "pr_number": "integer"}, "sample_args": {"repo": "enterprise-backend", "pr_number": 42}, "example_call": "get_pr_status(repo='enterprise-backend', pr_number=42)"},
    {"name": "create_pull_request", "description": "Create a new PR between head and base branches.", "params": {"repo": "string", "title": "string", "head": "string", "base": "string"}, "sample_args": {"repo": "enterprise-backend", "title": "feat", "head": "feature/cache", "base": "main"}, "example_call": "create_pull_request(repo='enterprise-backend', title='feat', head='feat/cache', base='main')"},
    {"name": "merge_pull_request", "description": "Merge PR using merge, squash, or rebase strategy.", "params": {"repo": "string", "pr_number": "integer", "merge_method": "string (squash, merge, rebase)"}, "sample_args": {"repo": "enterprise-backend", "pr_number": 42, "merge_method": "squash"}, "example_call": "merge_pull_request(repo='enterprise-backend', pr_number=42, merge_method='squash')"},
    {"name": "list_workflows", "description": "List all GitHub Actions workflow YAML pipelines configured in a repo.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_workflows(repo='enterprise-backend')"},
    {"name": "trigger_workflow_dispatch", "description": "Trigger a GitHub Actions workflow manually with branch ref and inputs.", "params": {"repo": "string", "workflow_id": "string", "ref": "string", "inputs": "object"}, "sample_args": {"repo": "enterprise-backend", "workflow_id": "deploy.yml", "ref": "main"}, "example_call": "trigger_workflow_dispatch(repo='enterprise-backend', workflow_id='deploy.yml', ref='main')"},
    {"name": "list_dependabot_alerts", "description": "List open Dependabot dependency vulnerability alerts in a repository.", "params": {"repo": "string", "state": "string (open, fixed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_dependabot_alerts(repo='enterprise-backend', state='open')"},
    {"name": "list_code_scanning_alerts", "description": "List CodeQL static analysis security alerts and severity levels.", "params": {"repo": "string", "state": "string (open, fixed)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_code_scanning_alerts(repo='enterprise-backend', state='open')"},
    {"name": "list_secret_scanning_alerts", "description": "List detected leaked tokens and secret scanning alerts.", "params": {"repo": "string", "state": "string (open, resolved)"}, "sample_args": {"repo": "enterprise-backend", "state": "open"}, "example_call": "list_secret_scanning_alerts(repo='enterprise-backend', state='open')"},
    {"name": "list_environments", "description": "List deployment environments (e.g. production, staging) and protection rules.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_environments(repo='enterprise-backend')"},
    {"name": "create_deployment", "description": "Create a GitHub Deployment tracking deployment events.", "params": {"repo": "string", "ref": "string", "environment": "string"}, "sample_args": {"repo": "enterprise-backend", "ref": "main", "environment": "production"}, "example_call": "create_deployment(repo='enterprise-backend', ref='main', environment='production')"},
    {"name": "list_collaborators", "description": "List users and teams with access permissions to a repository.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_collaborators(repo='enterprise-backend')"},
    {"name": "list_branches", "description": "List repository branches, protected status, and latest commit SHAs.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_branches(repo='enterprise-backend')"},
    {"name": "list_releases", "description": "List published GitHub releases, tag names, assets, and changelogs.", "params": {"repo": "string"}, "sample_args": {"repo": "enterprise-backend"}, "example_call": "list_releases(repo='enterprise-backend')"},
    {"name": "search_code", "description": "Search code strings, functions, or patterns across organization repositories.", "params": {"query": "string"}, "sample_args": {"query": "def calculate_metrics in:file"}, "example_call": "search_code(query='def calculate_metrics')"},
    {"name": "search_repositories", "description": "Search repositories by keyword, language, or stars.", "params": {"query": "string"}, "sample_args": {"query": "microservice language:python"}, "example_call": "search_repositories(query='microservice language:python')"}
]

AWS_S3_TOOLS = [
    {"name": "list_buckets", "description": "List all S3 storage buckets in account with creation dates and owner.", "params": {}, "sample_args": {}, "example_call": "list_buckets()"},
    {"name": "get_bucket_location", "description": "Get the AWS region/location constraint for a specific S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_location(bucket='prod-data-lake')"},
    {"name": "list_objects_v2", "description": "List objects, keys, file sizes, and storage class in an S3 bucket or sub-folder prefix.", "params": {"bucket": "string (required)", "prefix": "string (optional)", "max_keys": "integer (default: 50)"}, "sample_args": {"bucket": "prod-data-lake", "prefix": "backups/2026/"}, "example_call": "list_objects_v2(bucket='prod-data-lake', prefix='backups/')"},
    {"name": "get_object_metadata", "description": "Retrieve HTTP headers, content-type, content-length, and ETag checksum for an S3 object.", "params": {"bucket": "string (required)", "key": "string (required)"}, "sample_args": {"bucket": "prod-data-lake", "key": "reports/q3_summary.pdf"}, "example_call": "get_object_metadata(bucket='prod-data-lake', key='reports/q3.pdf')"},
    {"name": "download_object", "description": "Download or retrieve text/data contents of an object from S3.", "params": {"bucket": "string (required)", "key": "string (required)"}, "sample_args": {"bucket": "prod-data-lake", "key": "config.json"}, "example_call": "download_object(bucket='prod-data-lake', key='config.json')"},
    {"name": "upload_object", "description": "Upload a file or string payload into an S3 bucket at a specified key.", "params": {"bucket": "string (required)", "key": "string (required)", "body": "string or base64 (required)", "content_type": "string"}, "sample_args": {"bucket": "prod-data-lake", "key": "logs/app.log", "body": "log data..."}, "example_call": "upload_object(bucket='prod-data-lake', key='logs/app.log', body='...')"},
    {"name": "delete_object", "description": "Permanently delete an object key from an S3 bucket.", "params": {"bucket": "string (required)", "key": "string (required)"}, "sample_args": {"bucket": "prod-data-lake", "key": "temp/test.tmp"}, "example_call": "delete_object(bucket='prod-data-lake', key='temp/test.tmp')"},
    {"name": "delete_objects_batch", "description": "Delete multiple S3 objects in a single batch request.", "params": {"bucket": "string (required)", "keys": "array of strings"}, "sample_args": {"bucket": "prod-data-lake", "keys": ["temp/1.tmp", "temp/2.tmp"]}, "example_call": "delete_objects_batch(bucket='prod-data-lake', keys=['1.tmp'])"},
    {"name": "generate_presigned_url", "description": "Generate a time-limited pre-signed URL for temporary secure download or upload.", "params": {"bucket": "string (required)", "key": "string (required)", "expires_in_seconds": "integer (default: 3600)"}, "sample_args": {"bucket": "prod-data-lake", "key": "data.csv", "expires_in_seconds": 1800}, "example_call": "generate_presigned_url(bucket='prod-data-lake', key='data.csv')"},
    {"name": "get_bucket_policy", "description": "Retrieve the JSON IAM access policy attached to an S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_policy(bucket='prod-data-lake')"},
    {"name": "get_bucket_cors", "description": "Retrieve Cross-Origin Resource Sharing (CORS) rules for an S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_cors(bucket='prod-data-lake')"},
    {"name": "get_bucket_encryption", "description": "Get server-side encryption (SSE-S3 / SSE-KMS) configuration for a bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_encryption(bucket='prod-data-lake')"},
    {"name": "get_bucket_lifecycle", "description": "Get lifecycle transitions and expiration rules (e.g. Glacier archiving) for a bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_lifecycle(bucket='prod-data-lake')"},
    {"name": "get_bucket_tagging", "description": "List cost-allocation and environment tags assigned to an S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "prod-data-lake"}, "example_call": "get_bucket_tagging(bucket='prod-data-lake')"},
    {"name": "create_bucket", "description": "Create a new S3 bucket in the configured AWS region.", "params": {"bucket": "string (required)", "region": "string (optional)"}, "sample_args": {"bucket": "new-microservice-assets"}, "example_call": "create_bucket(bucket='new-microservice-assets')"},
    {"name": "delete_bucket", "description": "Delete an empty S3 bucket.", "params": {"bucket": "string (required)"}, "sample_args": {"bucket": "old-temp-bucket"}, "example_call": "delete_bucket(bucket='old-temp-bucket')"}
]

AWS_EC2_TOOLS = [
    {"name": "list_instances", "description": "List EC2 virtual machines with state, instance type, and IP addresses."},
    {"name": "get_instance_status", "description": "Get CPU, health check status, and uptime for an EC2 instance."},
    {"name": "start_instance", "description": "Start a stopped EC2 virtual machine."},
    {"name": "stop_instance", "description": "Stop a running EC2 virtual machine."},
    {"name": "reboot_instance", "description": "Reboot an EC2 virtual machine."},
    {"name": "list_security_groups", "description": "List VPC Security Groups and ingress/egress rules."},
    {"name": "list_key_pairs", "description": "List SSH Key Pairs in region."},
    {"name": "list_volumes", "description": "List attached EBS storage volumes and IOPS."}
]

AWS_LAMBDA_TOOLS = [
    {"name": "list_functions", "description": "List serverless Lambda functions, memory, and runtimes."},
    {"name": "get_function_details", "description": "Get code configuration, timeout, and environment variables."},
    {"name": "invoke_function", "description": "Invoke an AWS Lambda function with JSON payload."},
    {"name": "update_function_code", "description": "Deploy new ZIP package or container image to Lambda."},
    {"name": "list_event_source_mappings", "description": "List event source triggers (SQS, DynamoDB, Kinesis)."},
    {"name": "get_function_logs", "description": "Fetch execution logs from CloudWatch for Lambda function."}
]

SERVICENOW_SNOW_TOOLS = [
    {"name": "create_incident", "description": "Create a new Incident ticket in ServiceNow with priority, caller, category, and short description.", "params": {"short_description": "string (required)", "urgency": "string (1=High, 2=Medium, 3=Low)", "impact": "string (1=High, 2=Medium, 3=Low)", "caller_id": "string (optional)", "category": "string (e.g. software, hardware, network)"}, "sample_args": {"short_description": "Payment Gateway Timeout", "urgency": "1", "impact": "1", "category": "software"}, "example_call": "create_incident(short_description='Payment Gateway Timeout', urgency='1')"},
    {"name": "get_incident", "description": "Retrieve incident details, state, assigned group, SLA status, and notes by number or sys_id.", "params": {"incident_number": "string (e.g. INC0010023)"}, "sample_args": {"incident_number": "INC0010023"}, "example_call": "get_incident(incident_number='INC0010023')"},
    {"name": "update_incident", "description": "Update incident state, assigned user/group, priority, or resolution details.", "params": {"incident_number": "string (required)", "state": "string (2=In Progress, 3=On Hold, 6=Resolved, 7=Closed)", "assigned_to": "string", "work_notes": "string"}, "sample_args": {"incident_number": "INC0010023", "state": "2", "work_notes": "Investigating load balancer logs."}, "example_call": "update_incident(incident_number='INC0010023', state='2')"},
    {"name": "add_work_note", "description": "Add an internal work note or customer-visible comment to an incident.", "params": {"incident_number": "string (required)", "note": "string (required)", "is_customer_visible": "boolean (default: false)"}, "sample_args": {"incident_number": "INC0010023", "note": "Root cause identified as DNS propagation delay."}, "example_call": "add_work_note(incident_number='INC0010023', note='...')"},
    {"name": "close_incident", "description": "Resolve and close an incident with resolution code and resolution notes.", "params": {"incident_number": "string (required)", "close_code": "string", "close_notes": "string (required)"}, "sample_args": {"incident_number": "INC0010023", "close_code": "Solved", "close_notes": "Restarted service and verified 200 OK."}, "example_call": "close_incident(incident_number='INC0010023', close_code='Solved')"},
    {"name": "reopen_incident", "description": "Reopen a previously resolved incident if the problem reoccurs.", "params": {"incident_number": "string (required)", "reason": "string (required)"}, "sample_args": {"incident_number": "INC0010023", "reason": "Intermittent timeouts detected again."}, "example_call": "reopen_incident(incident_number='INC0010023', reason='...')"},
    {"name": "create_change_request", "description": "Create a Change Request (Normal, Standard, Emergency) with implementation plan, backout plan, and risk level.", "params": {"type": "string (normal, standard, emergency)", "short_description": "string", "description": "string", "risk": "string"}, "sample_args": {"type": "normal", "short_description": "Deploy v2.4.0 to Production", "risk": "2"}, "example_call": "create_change_request(type='normal', short_description='Deploy v2.4.0')"},
    {"name": "get_change_request", "description": "Retrieve Change Request status, CAB approval state, schedule, and phase.", "params": {"change_number": "string (e.g. CHG0030012)"}, "sample_args": {"change_number": "CHG0030012"}, "example_call": "get_change_request(change_number='CHG0030012')"},
    {"name": "update_change_phase", "description": "Advance change request workflow state (e.g. Assess, Authorize, Scheduled, Implement, Review, Closed).", "params": {"change_number": "string (required)", "phase": "string (implement, review, closed)"}, "sample_args": {"change_number": "CHG0030012", "phase": "implement"}, "example_call": "update_change_phase(change_number='CHG0030012', phase='implement')"},
    {"name": "create_problem", "description": "Create a Problem record to track root cause analysis across multiple incidents.", "params": {"short_description": "string (required)", "description": "string"}, "sample_args": {"short_description": "Root Cause: Redis Connection Pool Exhaustion"}, "example_call": "create_problem(short_description='Root Cause: Redis Pool')"},
    {"name": "get_problem_details", "description": "Get problem details, associated incidents, root cause, and workaround description.", "params": {"problem_number": "string (e.g. PRB0040001)"}, "sample_args": {"problem_number": "PRB0040001"}, "example_call": "get_problem_details(problem_number='PRB0040001')"},
    {"name": "query_cmdb_ci", "description": "Query CMDB Configuration Items (servers, databases, network gear, microservices) by class or name.", "params": {"ci_class": "string", "query": "string"}, "sample_args": {"ci_class": "cmdb_ci_server", "query": "operational_status=1"}, "example_call": "query_cmdb_ci(ci_class='cmdb_ci_server')"},
    {"name": "get_ci_details", "description": "Retrieve detailed attributes, IP addresses, OS version, and relationship dependencies for a CI.", "params": {"ci_sys_id": "string"}, "sample_args": {"ci_sys_id": "prod-app-server-01"}, "example_call": "get_ci_details(ci_sys_id='prod-app-server-01')"},
    {"name": "list_catalog_items", "description": "List available Service Catalog orderable items and request forms.", "params": {}, "sample_args": {}, "example_call": "list_catalog_items()"},
    {"name": "submit_catalog_request", "description": "Order a Service Catalog item with required request parameters.", "params": {"item_sys_id": "string", "variables": "object"}, "sample_args": {"item_sys_id": "item_12345"}, "example_call": "submit_catalog_request(item_sys_id='item_12345')"},
    {"name": "query_table_api", "description": "Execute dynamic JSON query against ANY ServiceNow table.", "params": {"table_name": "string", "sysparm_query": "string"}, "sample_args": {"table_name": "sys_user_group", "sysparm_query": "active=true"}, "example_call": "query_table_api(table_name='sys_user_group')"}
]

PLATFORM_SPECS: Dict[str, Any] = {
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
    "aws_ec2": {
        "id": "aws_ec2",
        "aliases": ["ec2", "aws ec2", "amazon ec2", "ec2 compute"],
        "name": "AWS EC2 Compute",
        "category": "Cloud Compute",
        "description": "Dedicated suite for EC2 virtual machines, instance lifecycle (start, stop, reboot), security groups, and EBS volumes.",
        "icon": "cpu",
        "fields": [
            {"key": "aws_access_key_id", "label": "AWS Access Key ID", "prompt": "Enter AWS Access Key ID:", "placeholder": "AKIAXXXXXXXXXXXXXXXX", "default": "", "secret": False, "required": True},
            {"key": "aws_secret_access_key", "label": "AWS Secret Access Key", "prompt": "Enter AWS Secret Access Key:", "placeholder": "••••••••••••••••••••••••••••••••", "default": "", "secret": True, "required": True},
            {"key": "aws_region", "label": "Default AWS Region", "prompt": "Default AWS Region:", "placeholder": "us-west-2", "default": "us-west-2", "secret": False, "required": True}
        ],
        "tools": AWS_EC2_TOOLS
    },
    "aws_lambda": {
        "id": "aws_lambda",
        "aliases": ["lambda", "aws lambda", "serverless lambda"],
        "name": "AWS Lambda Serverless",
        "category": "Serverless Compute",
        "description": "Dedicated suite for invoking Lambda functions, updating code, checking environment variables, and reading CloudWatch execution logs.",
        "icon": "zap",
        "fields": [
            {"key": "aws_access_key_id", "label": "AWS Access Key ID", "prompt": "Enter AWS Access Key ID:", "placeholder": "AKIAXXXXXXXXXXXXXXXX", "default": "", "secret": False, "required": True},
            {"key": "aws_secret_access_key", "label": "AWS Secret Access Key", "prompt": "Enter AWS Secret Access Key:", "placeholder": "••••••••••••••••••••••••••••••••", "default": "", "secret": True, "required": True},
            {"key": "aws_region", "label": "Default AWS Region", "prompt": "Default AWS Region:", "placeholder": "us-west-2", "default": "us-west-2", "secret": False, "required": True}
        ],
        "tools": AWS_LAMBDA_TOOLS
    },
    "aws": {
        "id": "aws",
        "aliases": ["amazon", "amazon web services", "aws general", "aws infra"],
        "name": "AWS Cloud Infrastructure",
        "category": "Cloud & Infrastructure",
        "description": "Comprehensive 24-tool suite across EC2, S3, Lambda, ECS, EKS, CloudWatch, CloudFormation, and IAM.",
        "icon": "cloud",
        "fields": [
            {"key": "aws_access_key_id", "label": "AWS Access Key ID", "prompt": "Enter your AWS Access Key ID:", "placeholder": "AKIAXXXXXXXXXXXXXXXX", "default": "", "secret": False, "required": True},
            {"key": "aws_secret_access_key", "label": "AWS Secret Access Key", "prompt": "Enter your AWS Secret Access Key:", "placeholder": "••••••••••••••••••••••••••••••••", "default": "", "secret": True, "required": True},
            {"key": "aws_region", "label": "Default AWS Region", "prompt": "Default AWS region (e.g. us-west-2, us-east-1):", "placeholder": "us-west-2", "default": "us-west-2", "secret": False, "required": True}
        ],
        "tools": AWS_S3_TOOLS[:5] + AWS_EC2_TOOLS[:5] + AWS_LAMBDA_TOOLS[:4]
    },
    "servicenow": {
        "id": "servicenow",
        "aliases": ["snow", "service-now", "service now", "servicenow itsm"],
        "name": "ServiceNow (SNOW)",
        "category": "ITSM & Enterprise Service Management",
        "description": "Comprehensive enterprise suite: Incidents, Change Requests, Problems, CMDB CIs, Service Catalog, Work Notes, User Roles, and Table APIs.",
        "icon": "layers",
        "fields": [
            {"key": "instance_url", "label": "ServiceNow Instance URL", "prompt": "Enter your ServiceNow instance URL (e.g. https://dev12345.service-now.com):", "placeholder": "https://devXXXXX.service-now.com", "default": "", "secret": False, "required": True},
            {"key": "username", "label": "Username / Integration Account", "prompt": "Enter your ServiceNow integration username:", "placeholder": "admin", "default": "", "secret": False, "required": True},
            {"key": "password", "label": "Password or API Token", "prompt": "Enter your ServiceNow password or API token:", "placeholder": "••••••••••••", "default": "", "secret": True, "required": True}
        ],
        "tools": SERVICENOW_SNOW_TOOLS
    },
    "github": {
        "id": "github",
        "aliases": ["gh", "github enterprise", "git hub"],
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
    "terraform": {
        "id": "terraform",
        "aliases": ["tf", "terraform cloud", "terraform enterprise"],
        "name": "Terraform Cloud & Enterprise",
        "category": "Infrastructure as Code",
        "description": "Comprehensive 20-tool suite: Workspaces, Runs, Plans, State Versions, Variables, Varsets, Policy Checks, and Configuration versions.",
        "icon": "server",
        "fields": [
            {"key": "organization", "label": "Terraform Org Name", "prompt": "Terraform Cloud organization name:", "placeholder": "my-org", "default": "", "secret": False, "required": True},
            {"key": "api_token", "label": "User / Team API Token", "prompt": "Terraform Cloud API Token:", "placeholder": "••••••••••••", "default": "", "secret": True, "required": True}
        ],
        "tools": [
            {"name": "list_workspaces", "description": "List all Terraform workspaces in the organization."},
            {"name": "get_workspace_details", "description": "Get workspace status, terraform version, and auto-apply setting."},
            {"name": "create_workspace", "description": "Create a new Terraform workspace with execution mode."},
            {"name": "delete_workspace", "description": "Delete a Terraform workspace permanently."},
            {"name": "create_run", "description": "Trigger a Terraform plan or apply run on a workspace."},
            {"name": "get_run_status", "description": "Check status (planned, applying, applied, errored) of a run."},
            {"name": "apply_run", "description": "Confirm and apply a planned Terraform run."},
            {"name": "discard_run", "description": "Discard or cancel an active/planned run."},
            {"name": "list_state_versions", "description": "List historical state file versions for a workspace."},
            {"name": "list_workspace_variables", "description": "List all Terraform and environment variables in a workspace."},
            {"name": "create_workspace_variable", "description": "Add a new Terraform or environment variable."}
        ]
    }
}


def find_platform_by_query(query: str) -> Any:
    q = query.lower().strip()

    # 1. First check specific sub-service keywords (e.g. s3, ec2, lambda)
    if "s3" in q:
        return PLATFORM_SPECS["aws_s3"]
    if "ec2" in q:
        return PLATFORM_SPECS["aws_ec2"]
    if "lambda" in q:
        return PLATFORM_SPECS["aws_lambda"]

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

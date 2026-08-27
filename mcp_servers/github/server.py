"""
GitHub Enterprise FastMCP Server (45-Tool Enterprise Suite)
Reads credentials locally from mcp_servers/github/.env or OS keyring.
Provides complete coverage: Repos, Topics, Issues, Comments, Milestones, Labels, PRs, Reviews, Actions CI/CD, Artifacts, Dependabot Alerts, Code Scanning, Secret Scanning, Deployments, Environments, Collaborators, Commits, Releases, and Global Search.
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
    load_dotenv(ENV_PATH, override=True)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.mcpserver import MCPServer as FastMCP
    except ImportError:
        from mcp.server import Server as FastMCP

mcp = FastMCP("github-enterprise-server")
SERVICE_NAME = "mcp_github"


def safe_get_keyring(service: str, key: str) -> str:
    try:
        return keyring.get_password(service, key) or ""
    except Exception:
        return ""


def get_github_credentials() -> Dict[str, str]:
    """Retrieve credentials from local .env or fallback to OS keyring."""
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH, override=True)
    base_url = (
        os.environ.get("GITHUB_BASE_URL") or
        os.environ.get("BASE_URL") or
        safe_get_keyring(SERVICE_NAME, "base_url") or
        "https://api.github.com"
    )
    org = (
        os.environ.get("GITHUB_ORG") or
        os.environ.get("ORG") or
        os.environ.get("GITHUB_USERNAME") or
        safe_get_keyring(SERVICE_NAME, "org") or
        ""
    )
    token = (
        os.environ.get("GITHUB_TOKEN") or
        os.environ.get("GITHUB_PAT") or
        os.environ.get("TOKEN") or
        os.environ.get("AUTH_HEADER") or
        safe_get_keyring(SERVICE_NAME, "token") or
        ""
    )
    return {
        "base_url": base_url.rstrip("/"),
        "org": org,
        "token": token
    }


def get_headers(token: str) -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "MCP-Gateway-GitHub-Enterprise/1.0"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def parse_response(res: httpx.Response, url: str):
    if res.status_code in [200, 201]:
        try:
            return res.json()
        except Exception:
            return res.text
    elif res.status_code in [401, 403]:
        return f"🔒 GitHub Authentication / Permission Error ({res.status_code}): {res.text[:300]}"
    elif res.status_code == 404:
        return f"🔍 GitHub resource not found (404) at {url}."
    else:
        return f"GitHub API Error ({res.status_code}): {res.text[:300]}"


def resolve_repo(repo: Optional[str] = None, owner: Optional[str] = None) -> str:
    creds = get_github_credentials()
    org = (creds.get("org") or "").strip()
    repo_str = (repo or "").strip()
    owner_str = (owner or "").strip()

    if "/" in repo_str:
        return repo_str
    if owner_str and repo_str:
        return f"{owner_str}/{repo_str}"
    if org and repo_str:
        return f"{org}/{repo_str}"
    if owner_str and not repo_str:
        return owner_str
    return repo_str


# --- 1. Repositories & Metadata (7 tools) ---

@mcp.tool()
def list_repos(
    org: Optional[str] = None,
    user: Optional[str] = None,
    owner: Optional[str] = None,
    limit: Optional[int] = None,
    per_page: Optional[int] = None,
    page: int = 1,
    sort: str = "updated",
    direction: str = "desc",
    type: str = "all",
    visibility: Optional[str] = None,
    affiliation: Optional[str] = None
) -> str:
    """List repositories for authenticated user or org with visibility, stars, forks, language, and pagination."""
    creds = get_github_credentials()
    target = (org or user or owner or creds.get("org") or "").strip()
    try:
        count = int(per_page or limit or 30)
    except Exception:
        count = 30
    try:
        page_num = int(page or 1)
    except Exception:
        page_num = 1

    params = {
        "per_page": min(max(count, 1), 100),
        "page": page_num,
        "sort": sort,
        "direction": direction
    }
    if type and type != "all":
        params["type"] = type
    if visibility:
        params["visibility"] = visibility
    if affiliation:
        params["affiliation"] = affiliation

    # If authenticated, /user/repos retrieves all accessible public and private repositories
    if creds.get("token") and (not target or target == creds.get("org")):
        url = f"{creds['base_url']}/user/repos"
        if type:
            params["type"] = type
    elif target:
        url = f"{creds['base_url']}/users/{target}/repos"
    else:
        url = f"{creds['base_url']}/user/repos"

    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=20.0) as client:
            res = client.get(url, params=params)
            # Fallback if target is an organization
            if res.status_code == 404 and target:
                fallback_url = f"{creds['base_url']}/orgs/{target}/repos"
                res = client.get(fallback_url, params=params)
                url = fallback_url

            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No repositories found for '{target or 'user'}' (Page {page})."
            lines = [f"GitHub Repositories ({len(data)} returned, Page {page}):"]
            for r in data:
                vis = "🔒 Private" if r.get("private") else "🌐 Public"
                lang = r.get("language") or "General"
                stars = r.get("stargazers_count", 0)
                forks = r.get("forks_count", 0)
                updated = (r.get("updated_at") or "")[:10]
                lines.append(f"- **{r.get('full_name')}** ({vis}, ⭐ {stars}, 🍴 {forks}, `{lang}`, updated: {updated})\n  URL: {r.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing repos: {e}"


@mcp.tool()
def get_repo_details(repo: Optional[str] = None, owner: Optional[str] = None) -> str:
    """Get detailed metadata for a repository (stars, forks, open issues count, default branch, language)."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo, owner)
    url = f"{creds['base_url']}/repos/{full_repo}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return (
                f"**Repository: {data.get('full_name')}**\n"
                f"- Description: {data.get('description') or 'No description'}\n"
                f"- Default Branch: `{data.get('default_branch')}`\n"
                f"- Visibility: {'Private' if data.get('private') else 'Public'}\n"
                f"- Stars: ⭐ {data.get('stargazers_count', 0)} | Forks: 🍴 {data.get('forks_count', 0)}\n"
                f"- Open Issues / PRs: {data.get('open_issues_count', 0)}\n"
                f"- Clone URL: `{data.get('clone_url')}`"
            )
    except Exception as e:
        return f"Error fetching repo details: {e}"


@mcp.tool()
def create_repo(name: str, description: Optional[str] = None, private: bool = True) -> str:
    """Create a new repository in configured organization or user account."""
    creds = get_github_credentials()
    url = f"{creds['base_url']}/orgs/{creds['org']}/repos" if creds["org"] else f"{creds['base_url']}/user/repos"
    payload = {"name": name, "description": description or "", "private": private, "auto_init": True}
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json=payload)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"✅ Repository **{data.get('full_name')}** created!\nURL: {data.get('html_url')}"
    except Exception as e:
        return f"Error creating repo: {e}"


@mcp.tool()
def fork_repo(owner: str, repo: str) -> str:
    """Fork a repository into your user or target organization."""
    creds = get_github_credentials()
    url = f"{creds['base_url']}/repos/{owner}/{repo}/forks"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🍴 Fork initiated for **{owner}/{repo}** -> **{data.get('full_name')}**."
    except Exception as e:
        return f"Error forking repo: {e}"


@mcp.tool()
def delete_repo(repo: str) -> str:
    """Delete a repository permanently."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.delete(url)
            if res.status_code in [204, 200]:
                return f"🗑️ Repository **{full_repo}** deleted successfully."
            return parse_response(res, url)
    except Exception as e:
        return f"Error deleting repo: {e}"


@mcp.tool()
def list_repo_topics(repo: str) -> str:
    """List all topic tags assigned to a repository."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/topics"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            topics = data.get("names", [])
            return f"Topics for {full_repo}: {', '.join(topics) if topics else 'No topics assigned.'}"
    except Exception as e:
        return f"Error getting topics: {e}"


@mcp.tool()
def update_repo_topics(repo: str, topics: List[str]) -> str:
    """Replace topic tags on a repository."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/topics"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.put(url, json={"names": topics})
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🏷️ Topics updated for {full_repo}: {', '.join(data.get('names', []))}"
    except Exception as e:
        return f"Error updating topics: {e}"


# --- 2. Issues & Discussions (8 tools) ---

@mcp.tool()
def list_issues(repo: Optional[str] = None, owner: Optional[str] = None, state: str = "open", labels: Optional[str] = None) -> str:
    """List repository issues filtered by state (open, closed), label, or assignee."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo, owner)
    url = f"{creds['base_url']}/repos/{full_repo}/issues?state={state}"
    if labels: url += f"&labels={labels}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            issues = [i for i in data if "pull_request" not in i]
            if not issues: return f"No {state} issues found in {full_repo}."
            lines = [f"Issues in {full_repo} ({len(issues)} {state}):"]
            for i in issues:
                lbls = ", ".join([l.get("name") for l in i.get("labels", [])])
                lines.append(f"- #{i.get('number')}: **{i.get('title')}** by @{i.get('user', {}).get('login')} (`{lbls or 'None'}`)\n  URL: {i.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing issues: {e}"


@mcp.tool()
def get_issue(repo: Optional[str] = None, issue_number: int = 1, owner: Optional[str] = None) -> str:
    """Get detailed issue author, labels, body, and status."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo, owner)
    url = f"{creds['base_url']}/repos/{full_repo}/issues/{issue_number}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"**Issue #{data.get('number')}: {data.get('title')}**\n- State: `{data.get('state')}` (Comments: {data.get('comments')})\n- Author: @{data.get('user', {}).get('login')}\n- Description:\n{data.get('body') or 'No description'}\n- URL: {data.get('html_url')}"
    except Exception as e:
        return f"Error getting issue: {e}"


@mcp.tool()
def create_issue(title: str, repo: Optional[str] = None, owner: Optional[str] = None, body: Optional[str] = None, labels: Optional[List[str]] = None) -> str:
    """Create a new issue with markdown body, assignees, and labels."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo, owner)
    url = f"{creds['base_url']}/repos/{full_repo}/issues"
    payload = {"title": title, "body": body or "", "labels": labels or []}
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json=payload)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"✅ Created Issue **#{data.get('number')}**: {data.get('title')}\nURL: {data.get('html_url')}"
    except Exception as e:
        return f"Error creating issue: {e}"


@mcp.tool()
def update_issue(repo: str, issue_number: int, title: Optional[str] = None, body: Optional[str] = None, state: Optional[str] = None) -> str:
    """Update issue title, body, or state."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/issues/{issue_number}"
    payload = {}
    if title: payload["title"] = title
    if body: payload["body"] = body
    if state: payload["state"] = state
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.patch(url, json=payload)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"✅ Updated Issue #{issue_number}: {data.get('title')} (State: `{data.get('state')}`)"
    except Exception as e:
        return f"Error updating issue: {e}"


@mcp.tool()
def add_issue_comment(repo: str, issue_number: int, comment_body: str) -> str:
    """Add a comment to an existing issue or pull request."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/issues/{issue_number}/comments"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json={"body": comment_body})
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"💬 Comment added to #{issue_number}!\nURL: {data.get('html_url')}"
    except Exception as e:
        return f"Error adding comment: {e}"


@mcp.tool()
def list_issue_comments(repo: str, issue_number: int) -> str:
    """List all comments and discussion thread on an issue."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/issues/{issue_number}/comments"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No comments on issue #{issue_number}."
            lines = [f"Comments on Issue #{issue_number} ({len(data)} total):"]
            for c in data:
                lines.append(f"- @{c.get('user', {}).get('login')} at {c.get('created_at')}:\n  {c.get('body')[:200]}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing comments: {e}"


@mcp.tool()
def close_issue(repo: str, issue_number: int, state_reason: str = "completed") -> str:
    """Close an issue with optional reason (completed, not_planned)."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/issues/{issue_number}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.patch(url, json={"state": "closed", "state_reason": state_reason})
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🔒 Closed issue #{issue_number} (Reason: {state_reason})."
    except Exception as e:
        return f"Error closing issue: {e}"


@mcp.tool()
def lock_issue(repo: str, issue_number: int, lock_reason: str = "resolved") -> str:
    """Lock conversation on an issue to restrict comments."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/issues/{issue_number}/lock"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.put(url, json={"lock_reason": lock_reason})
            if res.status_code in [204, 200]:
                return f"🔒 Issue #{issue_number} locked (Reason: {lock_reason})."
            return parse_response(res, url)
    except Exception as e:
        return f"Error locking issue: {e}"


# --- 3. Milestones & Labels (4 tools) ---

@mcp.tool()
def list_milestones(repo: str) -> str:
    """List sprint milestones, due dates, and completion percentage."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/milestones"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No milestones configured in {full_repo}."
            lines = [f"Milestones in {full_repo}:"]
            for m in data:
                lines.append(f"- **{m.get('title')}** (Open: {m.get('open_issues')}, Closed: {m.get('closed_issues')}, Due: {m.get('due_on') or 'None'})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing milestones: {e}"


@mcp.tool()
def create_milestone(repo: str, title: str, description: Optional[str] = None, due_on: Optional[str] = None) -> str:
    """Create a new release milestone with due date."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/milestones"
    payload = {"title": title, "description": description or ""}
    if due_on: payload["due_on"] = due_on
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json=payload)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🎯 Milestone **{data.get('title')}** created!"
    except Exception as e:
        return f"Error creating milestone: {e}"


@mcp.tool()
def list_labels(repo: str) -> str:
    """List all configured issue and PR labels in a repository."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/labels"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            lines = [f"Labels in {full_repo} ({len(data)} total):"]
            for l in data:
                lines.append(f"- `{l.get('name')}` (Color: #{l.get('color')}, Desc: {l.get('description') or 'None'})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing labels: {e}"


@mcp.tool()
def create_label(repo: str, name: str, color: str = "1d76db", description: Optional[str] = None) -> str:
    """Create a new label with name, color hex, and description."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/labels"
    payload = {"name": name, "color": color.lstrip("#"), "description": description or ""}
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json=payload)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🏷️ Label `{data.get('name')}` created successfully!"
    except Exception as e:
        return f"Error creating label: {e}"


# --- 4. Pull Requests & Reviews (8 tools) ---

@mcp.tool()
def list_pull_requests(
    repo: Optional[str] = None,
    owner: Optional[str] = None,
    state: str = "open",
    base: Optional[str] = None,
    sort: Optional[str] = "created",
    direction: Optional[str] = "desc"
) -> str:
    """List pull requests in a repository filtered by state, base branch, sort, and direction."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo, owner)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls?state={state}"
    if base: url += f"&base={base}"
    if sort: url += f"&sort={sort}"
    if direction: url += f"&direction={direction}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No {state} PRs found in {full_repo}."
            lines = [f"Pull Requests in {full_repo} ({len(data)} {state}):"]
            for pr in data:
                lines.append(f"- PR #{pr.get('number')}: **{pr.get('title')}** (`{pr.get('head', {}).get('ref')}` -> `{pr.get('base', {}).get('ref')}`) by @{pr.get('user', {}).get('login')}\n  URL: {pr.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing PRs: {e}"


@mcp.tool()
def get_pr_status(repo: str, pr_number: int) -> str:
    """Get detailed PR status, CI checks, review approvals, and mergeability."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls/{pr_number}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"**Pull Request #{data.get('number')}: {data.get('title')}**\n- State: `{data.get('state')}` (Merged: `{data.get('merged')}`, Mergeable: `{data.get('mergeable')}`)\n- Changes: +{data.get('additions', 0)} / -{data.get('deletions', 0)} ({data.get('changed_files', 0)} files)\n- URL: {data.get('html_url')}"
    except Exception as e:
        return f"Error getting PR status: {e}"


@mcp.tool()
def create_pull_request(repo: str, title: str, head: str, base: str = "main", body: Optional[str] = None) -> str:
    """Create a new PR between head and base branches."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json={"title": title, "head": head, "base": base, "body": body or ""})
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🚀 Created PR **#{data.get('number')}**: {data.get('title')}\nURL: {data.get('html_url')}"
    except Exception as e:
        return f"Error creating PR: {e}"


@mcp.tool()
def merge_pull_request(repo: str, pr_number: int, merge_method: str = "squash") -> str:
    """Merge PR using merge, squash, or rebase strategy."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls/{pr_number}/merge"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.put(url, json={"merge_method": merge_method})
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🔀 PR #{pr_number} merged successfully ({merge_method})!"
    except Exception as e:
        return f"Error merging PR: {e}"


@mcp.tool()
def list_pr_files(repo: str, pr_number: int) -> str:
    """List all modified files, additions, and deletions in a PR."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls/{pr_number}/files"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            lines = [f"Files in PR #{pr_number} ({len(data)} files):"]
            for f in data:
                lines.append(f"- `{f.get('filename')}` (+{f.get('additions')}/-{f.get('deletions')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing PR files: {e}"


@mcp.tool()
def add_pr_review_comment(repo: str, pr_number: int, event: str = "APPROVE", body: str = "LGTM") -> str:
    """Submit a code review on a PR (APPROVE, REQUEST_CHANGES, or COMMENT)."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls/{pr_number}/reviews"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json={"event": event, "body": body})
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"📝 Submitted review ({event}) on PR #{pr_number}."
    except Exception as e:
        return f"Error adding review: {e}"


@mcp.tool()
def list_pr_reviews(repo: str, pr_number: int) -> str:
    """List all submitted review approvals and change requests for a PR."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls/{pr_number}/reviews"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No reviews on PR #{pr_number}."
            lines = [f"Reviews for PR #{pr_number}:"]
            for r in data:
                lines.append(f"- @{r.get('user', {}).get('login')}: `{r.get('state')}` ({r.get('submitted_at')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing PR reviews: {e}"


@mcp.tool()
def update_pr_branch(repo: str, pr_number: int) -> str:
    """Update a pull request branch by merging target base branch."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/pulls/{pr_number}/update-branch"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.put(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🔄 Branch updated successfully for PR #{pr_number}!"
    except Exception as e:
        return f"Error updating PR branch: {e}"


# --- 5. GitHub Actions CI/CD (7 tools) ---

@mcp.tool()
def list_workflows(repo: str) -> str:
    """List all GitHub Actions workflow YAML pipelines configured in a repo."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/workflows"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            workflows = data.get("workflows", [])
            lines = [f"Workflows in {full_repo} ({len(workflows)} total):"]
            for w in workflows:
                lines.append(f"- **{w.get('name')}** (ID: `{w.get('id')}`, Path: `{w.get('path')}`)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing workflows: {e}"


@mcp.tool()
def trigger_workflow_dispatch(repo: str, workflow_id: str, ref: str = "main", inputs: Optional[Dict[str, Any]] = None) -> str:
    """Trigger a GitHub Actions workflow manually with branch ref and inputs."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/workflows/{workflow_id}/dispatches"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json={"ref": ref, "inputs": inputs or {}})
            if res.status_code in [200, 204]:
                return f"🚀 Workflow dispatch triggered for **{workflow_id}** on branch `{ref}`!"
            return parse_response(res, url)
    except Exception as e:
        return f"Error triggering workflow: {e}"


@mcp.tool()
def list_workflow_runs(repo: str) -> str:
    """List recent workflow execution runs, status, and conclusion."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/runs?per_page=10"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            runs = data.get("workflow_runs", [])
            lines = [f"Workflow Runs in {full_repo} ({len(runs)} runs):"]
            for r in runs:
                conclusion = r.get("conclusion") or r.get("status")
                emoji = "✅" if conclusion == "success" else ("❌" if conclusion == "failure" else "⏳")
                lines.append(f"- {emoji} Run #{r.get('run_number')} (**{r.get('name')}**): `{conclusion}` (ID: `{r.get('id')}`)\n  URL: {r.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing runs: {e}"


@mcp.tool()
def get_workflow_run_logs(repo: str, run_id: int) -> str:
    """Fetch execution summary and logs for a GitHub Actions workflow run."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/runs/{run_id}/jobs"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            jobs = data.get("jobs", [])
            lines = [f"**Jobs for Workflow Run #{run_id}:**"]
            for j in jobs:
                lines.append(f"- **{j.get('name')}**: `{j.get('conclusion') or j.get('status')}`")
            return "\n".join(lines)
    except Exception as e:
        return f"Error getting logs: {e}"


@mcp.tool()
def cancel_workflow_run(repo: str, run_id: int) -> str:
    """Cancel an active running GitHub Actions workflow run."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/runs/{run_id}/cancel"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url)
            if res.status_code in [202, 200]: return f"🛑 Cancel signal sent for Run #{run_id}."
            return parse_response(res, url)
    except Exception as e:
        return f"Error cancelling workflow: {e}"


@mcp.tool()
def rerun_workflow(repo: str, run_id: int) -> str:
    """Re-run failed jobs or entire workflow run in GitHub Actions."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/runs/{run_id}/rerun-failed-jobs"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url)
            if res.status_code in [201, 200, 202]: return f"🔄 Re-run initiated for Run #{run_id}."
            return parse_response(res, url)
    except Exception as e:
        return f"Error rerunning workflow: {e}"


@mcp.tool()
def list_workflow_run_artifacts(repo: str, run_id: int) -> str:
    """List downloadable build artifacts produced by a workflow run."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/runs/{run_id}/artifacts"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            artifacts = data.get("artifacts", [])
            lines = [f"Artifacts for Run #{run_id} ({len(artifacts)} total):"]
            for a in artifacts:
                lines.append(f"- 📦 **{a.get('name')}** ({a.get('size_in_bytes', 0)/(1024*1024):.2f} MB)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing artifacts: {e}"


# --- 6. Security, Vulnerabilities & Dependabot (4 tools) ---

@mcp.tool()
def list_dependabot_alerts(repo: str, state: str = "open") -> str:
    """List open Dependabot dependency vulnerability alerts in a repository."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/dependabot/alerts?state={state}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No {state} Dependabot alerts in {full_repo}."
            lines = [f"Dependabot Alerts ({len(data)} {state}):"]
            for a in data:
                sec = a.get("security_advisory", {})
                lines.append(f"- ⚠️ **{sec.get('summary')}** (`{a.get('dependency', {}).get('package', {}).get('name')}`, Severity: `{sec.get('severity')}`)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing dependabot alerts: {e}"


@mcp.tool()
def list_code_scanning_alerts(repo: str, state: str = "open") -> str:
    """List CodeQL static analysis security alerts and severity levels."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/code-scanning/alerts?state={state}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No {state} Code Scanning alerts in {full_repo}."
            lines = [f"Code Scanning Alerts ({len(data)} {state}):"]
            for a in data:
                lines.append(f"- 🛡️ **{a.get('rule', {}).get('description')}** (Severity: `{a.get('rule', {}).get('severity')}`, Location: `{a.get('most_recent_instance', {}).get('location', {}).get('path')}`)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing code scanning alerts: {e}"


@mcp.tool()
def list_secret_scanning_alerts(repo: str, state: str = "open") -> str:
    """List detected leaked tokens and secret scanning alerts."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/secret-scanning/alerts?state={state}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No {state} secret scanning alerts in {full_repo}."
            lines = [f"Secret Scanning Alerts ({len(data)} {state}):"]
            for a in data:
                lines.append(f"- 🔑 **{a.get('secret_type_display_name')}** (State: `{a.get('state')}`, Created: {a.get('created_at')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing secret alerts: {e}"


@mcp.tool()
def get_security_advisories(ecosystem: str = "pip") -> str:
    """List global security advisories affecting repository packages."""
    creds = get_github_credentials()
    url = f"{creds['base_url']}/advisories?ecosystem={ecosystem}&per_page=10"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            lines = [f"GitHub Security Advisories for `{ecosystem}`:"]
            for adv in data:
                lines.append(f"- **{adv.get('summary')}** (GHSA: `{adv.get('ghsa_id')}`, Severity: `{adv.get('severity')}`)")
            return "\n".join(lines)
    except Exception as e:
        return f"Error getting advisories: {e}"


# --- 7. Deployments, Environments & Secrets (4 tools) ---

@mcp.tool()
def list_environments(repo: str) -> str:
    """List deployment environments (e.g. production, staging) and protection rules."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/environments"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            envs = data.get("environments", [])
            lines = [f"Environments in {full_repo} ({len(envs)} total):"]
            for e in envs:
                lines.append(f"- 🌐 **{e.get('name')}** (Created: {e.get('created_at')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing environments: {e}"


@mcp.tool()
def create_deployment(repo: str, ref: str = "main", environment: str = "production", description: Optional[str] = None) -> str:
    """Create a GitHub Deployment tracking deployment events."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/deployments"
    payload = {"ref": ref, "environment": environment, "description": description or "", "auto_merge": False}
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json=payload)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🚀 Deployment #{data.get('id')} created for `{ref}` on environment `{environment}`!"
    except Exception as e:
        return f"Error creating deployment: {e}"


@mcp.tool()
def list_deployments(repo: str, environment: Optional[str] = None) -> str:
    """List deployment history and statuses for an environment."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/deployments"
    if environment: url += f"?environment={environment}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            lines = [f"Deployments in {full_repo} ({len(data)} total):"]
            for d in data:
                lines.append(f"- ID #{d.get('id')}: Ref `{d.get('ref')}` -> `{d.get('environment')}` by @{d.get('creator', {}).get('login')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing deployments: {e}"


@mcp.tool()
def list_repo_secrets(repo: str) -> str:
    """List configured Actions secret names (encrypted values are masked)."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/actions/secrets"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            secrets = data.get("secrets", [])
            lines = [f"Actions Secrets in {full_repo} ({len(secrets)} configured):"]
            for s in secrets:
                lines.append(f"- 🔑 `{s.get('name')}` (Updated: {s.get('updated_at')})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing secrets: {e}"


# --- 8. Collaborators & Permissions (3 tools) ---

@mcp.tool()
def list_collaborators(repo: str) -> str:
    """List users and teams with access permissions to a repository."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/collaborators"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            lines = [f"Collaborators on {full_repo}:"]
            for c in data:
                perms = [k for k, v in c.get("permissions", {}).items() if v]
                lines.append(f"- @{c.get('login')} (Role: `{c.get('role_name')}`, Permissions: {', '.join(perms)})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing collaborators: {e}"


@mcp.tool()
def add_collaborator(repo: str, username: str, permission: str = "push") -> str:
    """Invite or add a user as repository collaborator with role (pull, push, admin)."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/collaborators/{username}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.put(url, json={"permission": permission})
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"👥 Collaborator @{username} added/invited to {full_repo} with `{permission}` permission."
    except Exception as e:
        return f"Error adding collaborator: {e}"


@mcp.tool()
def check_collaborator_permission(repo: str, username: str) -> str:
    """Check specific permission level (admin, write, read) for a user."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/collaborators/{username}/permission"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"Permission for @{username} on {full_repo}: `{data.get('permission')}`"
    except Exception as e:
        return f"Error checking permission: {e}"


# --- 9. Branches, Commits & Releases (6 tools) ---

@mcp.tool()
def list_branches(repo: str) -> str:
    """List repository branches, protected status, and latest commit SHAs."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/branches"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            lines = [f"Branches in {full_repo} ({len(data)} total):"]
            for b in data:
                prot = "🔒 Protected" if b.get("protected") else "Unlocked"
                lines.append(f"- **{b.get('name')}** (`{(b.get('commit', {}).get('sha') or '')[:8]}`, {prot})")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing branches: {e}"


@mcp.tool()
def get_branch_protection(repo: str, branch: str = "main") -> str:
    """Get branch protection rules (required reviews, status checks)."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/branches/{branch}/protection"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            if res.status_code == 404: return f"No branch protection rules configured for '{branch}' in {full_repo}."
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"**Branch Protection for `{branch}`:**\n- Required Approvals: {data.get('required_pull_request_reviews', {}).get('required_approving_review_count', 0)}\n- Enforce Admins: `{data.get('enforce_admins', {}).get('enabled', False)}`"
    except Exception as e:
        return f"Error getting protection rules: {e}"


@mcp.tool()
def get_commit_details(repo: str, commit_sha: str) -> str:
    """Get commit author, date, message, stats, and changed files for a SHA."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/commits/{commit_sha}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            commit = data.get("commit", {})
            return f"**Commit: `{commit_sha[:8]}`**\n- Author: {commit.get('author', {}).get('name')}\n- Message: {commit.get('message')}\n- Stats: +{data.get('stats', {}).get('additions', 0)} / -{data.get('stats', {}).get('deletions', 0)}"
    except Exception as e:
        return f"Error getting commit: {e}"


@mcp.tool()
def compare_commits(repo: str, base: str = "main", head: str = "develop") -> str:
    """Compare commit differences and diff stats between two branches or SHAs."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/compare/{base}...{head}"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"**Comparison: `{base}` ➔ `{head}`:**\n- Status: `{data.get('status')}` (Ahead by: {data.get('ahead_by')}, Behind by: {data.get('behind_by')})\n- Total Commits: {data.get('total_commits')}\n- Files Changed: {len(data.get('files', []))}"
    except Exception as e:
        return f"Error comparing commits: {e}"


@mcp.tool()
def list_releases(repo: str) -> str:
    """List published GitHub releases, tag names, assets, and changelogs."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/releases"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            if not data: return f"No releases published for {full_repo}."
            lines = [f"Releases for {full_repo}:"]
            for r in data:
                lines.append(f"- 🏷️ **{r.get('name') or r.get('tag_name')}** (Tag: `{r.get('tag_name')}`, Published: {r.get('published_at')})\n  URL: {r.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error listing releases: {e}"


@mcp.tool()
def create_release(repo: str, tag_name: str, name: Optional[str] = None, body: Optional[str] = None) -> str:
    """Publish a new release with tag name, release title, and notes."""
    creds = get_github_credentials()
    full_repo = resolve_repo(repo)
    url = f"{creds['base_url']}/repos/{full_repo}/releases"
    payload = {"tag_name": tag_name, "name": name or tag_name, "body": body or ""}
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.post(url, json=payload)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            return f"🎉 Release **{data.get('name')}** created!\nURL: {data.get('html_url')}"
    except Exception as e:
        return f"Error creating release: {e}"


# --- 10. Global Search (4 tools) ---

@mcp.tool()
def search_code(query: str) -> str:
    """Search code strings, functions, or patterns across organization repositories."""
    creds = get_github_credentials()
    owner = creds["org"]
    full_query = f"{query} org:{owner}" if owner and "org:" not in query else query
    url = f"{creds['base_url']}/search/code?q={full_query}&per_page=10"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            items = data.get("items", [])
            if not items: return f"No code matches found for '{query}'."
            lines = [f"Code Search Results ({len(items)} matches):"]
            for i in items:
                lines.append(f"- **{i.get('repository', {}).get('full_name')}**: `{i.get('path')}`\n  URL: {i.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error searching code: {e}"


@mcp.tool()
def search_repositories(query: str) -> str:
    """Search repositories by keyword, language, or stars."""
    creds = get_github_credentials()
    url = f"{creds['base_url']}/search/repositories?q={query}&per_page=10"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            items = data.get("items", [])
            lines = [f"Repository Search Results ({len(items)} matches):"]
            for r in items:
                lines.append(f"- **{r.get('full_name')}** (⭐ {r.get('stargazers_count', 0)}, `{r.get('language')}`)\n  URL: {r.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error searching repos: {e}"


@mcp.tool()
def search_issues(query: str) -> str:
    """Search issues and pull requests across all organization repositories."""
    creds = get_github_credentials()
    url = f"{creds['base_url']}/search/issues?q={query}&per_page=10"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            items = data.get("items", [])
            lines = [f"Issues/PR Search Results ({len(items)} matches):"]
            for i in items:
                lines.append(f"- #{i.get('number')}: **{i.get('title')}** (State: `{i.get('state')}`)\n  URL: {i.get('html_url')}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error searching issues: {e}"


@mcp.tool()
def search_commits(query: str) -> str:
    """Search commit messages and authors across organization repositories."""
    creds = get_github_credentials()
    url = f"{creds['base_url']}/search/commits?q={query}&per_page=10"
    try:
        with httpx.Client(verify=False, headers=get_headers(creds["token"]), timeout=15.0) as client:
            res = client.get(url)
            data = parse_response(res, url)
            if isinstance(data, str): return data
            items = data.get("items", [])
            lines = [f"Commit Search Results ({len(items)} matches):"]
            for c in items:
                commit = c.get("commit", {})
                lines.append(f"- `{c.get('sha', '')[:8]}` by @{c.get('author', {}).get('login', 'dev')}: {commit.get('message', '')[:60]}")
            return "\n".join(lines)
    except Exception as e:
        return f"Error searching commits: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

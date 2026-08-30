"""
Docker Engine MCP Server Functions
Exposes direct Python functions for container lifecycle, inspection, logs, and image management.
"""

import subprocess
import json
import logging

logger = logging.getLogger("docker_mcp")


def _run_docker(args: list):
    try:
        proc = subprocess.run(["docker"] + args, capture_output=True, text=True, timeout=30)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)


def list_containers(all: bool = True):
    """List all Docker containers (running and stopped) with status, ports, and names."""
    cmd = ["ps", "-a", "--format", "json"] if all else ["ps", "--format", "json"]
    code, out, err = _run_docker(cmd)
    if code != 0:
        cmd = ["ps", "-a"] if all else ["ps"]
        code, out, err = _run_docker(cmd)
        return out or err

    containers = []
    for line in out.strip().split("\n"):
        if line.strip():
            try:
                containers.append(json.loads(line))
            except Exception:
                pass
    return containers if containers else out


def get_container_logs(container_name: str, tail: int = 50):
    """Fetch live stdout/stderr logs from a specific Docker container."""
    if not container_name:
        return "Error: container_name is required"
    code, out, err = _run_docker(["logs", "--tail", str(tail), container_name])
    return out if out else (err or "No logs available.")


def restart_container(container_name: str):
    """Restart a running or stopped Docker container."""
    if not container_name:
        return "Error: container_name is required"
    code, out, err = _run_docker(["restart", container_name])
    if code == 0:
        return f"Successfully restarted container '{container_name}'."
    return f"Failed to restart '{container_name}': {err}"


def start_container(container_name: str):
    """Start a stopped Docker container."""
    if not container_name:
        return "Error: container_name is required"
    code, out, err = _run_docker(["start", container_name])
    if code == 0:
        return f"Successfully started container '{container_name}'."
    return f"Failed to start '{container_name}': {err}"


def stop_container(container_name: str, timeout: int = 10):
    """Stop a running Docker container."""
    if not container_name:
        return "Error: container_name is required"
    code, out, err = _run_docker(["stop", "-t", str(timeout), container_name])
    if code == 0:
        return f"Successfully stopped container '{container_name}'."
    return f"Failed to stop '{container_name}': {err}"


def inspect_container(container_name: str):
    """Retrieve detailed JSON inspection metadata for a container."""
    if not container_name:
        return "Error: container_name is required"
    code, out, err = _run_docker(["inspect", container_name])
    if code == 0:
        try:
            return json.loads(out)
        except Exception:
            return out
    return err


def list_images():
    """List all Docker images available locally on the host."""
    code, out, err = _run_docker(["images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"])
    return out if code == 0 else err


def prune_images(all: bool = False):
    """Remove unused, dangling, and unreferenced Docker images to reclaim disk space."""
    cmd = ["image", "prune", "-a", "-f"] if all else ["image", "prune", "-f"]
    code, out, err = _run_docker(cmd)
    return out if code == 0 else err


def get_docker_system_info():
    """Display host-wide Docker system information."""
    code, out, err = _run_docker(["info", "--format", "json"])
    if code == 0:
        try:
            return json.loads(out)
        except Exception:
            return out
    return err

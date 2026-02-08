"""CLI entry point."""

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

from gmccc.runner import DEFAULT_CONFIG_DIR, get_config, init, resolve_config_path, run_job, setup

PID_FILE = DEFAULT_CONFIG_DIR / ".scheduler.pid"
LOG_FILE = DEFAULT_CONFIG_DIR / "scheduler.log"


def _read_pid(pid_file: Path) -> int | None:
    if not pid_file.exists():
        return None
    pid = int(pid_file.read_text().strip())
    try:
        os.kill(pid, 0)
        return pid
    except OSError:
        pid_file.unlink()
        return None


def cmd_start(config_path: Path | None):
    """Start scheduler daemon."""
    if _read_pid(PID_FILE):
        print(f"Scheduler already running (PID: {PID_FILE.read_text().strip()})")
        return

    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "gmccc.scheduler"]
    if config_path:
        cmd += ["-c", str(config_path)]

    with open(LOG_FILE, "w") as lf:
        proc = subprocess.Popen(
            cmd, stdout=lf, stderr=subprocess.STDOUT, start_new_session=True
        )

    PID_FILE.write_text(str(proc.pid))
    print(f"Scheduler started (PID: {proc.pid})")
    print("Logs: gmccc logs")


def cmd_stop(config_path: Path | None):
    """Stop scheduler daemon."""
    pid = _read_pid(PID_FILE)

    if not pid:
        print("Scheduler not running")
        return

    os.kill(pid, signal.SIGTERM)
    PID_FILE.unlink(missing_ok=True)
    print("Scheduler stopped")


def cmd_status(config_path: Path | None):
    """Check scheduler status, jobs, and logs path."""
    pid = _read_pid(PID_FILE)

    if pid:
        print(f"Scheduler: running (PID: {pid})")
    else:
        print("Scheduler: not running")

    config_file = resolve_config_path(config_path)
    print(f"Config: {config_file}")
    logs_dir = config_file.parent / "logs"
    print(f"Logs: {logs_dir}")

    if config_file.exists():
        config = get_config(config_path)
        print(f"\nJobs ({len(config.jobs)}):")
        for j in config.jobs:
            status = "enabled" if j.enabled else "disabled"
            print(f"  - {j.name} /{j.skill} ({status}) {j.schedule.cron}")


def cmd_logs(config_path: Path | None):
    """Show scheduler daemon log."""
    if not LOG_FILE.exists():
        print("No log file found. Start scheduler first: gmccc start")
        return

    print(f"Log: {LOG_FILE}\n")
    print(LOG_FILE.read_text())


def main():
    parser = argparse.ArgumentParser(description="gmccc - Claude workflow automation")
    aliases = {"i": "install", "r": "run", "c": "config", "l": "list", "t": "test"}
    parser.add_argument(
        "command",
        nargs="?",
        choices=["install", "run", "config", "list", "test", "start", "stop", "status", "logs"],
        help="Commands (i = install, r = run, c = config, l = list, t = test)",
    )
    parser.add_argument("name", nargs="?", help="Argument for run/config commands")

    # Resolve aliases before parsing
    raw = sys.argv[1:]
    if raw and raw[0] in aliases:
        raw[0] = aliases[raw[0]]
    args = parser.parse_args(raw)

    config_path = Path(args.name) if args.name and args.command == "config" else None

    if args.command == "config":
        init(config_path)
        return

    if args.command and args.command not in ("run", "list", "test"):
        cmds = {
            "install": lambda c: setup(c),
            "start": cmd_start,
            "stop": cmd_stop,
            "status": cmd_status,
            "logs": cmd_logs,
        }
        cmds[args.command](config_path)
        return

    dry_run = args.command == "test"
    config = get_config(config_path)
    config_dir = resolve_config_path(config_path).parent
    logs_dir = config_dir / "logs"
    jobs = config.jobs

    if args.command == "list":
        print("Available jobs:")
        for j in jobs:
            status = "enabled" if j.enabled else "disabled"
            print(f"- {j.name} /{j.skill} ({status}) {j.schedule.cron}")
        return

    if args.command == "run":
        if not args.name:
            print("Usage: gmccc run <name>")
            sys.exit(1)
        jobs = [j for j in jobs if j.name == args.name]
        if not jobs:
            print(f"Job '{args.name}' not found.")
            sys.exit(1)

    for job in jobs:
        run_job(job, email=config.email, logs_dir=logs_dir, dry_run=dry_run)

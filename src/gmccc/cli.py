"""CLI entry point."""

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

from gmccc.runner import get_config, init, resolve_config_path, run_job, setup


def _pid_file(config_dir: Path) -> Path:
    return config_dir / ".scheduler.pid"


def _log_file(config_dir: Path) -> Path:
    return config_dir / "scheduler.log"


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
    config_dir = resolve_config_path(config_path).parent
    pid_file = _pid_file(config_dir)
    log_file = _log_file(config_dir)

    if _read_pid(pid_file):
        print(f"Scheduler already running (PID: {pid_file.read_text().strip()})")
        return

    cmd = [sys.executable, "-m", "gmccc.scheduler"]
    if config_path:
        cmd += ["-c", str(config_path)]

    with open(log_file, "w") as lf:
        proc = subprocess.Popen(
            cmd, stdout=lf, stderr=subprocess.STDOUT, start_new_session=True
        )

    pid_file.write_text(str(proc.pid))
    print(f"Scheduler started (PID: {proc.pid})")
    print("Logs: gmccc logs")


def cmd_stop(config_path: Path | None):
    """Stop scheduler daemon."""
    config_dir = resolve_config_path(config_path).parent
    pid_file = _pid_file(config_dir)
    pid = _read_pid(pid_file)

    if not pid:
        print("Scheduler not running")
        return

    os.kill(pid, signal.SIGTERM)
    pid_file.unlink(missing_ok=True)
    print("Scheduler stopped")


def cmd_status(config_path: Path | None):
    """Check scheduler status."""
    config_dir = resolve_config_path(config_path).parent
    pid = _read_pid(_pid_file(config_dir))

    if pid:
        print(f"Scheduler running (PID: {pid})")
    else:
        print("Scheduler not running")


def cmd_logs(config_path: Path | None):
    """Tail scheduler logs."""
    config_dir = resolve_config_path(config_path).parent
    log_file = _log_file(config_dir)

    if not log_file.exists():
        print("No log file found")
        return

    subprocess.run(["tail", "-f", str(log_file)])


def main():
    parser = argparse.ArgumentParser(description="gmccc - Claude workflow automation")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["start", "stop", "status", "logs"],
        help="Scheduler daemon commands",
    )
    parser.add_argument("-c", "--config", type=Path, help="Path to jobs config file")
    parser.add_argument("-p", "--project", help="Run specific job by name")
    parser.add_argument("-l", "--list", action="store_true", help="List available jobs")
    parser.add_argument(
        "--setup", action="store_true", help="Install skills via openskills"
    )
    parser.add_argument(
        "--init", action="store_true", help="Create default config file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without running commands",
    )
    args = parser.parse_args()

    if args.command:
        {"start": cmd_start, "stop": cmd_stop, "status": cmd_status, "logs": cmd_logs}[
            args.command
        ](args.config)
        return

    if args.init:
        init(args.config)
        return

    if args.setup:
        setup(args.config)
        return

    config = get_config(args.config)
    config_dir = resolve_config_path(args.config).parent
    logs_dir = config_dir / "logs"
    jobs = config.jobs

    if args.list:
        print("Available jobs:")
        for j in jobs:
            status = "enabled" if j.enabled else "disabled"
            print(f"- {j.name} /{j.skill} ({status}) {j.schedule.cron}")
        return

    if args.project:
        jobs = [j for j in jobs if j.name == args.project]
        if not jobs:
            print(f"Job '{args.project}' not found.")
            sys.exit(1)

    for job in jobs:
        run_job(job, email=config.email, logs_dir=logs_dir, dry_run=args.dry_run)

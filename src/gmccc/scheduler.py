"""Run skills with APScheduler based on config schedules."""

import argparse
import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from gmccc.models import EmailConfig, JobConfig
from gmccc.runner import get_config, resolve_config_path, run_job

sys.stdout.reconfigure(line_buffering=True)

# Suppress verbose APScheduler default logging
logging.getLogger("apscheduler").setLevel(logging.WARNING)


def _log(name: str, msg: str):
    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{name}] {msg}")


def run_job_n_times(config: JobConfig, email: EmailConfig | None, logs_dir: Path):
    """Run a job N times based on schedule.times config."""
    times = config.schedule.times
    name = config.name

    _log(name, "Job triggered")

    try:
        for i in range(times):
            _log(name, f"Running {i + 1}/{times}")
            run_job(config, email=email, logs_dir=logs_dir)
            _log(name, f"Completed {i + 1}/{times}")
        _log(name, "Job finished")
    except Exception as e:
        _log(name, f"Job failed: {e}")
        traceback.print_exc()


def job_executed_listener(event):
    _log(event.job_id, "Done")


def job_error_listener(event):
    _log(event.job_id, f"Error: {event.exception}")


def job_missed_listener(event):
    _log(event.job_id, "Skipped (previous run still active)")


def main():
    parser = argparse.ArgumentParser(description="gmccc scheduler")
    parser.add_argument("-c", "--config", type=Path, help="Path to jobs config file")
    args = parser.parse_args()

    config = get_config(args.config)
    config_dir = resolve_config_path(args.config).parent
    logs_dir = config_dir / "logs"

    scheduler = BlockingScheduler()
    local_tz = datetime.now().astimezone().tzinfo

    scheduler.add_listener(job_executed_listener, EVENT_JOB_EXECUTED)
    scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)
    scheduler.add_listener(job_missed_listener, EVENT_JOB_MISSED)

    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"gmccc scheduler | {ts}")
    print()

    for job in config.jobs:
        if not job.enabled:
            continue

        cron = job.schedule.cron
        trigger = CronTrigger.from_crontab(cron, timezone=local_tz)
        timeout = job.schedule.timeout
        scheduler.add_job(
            run_job_n_times,
            trigger,
            args=[job, config.email, logs_dir],
            id=job.name,
            name=f"Run {job.name}",
            max_instances=1,
            misfire_grace_time=60,
        )
        next_run = trigger.get_next_fire_time(None, datetime.now(local_tz))
        next_str = next_run.strftime("%Y-%m-%d %H:%M") if next_run else "N/A"
        print(f"  {job.name:<16} cron={cron:<20} next={next_str}  timeout={timeout}s  x{job.schedule.times}")

    if not scheduler.get_jobs():
        print("\nNo scheduled jobs. Exiting.")
        return

    print()
    _log("scheduler", "Waiting for jobs...")
    scheduler.start()


if __name__ == "__main__":
    main()

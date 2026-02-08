"""Run skills with APScheduler based on config schedules."""

import argparse
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


def run_job_n_times(config: JobConfig, email: EmailConfig | None, logs_dir: Path):
    """Run a job N times based on schedule.times config."""
    times = config.schedule.times
    name = config.name

    print(f"[{datetime.now().astimezone()}] [{name}] Job triggered")

    try:
        for i in range(times):
            print(f"[{datetime.now().astimezone()}] [{name}] Running {i + 1}/{times}")
            run_job(config, email=email, logs_dir=logs_dir)
            print(f"[{datetime.now().astimezone()}] [{name}] Completed {i + 1}/{times}")
        print(f"[{datetime.now().astimezone()}] [{name}] Job finished successfully")
    except Exception as e:
        print(f"[{datetime.now().astimezone()}] [{name}] Job failed: {e}")
        traceback.print_exc()


def job_executed_listener(event):
    """Log when a job executes successfully."""
    print(f"[{datetime.now().astimezone()}] APScheduler: Job '{event.job_id}' executed")


def job_error_listener(event):
    """Log when a job encounters an error."""
    print(
        f"[{datetime.now().astimezone()}] APScheduler: Job '{event.job_id}' raised exception: {event.exception}"
    )


def job_missed_listener(event):
    """Log when a job is missed."""
    print(
        f"[{datetime.now().astimezone()}] APScheduler: Job '{event.job_id}' missed its scheduled time"
    )


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

    print(f"Current local time: {datetime.now().astimezone()}")
    print(f"Timezone: {local_tz}")
    print("-" * 50)

    for job in config.jobs:
        if not job.enabled:
            continue

        cron = job.schedule.cron
        trigger = CronTrigger.from_crontab(cron, timezone=local_tz)
        scheduler.add_job(
            run_job_n_times,
            trigger,
            args=[job, config.email, logs_dir],
            id=job.name,
            name=f"Run {job.name}",
            max_instances=1,
        )
        next_run = trigger.get_next_fire_time(None, datetime.now(local_tz))
        print(f"Scheduled: {job.name}")
        print(f"  Cron: '{cron}', Times: {job.schedule.times}")
        print(f"  Next run: {next_run}")

    if not scheduler.get_jobs():
        print("No scheduled jobs found. Exiting.")
        return

    print("-" * 50)
    print(f"[{datetime.now().astimezone()}] Scheduler started. Waiting for jobs...")
    scheduler.start()


if __name__ == "__main__":
    main()

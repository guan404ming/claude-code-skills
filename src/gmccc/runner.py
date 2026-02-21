"""Job runner - load config and execute skills via openskills."""

import json
import shutil
import smtplib
import subprocess
import threading
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

from gmccc.models import Config, EmailConfig, JobConfig

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "gmccc"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "jobs.json"

EXAMPLE_CONFIG = {
    "skills_repo": "guan404ming/claude-code-skills",
    "email": {
        "to": "guanmingchiu@gmail.com",
        "smtp_user": "xxx@gmail.com",
        "smtp_password": "",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
    },
    "jobs": [
        {
            "name": "example",
            "skill": "dev-autodev",
            "path": "/path/to/your/project",
            "enabled": False,
            "schedule": {"cron": "0 4 * * *", "times": 1},
        }
    ],
}

CMD = [
    "claude",
    "-p",
    "{prompt}",
    "--dangerously-skip-permissions",
    "--model",
    "claude-opus-4-6",
]


def resolve_config_path(config_path: Path | None = None) -> Path:
    """Resolve config file path."""
    if config_path:
        return Path(config_path).expanduser().resolve()
    return DEFAULT_CONFIG_FILE


def get_config(config_path: Path | None = None) -> Config:
    """Load config from jobs.json."""
    path = resolve_config_path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}\n"
            f"Run 'gmccc config' to create a default config."
        )
    data = json.loads(path.read_text())
    return Config(**data)


def get_jobs(config_path: Path | None = None) -> list[JobConfig]:
    """Get all job configs."""
    return get_config(config_path).jobs


def init(config_path: Path | None = None):
    """Create default config file."""
    path = resolve_config_path(config_path)
    if path.exists():
        print(f"Config already exists: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(EXAMPLE_CONFIG, indent=2) + "\n")
    print(f"Created: {path}")
    print("Edit this file to configure your jobs.")


def setup(config_path: Path | None = None):
    """Install skills globally via openskills."""
    config = get_config(config_path)
    cmd = ["npx", "openskills", "install", config.skills_repo, "--global", "-y"]
    print(f"Installing skills from {config.skills_repo}...")
    subprocess.run(cmd, check=True)
    print("Skills installed.")


def uninstall():
    """Remove skills and config."""
    skills_dir = Path.home() / ".claude" / "skills"
    if skills_dir.exists():
        shutil.rmtree(skills_dir)
        print(f"Removed {skills_dir}")
    else:
        print("No skills found")

    if DEFAULT_CONFIG_DIR.exists():
        shutil.rmtree(DEFAULT_CONFIG_DIR)
        print(f"Removed {DEFAULT_CONFIG_DIR}")
    else:
        print("No config found")

    print("Done.")


def send_email(email: EmailConfig, subject: str, body: str):
    """Send email via Gmail SMTP."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email.smtp_user
    msg["To"] = email.to
    with smtplib.SMTP(email.smtp_host, email.smtp_port) as server:
        server.starttls()
        server.login(email.smtp_user, email.smtp_password)
        server.send_message(msg)
    print(f"Email sent to {email.to}")


def run_job(
    config: JobConfig,
    email: EmailConfig | None = None,
    logs_dir: Path | None = None,
    dry_run: bool = False,
):
    """Run a skill in the target path."""
    if not config.enabled and not dry_run:
        return

    target = Path(config.path)
    prompt = f"/{config.skill}"
    if config.prompt:
        prompt = f"{prompt}\n\n{config.prompt}"
    cmd = [arg.replace("{prompt}", prompt) for arg in CMD]

    if dry_run:
        msg = f"[DRY RUN] Would run {prompt} in {target}\n  {' '.join(cmd)}"
        print(msg)
        if logs_dir is None:
            logs_dir = DEFAULT_CONFIG_DIR / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / f"{config.name}_test.log"
        log_file.write_text(msg + "\n")
        print(f"Log: {log_file}")
        if email and email.smtp_user and email.smtp_password:
            send_email(
                email,
                subject=f"[gmccc] {config.name} test",
                body=f"Job: {config.name}\nSkill: /{config.skill}\nStatus: test",
            )
        return

    if not target.exists():
        print(f"Path not found: {target}")
        return

    if logs_dir is None:
        logs_dir = DEFAULT_CONFIG_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{config.name}_{timestamp}.log"
    timeout = config.schedule.timeout

    print(f"Running {config.name} (/{config.skill})")
    print(f"Log: {log_file}")

    status = "completed"
    try:
        with open(log_file, "w") as lf:
            proc = subprocess.Popen(
                cmd, cwd=target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )

            def _stream():
                for line in proc.stdout:
                    print(line, end="")
                    lf.write(line)
                    lf.flush()

            reader = threading.Thread(target=_stream, daemon=True)
            reader.start()

            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                lf.write(f"\n[gmccc] Killed after {timeout}s timeout\n")
                status = f"timeout ({timeout}s)"
                print(f"Killed after {timeout}s timeout")

            reader.join(timeout=5)

        if status == "completed" and proc.returncode != 0:
            status = f"failed (exit {proc.returncode})"

        # Copy log to working directory
        local_log = target / f"{config.name}.log"
        shutil.copy2(log_file, local_log)
        print(f"Done ({status})")

    except Exception as e:
        status = f"error: {e}"
        print(f"Error: {e}")

    if email and email.smtp_user and email.smtp_password:
        log_content = log_file.read_text() if log_file.exists() else "(no log)"
        send_email(
            email,
            subject=f"[gmccc] {config.name} {status}",
            body=f"Job: {config.name}\nSkill: /{config.skill}\nStatus: {status}\n\n--- Log ---\n{log_content}",
        )

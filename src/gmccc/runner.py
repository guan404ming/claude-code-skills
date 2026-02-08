"""Job runner - load config and execute skills via openskills."""

import json
import os
import smtplib
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

from gmccc.models import Config, EmailConfig, JobConfig

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "gmccc"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "jobs.json"

EXAMPLE_CONFIG = {
    "skills_repo": "guan404ming/claude-code-skills",
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


def _load_env(config_dir: Path):
    """Load .env file into os.environ."""
    env_file = config_dir / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def get_config(config_path: Path | None = None) -> Config:
    """Load config, with smtp_password from .env next to config file."""
    path = resolve_config_path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}\n"
            f"Run 'gmccc --init' to create a default config."
        )
    _load_env(path.parent)
    data = json.loads(path.read_text())
    config = Config(**data)
    if config.email:
        config.email.smtp_user = os.environ.get("SMTP_USER", config.email.smtp_user)
        config.email.smtp_password = os.environ.get(
            "SMTP_PASSWORD", config.email.smtp_password
        )
    return config


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
    if not config.enabled:
        return

    target = Path(config.path)
    prompt = f"/{config.skill}"
    if config.prompt:
        prompt = f"{prompt}\n\n{config.prompt}"
    cmd = [arg.replace("{prompt}", prompt) for arg in CMD]

    if dry_run:
        print(f"[DRY RUN] Would run {prompt} in {target}")
        print(f"  {' '.join(cmd)}")
        return

    if not target.exists():
        print(f"Path not found: {target}")
        return

    if logs_dir is None:
        logs_dir = DEFAULT_CONFIG_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{config.name}_{timestamp}.log"

    print(f"Running {config.name} (/{config.skill})")
    print(f"Log: {log_file}")

    with open(log_file, "w") as lf:
        proc = subprocess.Popen(
            cmd, cwd=target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in proc.stdout:
            print(line, end="")
            lf.write(line)
            lf.flush()
        proc.wait()

    print(f"Done (exit {proc.returncode})")

    if email and email.smtp_user and email.smtp_password:
        status = (
            "completed" if proc.returncode == 0 else f"failed (exit {proc.returncode})"
        )
        log_content = log_file.read_text()
        send_email(
            email,
            subject=f"[gmccc] {config.name} {status}",
            body=f"Job: {config.name}\nSkill: /{config.skill}\nStatus: {status}\n\n--- Log ---\n{log_content}",
        )

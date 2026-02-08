"""Pydantic models for configuration."""

from pydantic import BaseModel


class ScheduleConfig(BaseModel):
    """Schedule configuration."""

    cron: str
    times: int = 1


class JobConfig(BaseModel):
    """Job configuration."""

    name: str
    skill: str
    path: str
    prompt: str = ""
    enabled: bool = False
    schedule: ScheduleConfig

    model_config = {"extra": "forbid"}


class EmailConfig(BaseModel):
    """Gmail SMTP configuration."""

    to: str
    smtp_user: str = "guanmingchiu@gmail.com"
    smtp_password: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587


class Config(BaseModel):
    """Top-level configuration."""

    skills_repo: str = "guan404ming/claude-code-skills"
    email: EmailConfig | None = None
    jobs: list[JobConfig]

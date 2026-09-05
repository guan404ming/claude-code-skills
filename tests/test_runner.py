import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import gmccc.runner as runner
from gmccc.runner import _install_repo_skills


def make_skill(parent: Path, name: str, source: str) -> Path:
    skill_dir = parent / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(f"# {name}\n")
    (skill_dir / ".openskills.json").write_text(
        json.dumps({"source": source, "installedAt": "2026-01-01T00:00:00Z"})
    )
    return skill_dir


class InstallTest(unittest.TestCase):
    def test_setup_installs_both_agent_targets_without_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            targets = {
                "claude": root / ".claude/skills",
                "codex": root / ".agents/skills",
            }

            def install(cmd, check):
                self.assertTrue(check)
                self.assertIn("--yes", cmd)
                self.assertIn("--global", cmd)
                make_skill(
                    targets["claude"],
                    "new",
                    runner.DEFAULT_SKILLS_REPO,
                )

            with (
                patch.dict(runner.SKILLS_DIRS, targets, clear=True),
                patch.object(runner.subprocess, "run", side_effect=install),
                redirect_stdout(io.StringIO()),
            ):
                runner.setup(root / "missing.json")

            self.assertTrue((targets["claude"] / "new/SKILL.md").exists())
            self.assertTrue((targets["codex"] / "new/SKILL.md").exists())

    def test_installs_repo_skills_and_preserves_other_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            target = root / "target"
            make_skill(source, "new", "owner/repo")
            make_skill(target, "stale", "owner/repo")
            make_skill(target, "other", "other/repo")

            count = _install_repo_skills(source, target, "owner/repo")

            self.assertEqual(count, 1)
            self.assertTrue((target / "new" / "SKILL.md").exists())
            self.assertFalse((target / "stale").exists())
            self.assertTrue((target / "other" / "SKILL.md").exists())

    def test_stops_on_name_conflict_before_removing_skills(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            target = root / "target"
            make_skill(source, "same", "owner/repo")
            make_skill(target, "same", "other/repo")
            make_skill(target, "stale", "owner/repo")

            with self.assertRaises(FileExistsError):
                _install_repo_skills(source, target, "owner/repo")

            self.assertTrue((target / "same").exists())
            self.assertTrue((target / "stale").exists())

    def test_uninstall_removes_only_managed_skills(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / ".config/gmccc"
            config_file = config_dir / "jobs.json"
            config_dir.mkdir(parents=True)
            config_file.write_text("{}")
            targets = {
                "claude": root / ".claude/skills",
                "codex": root / ".agents/skills",
            }
            for target in targets.values():
                make_skill(target, "managed", runner.DEFAULT_SKILLS_REPO)
                make_skill(target, "other", "other/repo")

            with (
                patch.dict(runner.SKILLS_DIRS, targets, clear=True),
                patch.object(runner, "DEFAULT_CONFIG_DIR", config_dir),
                patch.object(runner, "DEFAULT_CONFIG_FILE", root / "missing.json"),
                redirect_stdout(io.StringIO()),
            ):
                runner.uninstall()

            for target in targets.values():
                self.assertFalse((target / "managed").exists())
                self.assertTrue((target / "other/SKILL.md").exists())
            self.assertFalse(config_dir.exists())


if __name__ == "__main__":
    unittest.main()

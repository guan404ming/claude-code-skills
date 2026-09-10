#!/usr/bin/env node

const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const REPO = "guan404ming/gmccc";
const CLAUDE_MD_URL = `https://raw.githubusercontent.com/${REPO}/main/CLAUDE.md`;
const RULES_FILES = [
  path.join(os.homedir(), ".claude", "CLAUDE.md"),
  path.join(os.homedir(), ".codex", "AGENTS.md"),
];
const TARGETS = [
  {
    name: "Claude Code",
    skillsDir: path.join(os.homedir(), ".claude", "skills"),
  },
  {
    name: "Codex",
    skillsDir: path.join(os.homedir(), ".agents", "skills"),
  },
];

const skillSource = (skillDir) => {
  try {
    const metadata = path.join(skillDir, ".openskills.json");
    return JSON.parse(fs.readFileSync(metadata, "utf8")).source;
  } catch {
    return undefined;
  }
};

const repoSkills = (skillsDir) => {
  if (!fs.existsSync(skillsDir)) return [];
  return fs
    .readdirSync(skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(skillsDir, entry.name))
    .filter((skillDir) => skillSource(skillDir) === REPO)
    .sort();
};

const prune = (since) => {
  for (const skillDir of repoSkills(TARGETS[0].skillsDir)) {
    const metadata = path.join(skillDir, ".openskills.json");
    const { installedAt } = JSON.parse(fs.readFileSync(metadata, "utf8"));
    if (new Date(installedAt) < since) {
      fs.rmSync(skillDir, { recursive: true });
      console.log(`Pruned: ${path.basename(skillDir)}`);
    }
  }
};

const assertNoConflicts = (skills, targetDir) => {
  const conflicts = skills
    .map((skillDir) => path.join(targetDir, path.basename(skillDir)))
    .filter(
      (skillDir) =>
        fs.existsSync(skillDir) && skillSource(skillDir) !== REPO,
    );
  if (conflicts.length) {
    const names = conflicts.map((skillDir) => path.basename(skillDir));
    throw new Error(
      `Skills already installed from another source: ${names.join(", ")}`,
    );
  }
};

const installSkills = (skills, targetDir) => {
  fs.mkdirSync(targetDir, { recursive: true });
  for (const skillDir of repoSkills(targetDir)) {
    fs.rmSync(skillDir, { recursive: true });
  }
  for (const skillDir of skills) {
    fs.cpSync(skillDir, path.join(targetDir, path.basename(skillDir)), {
      recursive: true,
    });
  }
};

const removeSkills = (targetDir) => {
  const skills = repoSkills(targetDir);
  for (const skillDir of skills) {
    fs.rmSync(skillDir, { recursive: true });
  }
  return skills.length;
};

const commands = {
  install: () => {
    const start = new Date();
    console.log("Installing skills...");
    execFileSync(
      "npx",
      ["--yes", "openskills", "install", REPO, "--global", "-y"],
      { stdio: "inherit" },
    );
    prune(start);
    const skills = repoSkills(TARGETS[0].skillsDir);
    if (!skills.length) throw new Error(`No skills found for ${REPO}`);
    assertNoConflicts(skills, TARGETS[1].skillsDir);
    installSkills(skills, TARGETS[1].skillsDir);
    console.log(
      `Installed ${skills.length} Codex skills in ${TARGETS[1].skillsDir}`,
    );
    console.log("Installing global rules...");
    for (const rulesFile of RULES_FILES) {
      fs.mkdirSync(path.dirname(rulesFile), { recursive: true });
      execFileSync("curl", ["-fsSL", "-o", rulesFile, CLAUDE_MD_URL]);
    }
    console.log("Done!");
  },
  uninstall: () => {
    for (const target of TARGETS) {
      const count = removeSkills(target.skillsDir);
      console.log(`Removed ${count} ${target.name} skills`);
    }
    for (const rulesFile of RULES_FILES) {
      fs.rmSync(rulesFile, { force: true });
    }
    console.log("Done!");
  },
};

const aliases = { i: "install", u: "uninstall" };
const cmd = aliases[process.argv[2]] || process.argv[2];
if (!cmd || cmd === "-h" || cmd === "--help" || !commands[cmd]) {
  console.log("Usage: gmccc <install|uninstall> (i, u)");
  process.exit(0);
}

commands[cmd]();

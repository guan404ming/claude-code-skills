#!/usr/bin/env node

const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const REPO = "guan404ming/gmccc";
const RAW_URL = `https://raw.githubusercontent.com/${REPO}/main`;
const CLAUDE_MD_URL = `${RAW_URL}/CLAUDE.md`;
const CLAUDE_DIR = path.join(os.homedir(), ".claude");
const SETTINGS_FILE = path.join(CLAUDE_DIR, "settings.json");
const HOOKS_DIR = path.join(CLAUDE_DIR, "hooks");
const HOOK_SCRIPTS = ["use-tgrep.sh", "tgrep-serve.sh"];
const TGREP_PERMISSION = "Bash(tgrep:*)";
const TGREP_HOOKS = {
  SessionStart: {
    matcher: "*",
    hooks: [
      {
        type: "command",
        command: `bash "${path.join(HOOKS_DIR, "tgrep-serve.sh")}"`,
        timeout: 10,
      },
    ],
  },
  PreToolUse: {
    matcher: "Grep",
    hooks: [
      {
        type: "command",
        command: `bash "${path.join(HOOKS_DIR, "use-tgrep.sh")}"`,
      },
    ],
  },
};
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

const readSettings = () => {
  try {
    return JSON.parse(fs.readFileSync(SETTINGS_FILE, "utf8"));
  } catch {
    return {};
  }
};

const writeSettings = (settings) => {
  fs.mkdirSync(CLAUDE_DIR, { recursive: true });
  fs.writeFileSync(SETTINGS_FILE, JSON.stringify(settings, null, 2) + "\n");
};

const isTgrepHook = (entry) =>
  entry.hooks?.some((hook) => hook.command?.includes("tgrep"));

const removeTgrepSettings = (settings) => {
  for (const event of Object.keys(TGREP_HOOKS)) {
    const entries = (settings.hooks?.[event] ?? []).filter(
      (entry) => !isTgrepHook(entry),
    );
    if (entries.length) settings.hooks[event] = entries;
    else if (settings.hooks) delete settings.hooks[event];
  }
  const allow = (settings.permissions?.allow ?? []).filter(
    (rule) => rule !== TGREP_PERMISSION,
  );
  if (settings.permissions) settings.permissions.allow = allow;
  return settings;
};

const installTgrep = () => {
  fs.mkdirSync(HOOKS_DIR, { recursive: true });
  for (const script of HOOK_SCRIPTS) {
    const target = path.join(HOOKS_DIR, script);
    execFileSync("curl", ["-fsSL", "-o", target, `${RAW_URL}/hooks/${script}`]);
    fs.chmodSync(target, 0o755);
  }
  const settings = removeTgrepSettings(readSettings());
  settings.hooks ??= {};
  for (const [event, entry] of Object.entries(TGREP_HOOKS)) {
    settings.hooks[event] = [...(settings.hooks[event] ?? []), entry];
  }
  settings.permissions ??= {};
  settings.permissions.allow = [
    ...(settings.permissions.allow ?? []),
    TGREP_PERMISSION,
  ];
  writeSettings(settings);
  try {
    execFileSync("tgrep", ["--version"], { stdio: "ignore" });
  } catch {
    console.warn("tgrep not found. Install it: brew install tgrep");
  }
};

const uninstallTgrep = () => {
  for (const script of HOOK_SCRIPTS) {
    fs.rmSync(path.join(HOOKS_DIR, script), { force: true });
  }
  if (fs.existsSync(SETTINGS_FILE)) {
    writeSettings(removeTgrepSettings(readSettings()));
  }
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
    console.log("Installing tgrep hooks...");
    installTgrep();
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
    uninstallTgrep();
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

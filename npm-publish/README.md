# windows-software-installer-skill

> 🛡️ Safer Windows software installer for AI agents and humans.

[![platform](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/BingWuJ/windows-software-installer)
[![type](https://img.shields.io/badge/type-Agent%20Skill-purple)](https://github.com/BingWuJ/windows-software-installer)
[![license](https://img.shields.io/badge/license-MIT-green)](https://github.com/BingWuJ/windows-software-installer)

One-line installer that sets up the **Windows Software Installer Skill** for [Pi](https://pi.dev) and [Claude Code](https://claude.ai/code).

## Quick Install

```bash
npx windows-software-installer-skill
```

This auto-detects your agent environment and installs the skill to:
- `~/.agents/skills/windows-software-installer` (Pi)
- `~/.claude/skills/windows-software-installer` (Claude Code, via junction)

## Usage

After installation, your agent understands:

```
/INSTALL vscode                          # Scoop install
/INSTALL D:\Downloads\setup.exe          # Local installer
/INSTALL https://example.com/app.exe     # Download + verify
```

## What it does

- **Scoop mode** — install from Scoop buckets (safest)
- **Local file mode** — install a trusted `.exe` / `.msi` you already have
- **Verified download mode** — download over HTTPS, verify SHA256 or Authenticode signature

Default install path: `D:\iStall\{software_name}` (keeps C: clean).

## For other agents or manual use

See the [full documentation on GitHub](https://github.com/BingWuJ/windows-software-installer).

```bash
git clone https://github.com/BingWuJ/windows-software-installer.git
```

## Requirements

- Windows 10/11
- Node.js ≥ 16 (for this installer)
- Python 3.8+ (for the installation script itself)

## License

MIT © [BingWuJ](https://github.com/BingWuJ)

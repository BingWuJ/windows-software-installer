<p align="center">
  <strong>Windows Software Installer Skill</strong>
</p>

<p align="center">
  <em>Safer Windows software installation for AI agents and humans.<br/>
  Scoop, local installer, or verified download — one command, zero guesswork.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%20Only-0078D4?logo=windows11" alt="Windows Only" />
  <img src="https://img.shields.io/badge/type-Agent%20Skill-8B5CF6" alt="Agent Skill" />
  <img src="https://img.shields.io/npm/v/windows-software-installer-skill?style=flat-square&color=CB3837&logo=npm" alt="npm" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
</p>

---

## Quick Start

### For AI Agents

Install the skill once, then use `/INSTALL` in any supported agent:

```bash
npx windows-software-installer-skill
```

Supported agents: **Pi**, **Claude Code**.  
*(The installer auto-detects your agent environment and places the skill files in the correct directory.)*

After installation, your agent understands commands like:

```
/INSTALL vscode                              # Scoop install
/INSTALL D:\Downloads\setup.exe              # Local installer
/INSTALL https://example.com/app.exe         # Download + verify
```

### For Humans

If you just want to install software directly without an AI agent:

```bash
# 1. Clone the repository
git clone https://github.com/BingWuJ/windows-software-installer.git
cd windows-software-installer

# 2. Run the installer directly (Python 3.8+ required)
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name vscode
```

Or install it as a skill for your agent:

```bash
npx windows-software-installer-skill
```

---

## What is this?

**Windows Software Installer Skill** is a safety-first tool for installing Windows software through three explicit, controlled modes:

| Mode | When to use | Safety |
|:---|:---|:---|
| **Scoop** | Package exists in Scoop | ✅ Highest — managed by Scoop |
| **Local file** | You already have a trusted `.exe` / `.msi` | ✅ Trusted — you vetted the source |
| **Verified download** | Need to download from vendor URL | ✅ Verified — SHA256 or Authenticode |

It is designed primarily as an **AI Agent Skill** (for Pi, Claude Code, and similar agents), but the underlying Python script works standalone for human users too.

Key design decisions:

- **D-drive first** — Default install path is `D:\iStall\{software_name}`, keeping C: clean.
- **No arbitrary installer arguments** — Prevents command injection and unexpected installer behavior.
- **No automatic fallback** — Each mode is explicit; the script never silently switches strategies.

---

## Usage Examples

### Scoop mode — safest path

```bash
/INSTALL neovim-nightly
```

Equivalent CLI:

```bash
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name neovim-nightly \
  --scoop-bucket nightly
```

### Local file mode — already downloaded

```bash
/INSTALL D:\Downloads\Typeless-0.4.6-x64-Setup.exe
```

Equivalent CLI:

```bash
python scripts/install_windows_software.py \
  --mode local-file \
  --software-name typeless \
  --local-file "D:\Downloads\Typeless-0.4.6-x64-Setup.exe" \
  --installer-type nsis
```

### Verified download mode — download + check

```bash
/INSTALL https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe
```

Equivalent CLI:

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name sumatrapdf \
  --download-url "https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe" \
  --installer-type nsis \
  --sha256 "<sha256>"
```

With CDN referer protection (for Chinese software CDNs):

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name shandianshuo \
  --download-url "https://download.shandianshuo.cn/windows/shandianshuo_0.6.7_x64-setup.exe" \
  --installer-type nsis \
  --referer "https://shandianshuo.cn/" \
  --allow-untrusted-publisher
```

Interactive mode (launch installer UI to manually uncheck bundled software):

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name wechat \
  --download-url "https://example.com/WeChatSetup.exe" \
  --installer-type nsis \
  --publisher Tencent \
  --interactive
```

---

## Security

| Measure | Scoop | Local file | Download verified |
|:---|:---:|:---:|:---:|
| HTTPS enforcement | — | — | ✅ |
| SHA256 verification | — | — | ✅ |
| Authenticode signature check | — | — | ✅ |
| Unknown publisher confirmation | — | — | ✅ |
| File type restriction (.exe / .msi) | — | ✅ | — |
| No free-form installer args | ✅ | ✅ | ✅ |
| Single-mode execution (no fallback) | ✅ | ✅ | ✅ |

---

## Requirements

- Windows 10/11
- Node.js ≥ 16 (for `npx` skill installation)
- Python 3.8+ (for standalone script execution)
- Scoop (for scoop mode)

---

## FAQ

**Q: How do I install this for Codex CLI or OpenCode?**

The `npx` installer currently auto-detects Pi and Claude Code environments. For other agents, install manually:

```bash
# Codex CLI
git clone https://github.com/BingWuJ/windows-software-installer ~/.codex/skills/windows-software-installer

# OpenCode
git clone https://github.com/BingWuJ/windows-software-installer ~/.config/opencode/skills/windows-software-installer
```

**Q: Why not just use winget?**

winget's `--location` flag is frequently ignored by the underlying installer, causing software to land on C: anyway. This skill only uses winget for *discovery* (finding package names and official URLs), never for installation.

**Q: What if the vendor doesn't provide a SHA256?**

Use `download-verified` mode with a valid digital signature. If the signer is valid but not in the allowlist, the script shows the publisher name and asks for confirmation.

**Q: Why can't I pass custom installer arguments?**

This is intentional. Free-form installer arguments can lead to command injection or behavior that doesn't match what the skill expects. The script handles all installer invocations internally.

**Q: How do I avoid bundled software?**

Add `--interactive`. The script pre-fills the install directory and launches the installer UI, letting you manually uncheck bundled offers. Recommended for Chinese consumer software (WeChat, Baidu, 360, etc.).

---

## Directory Structure

```
windows-software-installer/
├── SKILL.md                      # Skill definition (read by agents)
├── README.md                     # This file
├── scripts/
│   └── install_windows_software.py   # Core installation script
├── references/
│   ├── scoop-buckets.md          # Scoop bucket reference
│   └── installer-patterns.md     # Installer type documentation
├── evals/
│   └── evals.json                # Evaluation test cases
└── npm-publish/                  # npm package source
    ├── bin/cli.js                # npx installer script
    └── package.json
```

---

## License

[MIT](./LICENSE) © [BingWuJ](https://github.com/BingWuJ)

---

<p align="center">
  <a href="./README.zh.md">中文文档</a>
</p>

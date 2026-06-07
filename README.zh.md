<p align="center">
  <strong>Windows Software Installer Skill</strong>
</p>

<p align="center">
  <em>为 AI Agent 和人类提供安全的 Windows 软件安装方案。<br/>
  Scoop 安装、本地安装包、下载校验 — 一条命令，无需猜测。</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%20Only-0078D4?logo=windows11" alt="Windows Only" />
  <img src="https://img.shields.io/badge/type-Agent%20Skill-8B5CF6" alt="Agent Skill" />
  <img src="https://img.shields.io/npm/v/windows-software-installer-skill?style=flat-square&color=CB3837&logo=npm" alt="npm" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
</p>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh.md">简体中文</a>
</p>

---

## 快速开始

### 给 AI Agent 使用

安装一次 skill，然后在任意支持的 Agent 中使用 `/INSTALL`：

```bash
npx windows-software-installer-skill
```

已支持的 Agent：**Pi**、**Claude Code**。  
*（安装器会自动检测你的 Agent 环境，并将 skill 文件放入正确的目录。）*

安装完成后，你的 Agent 将理解如下命令：

```
/INSTALL vscode                              # Scoop 安装
/INSTALL D:\Downloads\setup.exe              # 本地安装包
/INSTALL https://example.com/app.exe         # 下载并校验
```

### 给人类直接使用

如果你不想通过 AI Agent，而是直接运行安装脚本：

```bash
# 1. 克隆仓库
git clone https://github.com/BingWuJ/windows-software-installer.git
cd windows-software-installer

# 2. 直接运行安装脚本（需要 Python 3.8+）
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name vscode
```

或者，你也可以将其作为 Agent 的 skill 安装：

```bash
npx windows-software-installer-skill
```

---

## 这是什么？

**Windows Software Installer Skill** 是一个安全优先的 Windows 软件安装工具，通过三种显式、受控的模式工作：

| 模式 | 何时使用 | 安全性 |
|:---|:---|:---|
| **Scoop** | 软件存在于 Scoop 仓库中 | ✅ 最高 — Scoop 管理安装 |
| **本地安装包** | 你已拥有可信的 `.exe` / `.msi` 文件 | ✅ 可信 — 来源由你审核 |
| **下载校验** | 需要从厂商 URL 下载安装包 | ✅ 已验证 — SHA256 或 Authenticode |

它的设计初衷是作为 **AI Agent Skill**（供 Pi、Claude Code 等 Agent 使用），但其底层的 Python 脚本也可以独立供人类用户运行。

核心设计理念：

- **D 盘优先** — 默认安装路径为 `D:\iStall\{software_name}`，避免 C 盘膨胀。
- **禁止任意安装器参数** — 防止命令注入和非预期的安装器行为。
- **无自动回退** — 每种模式都是显式的，脚本永远不会静默切换策略。

---

## 使用示例

### Scoop 模式 — 最安全

```bash
/INSTALL neovim-nightly
```

等价的 CLI 命令：

```bash
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name neovim-nightly \
  --scoop-bucket nightly
```

### 本地安装包模式 — 已有下载文件

```bash
/INSTALL D:\Downloads\Typeless-0.4.6-x64-Setup.exe
```

等价的 CLI 命令：

```bash
python scripts/install_windows_software.py \
  --mode local-file \
  --software-name typeless \
  --local-file "D:\Downloads\Typeless-0.4.6-x64-Setup.exe" \
  --installer-type nsis
```

### 下载校验模式 — 下载并验证

```bash
/INSTALL https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe
```

等价的 CLI 命令：

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name sumatrapdf \
  --download-url "https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe" \
  --installer-type nsis \
  --sha256 "<sha256>"
```

支持 CDN Referer 防盗链（适用于国内软件 CDN）：

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name shandianshuo \
  --download-url "https://download.shandianshuo.cn/windows/shandianshuo_0.6.7_x64-setup.exe" \
  --installer-type nsis \
  --referer "https://shandianshuo.cn/" \
  --allow-untrusted-publisher
```

交互模式（启动安装器 UI，手动取消勾选捆绑软件）：

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

## 安全机制

| 安全措施 | Scoop | 本地安装包 | 下载校验 |
|:---|:---:|:---:|:---:|
| HTTPS 强制 | — | — | ✅ |
| SHA256 校验 | — | — | ✅ |
| Authenticode 签名验证 | — | — | ✅ |
| 未知发布者确认 | — | — | ✅ |
| 文件类型限制（.exe / .msi） | — | ✅ | — |
| 禁止自由格式安装器参数 | ✅ | ✅ | ✅ |
| 单模式执行（不回退） | ✅ | ✅ | ✅ |

---

## 环境要求

- Windows 10/11
- Node.js ≥ 16（用于 `npx` skill 安装）
- Python 3.8+（用于独立运行脚本）
- Scoop（用于 scoop 模式）

---

## 常见问题

**Q: 如何在 Codex CLI 或 OpenCode 中安装？**

`npx` 安装器目前自动检测 Pi 和 Claude Code 环境。其他 Agent 请手动安装：

```bash
# Codex CLI
git clone https://github.com/BingWuJ/windows-software-installer ~/.codex/skills/windows-software-installer

# OpenCode
git clone https://github.com/BingWuJ/windows-software-installer ~/.config/opencode/skills/windows-software-installer
```

**Q: 为什么不直接用 winget 安装？**

winget 的 `--location` 参数经常被底层安装器忽略，导致软件仍然装到 C 盘。本 skill 仅将 winget 用于*发现*（查找包名和官方下载地址），从不用于实际安装。

**Q: 如果厂商没有提供 SHA256 怎么办？**

使用 `download-verified` 模式并配合有效的数字签名。如果签名者有效但不在白名单中，脚本会显示发布者名称并请求确认。

**Q: 为什么不能传入自定义安装器参数？**

这是有意设计的。自由格式的安装器参数可能导致命令注入或产生与 skill 预期不符的行为。脚本在内部统一处理所有安装器调用。

**Q: 如何避免安装捆绑软件？**

添加 `--interactive` 参数。脚本会预填安装目录并启动安装器 UI，让你手动取消勾选捆绑选项。建议对国产消费类软件（微信、百度、360 等）使用此模式。

---

## 目录结构

```
windows-software-installer/
├── SKILL.md                      # Skill 定义（Agent 读取）
├── README.md                     # 英文文档
├── README.zh.md                  # 中文文档（本文）
├── scripts/
│   └── install_windows_software.py   # 核心安装脚本
├── references/
│   ├── scoop-buckets.md          # Scoop bucket 参考
│   └── installer-patterns.md     # 安装器类型文档
├── evals/
│   └── evals.json                # 评估测试用例
└── npm-publish/                  # npm 包源码
    ├── bin/cli.js                # npx 安装脚本
    └── package.json
```

---

## 许可证

[MIT](./LICENSE) © [BingWuJ](https://github.com/BingWuJ)

---

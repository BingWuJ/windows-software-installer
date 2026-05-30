# @bingwuj/windows-software-installer

> 🛡️ 更安全的 Windows 软件安装器 — AI Agent Skill

[![platform](https://img.shields.io/badge/platform-Windows-blue)](https://github.com/BingWuJ/windows-software-installer)
[![type](https://img.shields.io/badge/type-Agent%20Skill-purple)](https://github.com/BingWuJ/windows-software-installer)
[![license](https://img.shields.io/badge/license-MIT-green)](https://github.com/BingWuJ/windows-software-installer)

一行命令安装，为 [pi Coding Agent](https://pi.dev) 和 [Claude Code](https://claude.ai/code) 提供安全的 Windows 软件安装能力。

## 快速安装

```bash
npx @bingwuj/windows-software-installer
```

自动将 skill 文件安装到 `~/.agents/skills/` 和 `~/.claude/skills/`。

## 使用方式

安装完成后，在 pi 或 Claude Code 中直接使用：

```
/INSTALL vscode              # 通过 Scoop 安装
/INSTALL D:\Downloads\setup.exe   # 从本地安装包安装
/INSTALL https://example.com/app.exe  # 下载并验证后安装
```

## 三种安装模式

| 模式 | 说明 | 安全级别 |
|------|------|----------|
| **Scoop** | 从 Scoop 仓库安装 | ✅ 最高 |
| **Local file** | 从本地 .exe/.msi 安装 | ✅ 信任 |
| **Verified download** | 下载后 SHA256/签名验证 | ✅ 已验证 |

## 安全机制

- 🔒 **SHA256 哈希校验** — 验证下载文件完整性
- 🔏 **Authenticode 签名验证** — 确认发布者身份
- 🌐 **HTTPS 强制** — 所有下载必须走加密连接
- 📁 **C 盘保护** — 默认安装到 `D:\iStall\` 保持 C 盘干净

## 要求

- Windows 10/11
- Node.js >= 16（用于 npx 安装）
- Python 3.8+（安装脚本运行所需）

## 手动安装

```bash
git clone https://github.com/BingWuJ/windows-software-installer ~/.agents/skills/windows-software-installer
```

## License

MIT © [BingWuJ](https://github.com/BingWuJ)

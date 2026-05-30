<p align="center">
  <strong>Windows Software Installer</strong>
</p>

<p align="center">
  <em>Agent Skill - 安全优先的 Windows 软件安装自动化</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%20Only-0078D4?logo=windows11" alt="Windows Only" />
  <img src="https://img.shields.io/badge/type-Agent%20Skill-8B5CF6" alt="Agent Skill" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
  <img src="https://img.shields.io/badge/entry-%2FINSTALL-orange" alt="/INSTALL" />
</p>

---

一句话描述：通过 Scoop、本地安装包或经 SHA256 / Authenticode 校验的 HTTPS 下载三种模式安装 Windows 软件，默认安装到 D 盘，拒绝未经验证的可执行文件。

---

## 功能特性

- 快捷入口 - /INSTALL payload 一条指令直达，自动识别 payload 类型并选择对应模式
- Scoop 模式 - 最安全的路径，直接从 Scoop bucket 安装，自动管理目录
- 本地安装包模式 - 已下载的 .exe / .msi 文件直接安装，无需重复下载
- 下载校验模式 - 仅 HTTPS，强制 SHA256 或 Authenticode 签名校验，拒绝未签名文件
- D 盘优先 - 默认安装路径 D:\iStall\{software_name}，避免 C 盘膨胀
- CDN Referer 支持 - 自动处理国内软件 CDN 的防盗链问题
- 交互模式 - 可启动安装器 UI 手动勾选，规避捆绑软件
- 智能发现 - 通过 winget search / scoop search 查找包名和官方下载地址

---

## 安装流程

```
/INSTALL payload
       |
       v
 +-------------+
 |  识别 payload |
 +------+------+
        |
   +----+------------+
   |    |            |
   v    v            v
 绝对路径?    HTTPS URL?    软件名?
   |          |            |
   v          v            v
+------+  +----------+  +----------+
|local |  |download- |  | winget +  |
|-file |  |verified  |  | scoop搜索 |
|模式  |  |  模式    |  |  发现     |
+--+---+  +----+-----+  +-----+----+
   |           |              |
   v           v              v
 安装      安全校验      选择一种模式
       +----+----+
       |         |
   有SHA256?  有签名?
       |         |
  +----+    +----+
  v         v
哈希比对  Authenticode
  pass     签名验证 pass
       |
       v
  安装到 D:\iStall\
```

---

## 安装 Skill

**Pi Agent：**

```powershell
# Skill 已在 ~/.agents/skills/windows-software-installer/ 即可使用
# 无需额外配置，/INSTALL 自动触发
```

**Claude Code（通过 Junction 联接）：**

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\windows-software-installer" `
  -Target "$HOME\.agents\skills\windows-software-installer" -Force
```

---

## 使用示例

### 1. Scoop 模式 - 最安全

```powershell
/INSTALL neovim-nightly
```

等价于：

```bash
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name neovim-nightly \
  --scoop-bucket nightly
```

### 2. 本地安装包模式 - 已有安装文件

```powershell
/INSTALL D:\Downloads\Typeless-0.4.6-x64-Setup.exe
```

等价于：

```bash
python scripts/install_windows_software.py \
  --mode local-file \
  --software-name typeless \
  --local-file "D:\Downloads\Typeless-0.4.6-x64-Setup.exe" \
  --installer-type nsis
```

### 3. 下载校验模式 - 从 URL 下载并校验

```powershell
/INSTALL https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe
```

等价于：

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name sumatrapdf \
  --download-url "https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe" \
  --installer-type nsis \
  --sha256 "<sha256>"
```

**带 CDN 防盗链：**

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name shandianshuo \
  --download-url "https://download.shandianshuo.cn/windows/shandianshuo_0.6.7_x64-setup.exe" \
  --installer-type nsis \
  --referer "https://shandianshuo.cn/" \
  --allow-untrusted-publisher
```

---

## 安全机制

| 安全措施 | Scoop | local-file | download-verified | 说明 |
|:---|:---:|:---:|:---:|:---|
| HTTPS 强制 | - | - | pass | 拒绝非 HTTPS 下载 URL |
| SHA256 校验 | - | - | pass | 厂商提供的哈希值比对，最强验证 |
| Authenticode 签名验证 | - | - | pass | 未签名文件直接拒绝 |
| 未知发布者确认 | - | - | pass | 签名有效但未在白名单需手动确认 |
| 文件类型限制 | - | pass | - | 仅接受 .exe / .msi |
| 无自由注入参数 | pass | pass | pass | 禁止传入任意安装器参数防止命令注入 |
| 单模式执行 | pass | pass | pass | 安装过程不自动切换回退到其他模式 |

---

## 配置

| 配置项 | 默认值 | 说明 |
|:---|:---|:---|
| 默认安装路径 | D:\iStall\{software_name} | 可通过 --install-dir 覆盖 |
| 下载缓存目录 | D:\WUDownloadCache | 下载文件临时存放位置 |
| 支持的安装器类型 | nsis, inno, msi | local-file 和 download-verified 模式必填 |
| 下载引擎优先级 | NDM - aria2c - PowerShell | 自动检测，NDM 优先 |
| winget 角色 | 仅发现（search / show） | 不用于安装 --location 经常被安装器忽略 |

---

## 目录结构

```
windows-software-installer/
+-- SKILL.md                  # Skill 定义与完整指令
+-- README.md                 # 本文件
+-- scripts/
|   +-- install_windows_software.py   # 安装核心脚本
+-- references/
|   +-- scoop-buckets.md      # Scoop bucket 参考列表
|   +-- installer-patterns.md # 安装器模板文档
+-- evals/
    +-- evals.json            # 评估测试用例
```

---

## FAQ

<details>
<summary><strong>Q: 厂商没有提供 SHA256 怎么办？</strong></summary>

使用 download-verified 模式 + 有效的数字签名 + --publisher 参数。签名有效但发布者不在白名单时，脚本会显示签名者信息并请求手动确认。

</details>

<details>
<summary><strong>Q: 为什么不用 winget 直接安装？</strong></summary>

winget 的 --location 参数经常被底层安装器忽略，导致软件仍安装到 C 盘。本 skill 仅用 winget 做包名发现和 URL 提取，安装走 Scoop 或自管脚本以确保安装到 D 盘。

</details>

<details>
<summary><strong>Q: 下载返回 403 Forbidden 是什么原因？</strong></summary>

国内软件 CDN（如 download.*.cn）通常启用 Referer 防盗链，拒绝不带官方站点 Referer 的请求。NDM 和 aria2c 不发送 Referer，此时脚本会回退到 PowerShell Invoke-WebRequest。使用 --referer 传入官方站点 URL 即可解决。

</details>

<details>
<summary><strong>Q: 可以传入自定义安装器参数吗？</strong></summary>

不可以。本 skill 刻意禁止自由格式的安装器参数，以降低命令注入和安装器行为不匹配的风险。

</details>

<details>
<summary><strong>Q: 如何避免安装捆绑软件？</strong></summary>

添加 --interactive 参数。脚本会预填安装目录并启动安装器 UI，由你手动取消勾选捆绑项并完成安装。推荐对国产消费类软件（微信、百度、360 等）使用此模式。

</details>

---

## License

[MIT](./LICENSE) (c) 2025

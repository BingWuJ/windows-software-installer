---
name: windows-software-installer
description: >
  Safer Windows software installer for explicit Scoop, local installer, or verified download workflows.
  Use when installing Windows software with controlled modes: (1) Scoop packages, (2) trusted local
  .exe/.msi installers, or (3) HTTPS downloads that pass SHA256 or Authenticode signature checks.
  Also trigger on concise requests such as /INSTALL vscode, /INSTALL 微信, /INSTALL D:\Downloads\setup.msi,
  or /INSTALL https://vendor.example/app.exe. Avoid for generic "install anything" requests or arbitrary
  unverified download-and-run flows. Note: winget is used only for discovery (to find the official download
  URL or confirm a package exists), not for installation — winget's --location flag is frequently ignored
  by installers, which would defeat the goal of keeping software off the C drive.
---

# Windows Software Installer

Install Windows software through explicit modes with safer defaults. This skill keeps the existing default paths to avoid filling the C drive:

- Default install directory: `D:\iStall\{software_name}`
- Default download cache: `D:\WUDownloadCache`

## Quick Entry

Use `/INSTALL <payload>` as the short entrypoint for this skill. Treat `/INSTALL` and `/install` the same way.

Interpret `<payload>` in this order:

1. Absolute Windows path: use `local-file`
2. HTTPS URL: use `download-verified`
3. Anything else: treat as a software name → run `winget search <name>` and `scoop search <name>` only for discovery, then choose one explicit mode before installing

Examples:

```text
/INSTALL vscode
/INSTALL 微信
/INSTALL D:\Downloads\Typeless-0.4.6-x64-Setup.exe
/INSTALL https://vendor.example/app.exe
```

Rules:

- `/INSTALL` is only a shorter entrypoint. It does not bypass any security checks.
- Do not guess download links from vague software names.
- Reject non-HTTPS URLs.
- Reject local files that are not `.exe` or `.msi`.
- If the request is more complex than a single payload, fall back to the explicit CLI arguments below.
- For software-name payloads, discovery may inform the choice, but do not auto-switch modes during installation.

## Modes

### `scoop`
Use when the software exists in Scoop and you want the lowest-risk path. Note: `--installer-type` is not needed for scoop mode, Scoop manages the installation internally.

```bash
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name vscode
```

Optional bucket:

```bash
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name neovim-nightly \
  --scoop-bucket nightly
```

### `local-file`
Use when the installer has already been downloaded manually and you trust the file source.

```bash
python scripts/install_windows_software.py \
  --mode local-file \
  --software-name typeless \
  --local-file "D:\Downloads\Typeless-0.4.6-x64-Setup.exe" \
  --installer-type nsis
```

### `download-verified`
Use when you need the script to download the installer itself. Only HTTPS is allowed. The installer must either:

- pass `--sha256`, or
- have a valid Authenticode signature

If the signature is valid but the publisher is not in the allowlist, the script asks for confirmation unless `--allow-untrusted-publisher` is provided.

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name wechat \
  --download-url "https://example.com/WeChatSetup.exe" \
  --installer-type nsis \
  --publisher Tencent
```

With SHA256:

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name sumatrapdf \
  --download-url "https://www.sumatrapdfreader.org/dl/rel/3.5.2/SumatraPDF-3.5.2-64-install.exe" \
  --installer-type nsis \
  --sha256 "<sha256>"
```

Interactive mode (launches the installer UI with the install directory pre-filled; success here means the installer was launched, and you handle the remaining steps to avoid bundled software):

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name wechat \
  --download-url "https://example.com/WeChatSetup.exe" \
  --installer-type nsis \
  --publisher Tencent \
  --interactive
```

With CDN Referer protection (download URL requires a Referer header):

```bash
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name shandianshuo \
  --download-url "https://download.shandianshuo.cn/windows/shandianshuo_0.6.7_x64-setup.exe" \
  --installer-type nsis \
  --referer "https://shandianshuo.cn/" \
  --allow-untrusted-publisher
```

## Security Rules

- Use one explicit mode. Discovery is allowed, but installation must use a single chosen mode with no automatic fallback.
- Only HTTPS download URLs are allowed.
- Do not pass arbitrary installer argument strings.
- `download-verified` refuses unsigned installers.
- Signed installers from unknown publishers require confirmation unless `--allow-untrusted-publisher` is set.
- `local-file` mode copies the installer into the install directory for execution, but does not delete the original file.

## Parameters

| Parameter | Required | Modes | Description |
|---|---|---|---|
| `--mode` | Yes | all | `scoop`, `local-file`, or `download-verified` |
| `--software-name` | Yes | all | Safe identifier used for Scoop and default install dir |
| `--installer-type` | Yes | local-file, download-verified | `nsis`, `inno`, or `msi` |
| `--scoop-bucket` | No | scoop | Optional Scoop bucket |
| `--local-file` | Yes | local-file | Absolute path to a trusted `.exe` or `.msi` |
| `--download-url` | Yes | download-verified | HTTPS URL to the installer |
| `--sha256` | No | download-verified | Strongest verification when vendor provides a hash |
| `--publisher` | No | download-verified | Expected publisher hint for signed installers |
| `--allow-untrusted-publisher` | No | download-verified | Skip the confirmation step for valid but unlisted publishers |
| `--referer` | No | download-verified | Referer header URL for CDN hotlink protection (e.g. the software's official site) |
| `--interactive` | No | local-file, download-verified | Launch installer in interactive mode so you can manually uncheck bundled software |
| `--install-dir` | No | all | Override install destination; default is `D:\iStall\{software_name}` |

## Full Auto Workflow (recommended for winget-listed software)

When the software has a winget entry with `Installer Type: exe/msi`, use this pipeline to discover the URL automatically and download via Neat Download Manager:

```powershell
# Step 1: find the Package ID
winget search <name>

# Step 2: extract official URL and SHA256
winget show <PackageId>
# Look for:
#   Installer Url: https://...
#   Installer SHA256: <hash>
```

```bash
# Step 3: download-verified with the values from winget show
python scripts/install_windows_software.py \
  --mode download-verified \
  --software-name <name> \
  --download-url "<Installer Url>" \
  --installer-type <inno|nsis|msi> \
  --sha256 "<Installer SHA256>"
```

The script auto-detects Neat Download Manager (via registry) and uses it as the download engine. If NDM is not installed it falls back to aria2c, and if aria2c also fails, it falls back to PowerShell `Invoke-WebRequest` (which supports `--referer` for CDN hotlink protection). After downloading, it verifies the SHA256 and installs to `D:\iStall\<name>`. Use this only after you have explicitly chosen `download-verified` as the install mode.

**Note:** `winget show` sometimes lists `Installer Type: msstore` — those are Microsoft Store apps. They cannot be redirected to D: and this workflow does not apply.

## Post-Installation Cleanup

After any download-based installation (`download-verified` mode or manual download + extract) succeeds and the installed version is verified, **always delete the cached download file** from `D:\WUDownloadCache`:

```powershell
Remove-Item 'D:\WUDownloadCache\<downloaded-file>' -Force
```

This applies to all archive types (`.zip`, `.tar.gz`) and installer files (`.exe`, `.msi`). Only clean up after confirming the installation was successful — do not delete the cache if verification failed or the user may need to retry.

For portable software distributed as `.zip` (like CC-Switch Portable), the typical manual flow is:

1. Download to `D:\WUDownloadCache`
2. Verify SHA256
3. Extract to `D:\iStall\<software_name>`
4. Confirm installed version
5. **Delete the zip from `D:\WUDownloadCache`**

## When To Prefer Each Mode

- **Discovery first**: Run `winget search <name>` and `scoop search <name>` to find what's available. winget has broader coverage for mainstream consumer software; scoop is better for CLI/dev tools.
- **Do NOT install via winget** even if it lists the package — winget's `--location` flag is frequently ignored by the underlying installer, which defeats the goal of keeping software off the C drive.
- **Use `scoop`** when the package is found in Scoop. Scoop respects the install location because it manages the directory itself.
- **Use `local-file`** for installers you already downloaded yourself.
- **Use `download-verified`** when scoop doesn't have it and you need to download from a vendor URL. Always required — downloading from an "official" URL alone is not sufficient, as CDN compromise or MITM can tamper with the file in transit.
- **Add `--interactive`** when the installer is known to bundle unwanted software (common with Chinese consumer apps like WeChat, Baidu, 360). The script will pre-fill the install directory and launch the installer UI; you then manually uncheck bundled offers and complete the installation.

**Exception**: if the user explicitly accepts C drive installation, winget is fine and simpler.

## Finding the Download URL from an Official Website

When winget and scoop both come up empty, you need to find the download URL from the vendor's website. The full discovery flow is:

**Step 1: Web search to find the official website.**

Use a web search tool to look up the software name. The goal is to find the vendor's official site URL (not a third-party download mirror).

**Step 2: Fetch the raw HTML and extract download links.**

**Do not use webReader / web_fetch_exa / tavily_extract** for this — these tools render pages into readable markdown and strip HTML tag attributes, so `<a href="https://download.example.com/setup.exe">` download links are lost entirely.

Instead, fetch the raw HTML and search for installer URLs:

```powershell
$env:HTTPS_PROXY = 'http://127.0.0.1:10809'
$env:HTTP_PROXY  = 'http://127.0.0.1:10809'
$env:NODE_USE_ENV_PROXY = '1'
node -e "fetch('https://official-site.example/').then(r=>r.text()).then(t=>{const matches=t.match(/https?:\/\/[^\s\"'<>]+\.exe/gi); console.log(matches||'no exe links found')}).catch(e=>console.error(e.message))"
```

This returns the direct download URLs embedded in the page. If Node.js is not available, use the PowerShell equivalent:

```powershell
$response = Invoke-WebRequest -Uri 'https://official-site.example/' -UseBasicParsing
$matches = [regex]::Matches($response.Content, 'https?://[^\s""''<>]+\.exe', 'IgnoreCase')
if ($matches.Count -gt 0) { $matches.Value } else { Write-Host 'no exe links found' }
```

If the site is a single-page app that loads content via JavaScript, the HTML source may not contain the links — in that case try the site's GitHub releases page, or search the web for `<software name> download url exe` to find cached or documented download links.

## Troubleshooting

**Q: The vendor does not publish SHA256.**
A: Use `download-verified` with a valid digital signature and `--publisher`. If the signer is valid but not allowlisted, review the displayed signer and confirm manually.

**Q: I do not want software to install to C:.**
A: The default install path remains `D:\iStall\{software_name}`. You can also set `--install-dir` explicitly.

**Q: Can I still use arbitrary installer switches?**
A: No. This skill intentionally removes free-form installer arguments to reduce command injection and mismatched installer behavior.

**Q: Download fails with 403 Forbidden from CDN.**
A: Many Chinese software CDNs (e.g. `download.*.cn` subdomains) enforce Referer-based hotlink protection — they reject downloads that don't carry the official site as the `Referer` header. NDM and aria2c do not send Referer headers, so the script falls back to PowerShell `Invoke-WebRequest`. Use `--referer "https://official-site.example/"` to pass the official site URL. If you see an error mentioning `Referer ACL` or `denied by Referer ACL`, this is the cause.

## Reference Materials

- See [references/scoop-buckets.md](references/scoop-buckets.md) for bucket guidance.
- See [references/installer-patterns.md](references/installer-patterns.md) for the installer templates supported by this skill.

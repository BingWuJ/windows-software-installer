---
name: windows-software-installer
description: Safer Windows software installer for explicit Scoop, local installer, or verified download workflows. Use when installing Windows software with controlled modes: (1) Scoop packages, (2) trusted local .exe/.msi installers, or (3) HTTPS downloads that pass SHA256 or Authenticode signature checks. Also trigger on concise requests such as `/INSTALL vscode`, `/INSTALL 微信`, `/INSTALL D:\Downloads\setup.msi`, or `/INSTALL https://vendor.example/app.exe`. Avoid for generic "install anything" requests or arbitrary unverified download-and-run flows.
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
3. Anything else: treat as a software name and try `scoop`

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

## Modes

### `scoop`
Use when the software exists in Scoop and you want the lowest-risk path.

```bash
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name vscode \
  --installer-type nsis
```

Optional bucket:

```bash
python scripts/install_windows_software.py \
  --mode scoop \
  --software-name neovim-nightly \
  --scoop-bucket nightly \
  --installer-type nsis
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

## Security Rules

- Use one explicit mode. There is no automatic fallback.
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
| `--installer-type` | Yes | all | `nsis`, `inno`, `msi`, `installshield` |
| `--scoop-bucket` | No | scoop | Optional Scoop bucket |
| `--local-file` | Yes | local-file | Absolute path to a trusted `.exe` or `.msi` |
| `--download-url` | Yes | download-verified | HTTPS URL to the installer |
| `--sha256` | No | download-verified | Strongest verification when vendor provides a hash |
| `--publisher` | No | download-verified | Expected publisher hint for signed installers |
| `--allow-untrusted-publisher` | No | download-verified | Skip the confirmation step for valid but unlisted publishers |
| `--install-dir` | No | all | Override install destination; default is `D:\iStall\{software_name}` |

## When To Prefer Each Mode

- Use `scoop` first when possible.
- Use `local-file` for installers you already downloaded yourself.
- Use `download-verified` only when the download source is trusted and the file can be verified by hash or signature.

## Troubleshooting

**Q: The vendor does not publish SHA256.**
A: Use `download-verified` with a valid digital signature and `--publisher`. If the signer is valid but not allowlisted, review the displayed signer and confirm manually.

**Q: I do not want software to install to C:.**
A: The default install path remains `D:\iStall\{software_name}`. You can also set `--install-dir` explicitly.

**Q: Can I still use arbitrary installer switches?**
A: No. This skill intentionally removes free-form installer arguments to reduce command injection and mismatched installer behavior.

## Reference Materials

- See [references/scoop-buckets.md](references/scoop-buckets.md) for bucket guidance.
- See [references/installer-patterns.md](references/installer-patterns.md) for the installer templates supported by this skill.

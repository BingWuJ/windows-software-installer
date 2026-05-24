# Supported Installer Patterns

This skill no longer accepts free-form installer arguments. It uses built-in templates for a small set of installer types that can reliably honor the requested install directory.

## Supported Types

### NSIS
- Base flags: `/S`
- Install directory: `/D=<path>` appended by the script

### Inno Setup
- Base flags: `/VERYSILENT /NORESTART`
- Install directory: `/DIR="<path>"` appended by the script

### MSI
- Executed through `msiexec`
- Base flags: `/quiet /norestart`
- Install directory: `TARGETDIR=<path> INSTALLDIR=<path>` (both passed for maximum compatibility)


## Verification Rules

### `download-verified`
A download is allowed to run only if one of these conditions is true:

1. The provided `--sha256` matches the downloaded file.
2. The file has a valid Authenticode signature and either:
   - the signer matches the publisher allowlist, or
   - the user confirms a valid but unlisted publisher.

Unsigned downloads are rejected.

### `local-file`
Local installers must be `.exe` or `.msi` files on an absolute path.

## Interactive Mode (`--interactive`)

When `--interactive` is set, the silent flags are omitted but the install directory is still passed. This launches the installer UI with the directory pre-filled. In interactive mode, success means the installer was launched; the user then manually:

- Uncheck bundled software offers (common in Chinese consumer apps)
- Review license agreements
- Choose custom components

**Flags used in interactive mode:**

| Type | Interactive flags |
|------|-------------------|
| NSIS | `/D=<path>` (no `/S`) |
| Inno | `/DIR="<path>"` (no `/VERYSILENT /NORESTART`) |
| MSI | `TARGETDIR=... INSTALLDIR=...` (no `/quiet /norestart`) |

Interactive mode is only available for `local-file` and `download-verified` modes, not `scoop`.

## Why this skill removed custom arguments

The previous version accepted arbitrary installer switches and executed shell strings directly. That made command injection and unsafe installer execution too easy. The current version keeps behavior predictable and auditable by using fixed templates.

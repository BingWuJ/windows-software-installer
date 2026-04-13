# Supported Installer Patterns

This skill no longer accepts free-form installer arguments. It uses built-in templates for a small set of installer types.

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
- Install directory: `INSTALLDIR=<path>`

### InstallShield
- Base flags: `/s`
- Use only when the vendor confirms standard silent install behavior

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

## Why this skill removed custom arguments

The previous version accepted arbitrary installer switches and executed shell strings directly. That made command injection and unsafe installer execution too easy. The current version keeps behavior predictable and auditable by using fixed templates.

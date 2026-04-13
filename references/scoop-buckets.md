# Scoop Buckets Reference

Common Scoop buckets and their typical software packages.

## Official Buckets

### `main` (default)
The default bucket containing stable, well-maintained software.

Common packages:
- `python` - Python programming language
- `nodejs` - Node.js JavaScript runtime
- `git` - Git version control
- `vim` - Vim text editor
- `neovim` - Neovim text editor
- `ffmpeg` - FFmpeg multimedia framework
- `curl` - curl data transfer tool
- `wget` - wget download utility
- `grep` - grep text search
- `tar` - tar archive utility

### `extras`
Software that doesn't meet the criteria for the main bucket but is still useful.

Common packages:
- `vscode` - Visual Studio Code
- `chrome` - Google Chrome browser
- `firefox` - Mozilla Firefox browser
- `notepadplusplus` - Notepad++ text editor
- `sublime-text` - Sublime Text editor
- `obsidian` - Obsidian note-taking app
- `typora` - Typora markdown editor
- `telegram` - Telegram messenger
- `discord` - Discord chat app
- `spotify` - Spotify music streaming
- `steam` - Steam gaming platform
- `vlc` - VLC media player

### `versions`
Multiple versions of software (nightly, beta, portable, etc.)

Common packages:
- `python-nightly`
- `nodejs-nightly`
- `rust-nightly`
- `gcc-nightly`

### `nightly`
Nightly builds of software.

Common packages:
- `neovim-nightly`
- `ruby-nightly`

### `nerd-fonts`
Nerd Fonts - patched fonts for developers.

Common packages:
- `FiraCode-NF`
- `JetBrainsMono-NF`
- `Hack-NF`
- `SourceCodePro-NF`

## Third-Party Buckets

### `nonportable`
Contains non-portable versions of software (requires installation, not portable).

Usage:
```bash
scoop bucket add nonportable
scoop install nonportable/<app-name>
```

### `games`
Game-related software and tools.

### `java`
Java Development Kits and Runtime Environments.

Common packages:
- `temurin-jdk` - Eclipse Temurin JDK (formerly AdoptOpenJDK)
- `openjdk` - OpenJDK
- `oraclejdk` - Oracle JDK

## Managing Buckets

### Add a bucket:
```bash
scoop bucket add <bucket-name>
```

### List known buckets:
```bash
scoop bucket known
```

### List installed buckets:
```bash
scoop bucket list
```

### Remove a bucket:
```bash
scoop bucket rm <bucket-name>
```

## Searching for Software

### Search all buckets:
```bash
scoop search <software-name>
```

### Search specific bucket:
```bash
scoop search <software-name> # Shows results from all buckets with bucket names
```

## Bucket Selection Tips

1. **Try main bucket first** - Most stable and well-maintained packages
2. **Use extras for GUI apps** - Popular desktop applications
3. **Use versions for alternatives** - When you need specific versions or variants
4. **Use nightly for bleeding edge** - Latest development builds (may be unstable)
5. **Add third-party buckets as needed** - For specialized software

## Example: Finding Software

To find where VS Code is located:
```bash
scoop search vscode
# Output shows: 'vscode' bucket 'extras'
```

Then install with:
```bash
scoop install vscode --bucket extras
# or simply (scoop finds it automatically):
scoop install vscode
```

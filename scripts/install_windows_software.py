#!/usr/bin/env python3
"""
Windows Software Installer

Install software on Windows using one of three explicit modes:
- scoop
- local-file
- download-verified
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_INSTALL_ROOT = Path("D:/iStall")
DEFAULT_DOWNLOAD_CACHE = Path("D:/WUDownloadCache")
SAFE_NAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._+")
SAFE_BUCKET_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
SAFE_EXTENSIONS = {".exe", ".msi"}
DEFAULT_PUBLISHERS = {
    "Tencent Technology (Shenzhen) Company Limited",
    "Tencent",
    "Microsoft Corporation",
    "Google LLC",
    "Mozilla Corporation",
    "Notepad++ Team",
    "VideoLAN",
    "GitHub, Inc.",
}

INSTALLER_TEMPLATES = {
    "nsis": ["/S"],
    "inno": ["/VERYSILENT", "/NORESTART"],
    "msi": ["/quiet", "/norestart"],
    "installshield": ["/s"],
}


def safe_print_command(cmd):
    print("Running:", " ".join(str(part) for part in cmd))


def run_command(cmd, check=True, capture_output=True):
    safe_print_command(cmd)
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture_output,
        text=True,
    )


def fail(message):
    print(message, file=sys.stderr)
    return 1


def validate_safe_token(value, label, allowed_chars):
    if not value or any(char not in allowed_chars for char in value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


def ensure_windows_absolute_path(path_value, label):
    path = Path(path_value)
    if not path.is_absolute():
        raise ValueError(f"{label} must be an absolute path: {path_value}")
    return path


def get_default_install_dir(software_name):
    return DEFAULT_INSTALL_ROOT / software_name


def validate_installer_file(path):
    if not path.exists():
        raise ValueError(f"Installer file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Installer path is not a file: {path}")
    if path.suffix.lower() not in SAFE_EXTENSIONS:
        raise ValueError(f"Unsupported installer type: {path.suffix}")


def validate_download_url(url):
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https":
        raise ValueError("download-url must use HTTPS")
    if not parsed.netloc:
        raise ValueError("download-url must include a hostname")
    return parsed


def verify_sha256(path, expected_sha256):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest().lower()
    return actual == expected_sha256.lower(), actual


def get_authenticode_signature(path):
    command = [
        "pwsh",
        "-NoProfile",
        "-Command",
        (
            "Get-AuthenticodeSignature -FilePath $args[0] | "
            "Select-Object Status,StatusMessage,@{Name='Signer';Expression={"
            "if ($_.SignerCertificate) { $_.SignerCertificate.Subject } else { '' }"
            "}} | ConvertTo-Json -Compress"
        ),
        str(path),
    ]
    result = run_command(command, check=False)
    if result.returncode != 0 or not result.stdout.strip():
        return None

    try:
        import json

        payload = json.loads(result.stdout)
    except Exception:
        return None

    return {
        "status": payload.get("Status", ""),
        "status_message": payload.get("StatusMessage", ""),
        "signer": payload.get("Signer", ""),
    }


def signature_is_valid(signature):
    return signature and signature.get("status") == "Valid" and signature.get("signer")


def signer_matches_allowlist(signature, publisher, allowlisted_publishers):
    signer = signature.get("signer", "")
    if publisher:
        return publisher.lower() in signer.lower()
    return any(candidate.lower() in signer.lower() for candidate in allowlisted_publishers)


def confirm_untrusted_publisher(signature):
    signer = signature.get("signer", "")
    print("Publisher is not in the allowlist.")
    print(f"Detected publisher: {signer}")
    answer = input("Continue anyway? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def check_scoop_installed():
    result = run_command(["scoop", "--version"], check=False)
    return result.returncode == 0


def install_with_scoop(software_name, bucket=None):
    if not check_scoop_installed():
        print("Scoop is not installed.")
        return False

    command = ["scoop", "install", software_name]
    if bucket:
        command.extend(["--bucket", bucket])

    result = run_command(command, check=False)
    if result.returncode != 0:
        print(f"Scoop installation of {software_name} failed")
        return False

    verify_result = run_command(["scoop", "list"], check=False)
    if verify_result.returncode != 0:
        print("Could not verify Scoop installation")
        return False

    installed = any(
        line.split()[0].lower() == software_name.lower()
        for line in verify_result.stdout.splitlines()
        if line.strip() and not line.startswith("Installed apps:")
    )
    if installed:
        print(f"Successfully installed {software_name} via Scoop")
        return True

    print(f"Scoop did not report {software_name} as installed")
    return False


def download_installer(download_url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    result = run_command(
        ["aria2c", "--allow-overwrite=true", "-d", str(destination.parent), "-o", destination.name, download_url],
        check=False,
    )
    return result.returncode == 0


def build_install_command(installer_path, installer_type, install_dir):
    installer_type = installer_type.lower()
    if installer_type not in INSTALLER_TEMPLATES:
        raise ValueError(f"Unsupported installer type: {installer_type}")

    if installer_type == "msi":
        return [
            "msiexec",
            "/i",
            str(installer_path),
            *INSTALLER_TEMPLATES["msi"],
            f"INSTALLDIR={install_dir}",
        ]

    command = [str(installer_path), *INSTALLER_TEMPLATES[installer_type]]
    if installer_type == "nsis":
        command.append(f"/D={install_dir}")
    elif installer_type == "inno":
        command.append(f'/DIR="{install_dir}"')
    return command


def verify_manual_install(install_dir):
    if not install_dir.exists():
        return False

    for pattern in ("*.exe", "*.lnk", "*.dll"):
        if any(install_dir.rglob(pattern)):
            return True
    return False


def prepare_local_installer(local_file, software_name, install_dir):
    source = ensure_windows_absolute_path(local_file, "local-file")
    validate_installer_file(source)
    install_dir.mkdir(parents=True, exist_ok=True)

    copied_path = install_dir / f"{software_name}-installer{source.suffix.lower()}"
    shutil.copy2(source, copied_path)
    return copied_path


def prepare_downloaded_installer(download_url, software_name, install_dir):
    parsed = validate_download_url(download_url)
    install_dir.mkdir(parents=True, exist_ok=True)
    DEFAULT_DOWNLOAD_CACHE.mkdir(parents=True, exist_ok=True)

    extension = Path(parsed.path).suffix.lower()
    if extension not in SAFE_EXTENSIONS:
        raise ValueError("download-url must point to an .exe or .msi installer")

    cache_path = DEFAULT_DOWNLOAD_CACHE / f"{software_name}-installer{extension}"
    if not download_installer(download_url, cache_path):
        raise RuntimeError(f"Failed to download installer from {download_url}")

    final_path = install_dir / cache_path.name
    shutil.copy2(cache_path, final_path)
    return cache_path, final_path


def validate_downloaded_installer(installer_path, sha256_value, publisher, allow_untrusted_publisher):
    if sha256_value:
        is_valid, actual_sha256 = verify_sha256(installer_path, sha256_value)
        if not is_valid:
            raise RuntimeError(
                "SHA256 mismatch for downloaded installer. "
                f"Expected {sha256_value.lower()}, got {actual_sha256}"
            )
        print("SHA256 verification passed.")
        return

    signature = get_authenticode_signature(installer_path)
    if not signature_is_valid(signature):
        raise RuntimeError("Downloaded installer does not have a valid Authenticode signature")

    if signer_matches_allowlist(signature, publisher, DEFAULT_PUBLISHERS):
        print(f"Trusted signed publisher detected: {signature['signer']}")
        return

    if allow_untrusted_publisher or confirm_untrusted_publisher(signature):
        print(f"Proceeding with signed but untrusted publisher: {signature['signer']}")
        return

    raise RuntimeError("Publisher is signed but not allowlisted")


def install_manually(installer_path, installer_type, install_dir):
    command = build_install_command(installer_path, installer_type, install_dir)
    result = run_command(command, check=False)
    if result.returncode != 0:
        print("Manual installation failed")
        return False

    if verify_manual_install(install_dir):
        print(f"Successfully installed software to {install_dir}")
        return True

    print("Installer exited successfully but installation could not be verified")
    return False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install software on Windows using explicit and safer installation modes"
    )
    parser.add_argument("--mode", required=True, choices=["scoop", "local-file", "download-verified"])
    parser.add_argument("--software-name", "--software_name", required=True, dest="software_name")
    parser.add_argument("--scoop-bucket", "--scoop_bucket", dest="scoop_bucket")
    parser.add_argument("--local-file", "--local_file", dest="local_file")
    parser.add_argument("--download-url", "--download_url", dest="download_url")
    parser.add_argument("--sha256")
    parser.add_argument(
        "--installer-type",
        required=True,
        choices=["nsis", "inno", "msi", "installshield"],
    )
    parser.add_argument("--install-dir", dest="install_dir")
    parser.add_argument("--publisher")
    parser.add_argument("--allow-untrusted-publisher", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        software_name = validate_safe_token(args.software_name, "software-name", SAFE_NAME_CHARS)
        if args.scoop_bucket:
            validate_safe_token(args.scoop_bucket, "scoop-bucket", SAFE_BUCKET_CHARS)

        install_dir = (
            ensure_windows_absolute_path(args.install_dir, "install-dir")
            if args.install_dir
            else get_default_install_dir(software_name)
        )
        install_dir.mkdir(parents=True, exist_ok=True)
    except ValueError as error:
        return fail(str(error))

    if args.mode == "scoop":
        if args.local_file or args.download_url or args.sha256 or args.publisher or args.allow_untrusted_publisher:
            return fail("scoop mode does not accept local-file, download-url, sha256, publisher, or allow-untrusted-publisher")
        return 0 if install_with_scoop(software_name, args.scoop_bucket) else 1

    temp_paths = []
    try:
        if args.mode == "local-file":
            if not args.local_file:
                return fail("local-file mode requires --local-file")
            installer_path = prepare_local_installer(args.local_file, software_name, install_dir)
            temp_paths.append(installer_path)
            success = install_manually(installer_path, args.installer_type, install_dir)
            return 0 if success else 1

        if not args.download_url:
            return fail("download-verified mode requires --download-url")

        cache_path, installer_path = prepare_downloaded_installer(args.download_url, software_name, install_dir)
        temp_paths.extend([cache_path, installer_path])
        validate_downloaded_installer(
            installer_path,
            args.sha256,
            args.publisher,
            args.allow_untrusted_publisher,
        )
        success = install_manually(installer_path, args.installer_type, install_dir)
        return 0 if success else 1
    except (RuntimeError, ValueError) as error:
        return fail(str(error))
    finally:
        for path in temp_paths:
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())


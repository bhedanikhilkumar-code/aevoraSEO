"""Universal skill installer and git repository pull engine for AevoraSEO.

Allows AI agents and users to install and wire the AevoraSEO skill directly via CLI
from either local repository files or the official GitHub repository.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

DEFAULT_GIT_REPO = "https://github.com/bhedanikhilkumar-code/aevoraSEO.git"
DEFAULT_ZIP_URL = "https://github.com/bhedanikhilkumar-code/aevoraSEO/archive/refs/heads/main.zip"

ROOT_FILES = {
    "SKILL.md",
    "README.md",
    "pyproject.toml",
    "package.json",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CITATION.cff",
    ".gitignore",
}
ROOT_DIRS = {"src", "scripts", "references", "playbooks", "docs", "assets", "examples"}
SKIP = {".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".git"}


def bundle_files(source: Path) -> List[Path]:
    """Collect valid bundle files from a clean AevoraSEO source directory."""
    files: List[Path] = []
    source = source.resolve()
    for entry in sorted(source.iterdir()):
        if entry.name not in ROOT_FILES | ROOT_DIRS:
            continue
        if entry.is_symlink():
            raise ValueError(f"Refusing a symlink in the bundle: {entry.name}")
        if entry.name in ROOT_FILES:
            if not entry.is_file():
                raise ValueError(f"Expected a file: {entry.name}")
            files.append(entry)
            continue
        for directory, names, filenames in os.walk(entry, followlinks=False):
            names[:] = sorted(
                n
                for n in names
                if n not in SKIP and not n.startswith(".") and not n.endswith(".egg-info")
            )
            for name in names:
                if (Path(directory) / name).is_symlink():
                    raise ValueError(f"Refusing a symlink in the bundle: {name}")
            for name in sorted(filenames):
                if name.startswith(".") or name.endswith((".pyc", ".pyo")):
                    continue
                path = Path(directory) / name
                if path.is_symlink() or not path.is_file():
                    raise ValueError(f"Expected a regular file: {path.relative_to(source)}")
                files.append(path)
    if not all((source / name).is_file() for name in ("SKILL.md", "pyproject.toml", "LICENSE")):
        raise ValueError("Source is missing required AevoraSEO files (SKILL.md, pyproject.toml, LICENSE).")
    return files


def host_destination(
    host: str,
    workspace: Optional[Path | str] = None,
    profile_home: Optional[Path | str] = None,
    dest: Optional[Path | str] = None,
) -> Path:
    """Resolve destination skill path for the given agent platform or explicit directory."""
    if dest:
        return Path(dest).expanduser().resolve()

    host_key = host.lower().strip() if host else "gemini"
    home = Path.home()

    if profile_home and host_key != "hermes":
        raise ValueError("--profile-home is for Hermes. Use --dest or --workspace for other platforms.")

    if workspace:
        ws = Path(workspace).expanduser().resolve()
        roots = {
            "claude-code": ".claude/skills",
            "claude": ".claude/skills",
            "codex": ".agents/skills",
            "agent": ".agents/skills",
            "chatgpt": ".agents/skills",
            "work": ".agents/skills",
            "cursor": ".agents/skills",
            "windsurf": ".agents/skills",
            "openclaw": "skills",
            "aider": ".aider/skills",
            "copilot": ".github/skills",
            "vscode": ".github/skills",
            "gemini": ".gemini/skills",
            "gemini-cli": ".gemini/skills",
            "antigravity": ".gemini/skills",
            "droid": ".factory/skills",
            "kilocode": ".kilocode/skills",
            "opencode": ".opencode/skills",
            "qwen": ".qwen/skills",
            "jcode": ".jcode/skills",
            "jcode-cli": ".jcode/skills",
            "juni": ".juni/skills",
            "prime-agent": ".prime/skills",
            "prime": ".prime/skills",
            "cai": ".cai/skills",
            "kiro": ".kiro/skills",
        }
        if host_key in roots:
            return ws / roots[host_key] / "aevoraseo"
        return ws / ".agents/skills/aevoraseo"

    # Global user config locations
    if host_key in ("claude-code", "claude"):
        return home / ".claude/skills/aevoraseo"
    if host_key in ("codex", "agent", "chatgpt", "work", "cursor", "windsurf"):
        return home / ".agents/skills/aevoraseo"
    if host_key == "openclaw":
        return (
            Path(os.getenv("OPENCLAW_STATE_DIR") or home / ".openclaw").expanduser()
            / "skills/aevoraseo"
        )
    if host_key == "hermes":
        explicit = profile_home or os.getenv("HERMES_HOME")
        if explicit:
            return Path(explicit).expanduser().resolve() / "skills/aevoraseo"
        base = (
            Path(os.getenv("LOCALAPPDATA") or home / "AppData/Local") / "hermes"
            if sys.platform == "win32"
            else home / ".hermes"
        )
        active = base / "active_profile"
        if active.is_file():
            profile = active.read_text(encoding="utf-8").strip()
            if profile and profile != "default":
                raise ValueError(
                    "Hermes has a named active profile. Supply --profile-home with that profile's "
                    "directory, or run this command from its terminal with HERMES_HOME set."
                )
        return base / "skills/aevoraseo"
    if host_key in ("gemini", "gemini-cli", "antigravity"):
        return home / ".gemini/skills/aevoraseo"
    if host_key in ("copilot", "vscode"):
        return home / ".copilot/skills/aevoraseo"
    if host_key == "opencode":
        return (
            Path(os.getenv("XDG_CONFIG_HOME") or home / ".config").expanduser()
            / "opencode/skills/aevoraseo"
        )
    if host_key in ("droid", "kilocode", "qwen", "jcode", "jcode-cli", "juni", "prime-agent", "prime", "cai", "kiro", "aider"):
        prefix = f".{host_key}" if host_key != "droid" else ".factory"
        return home / f"{prefix}/skills/aevoraseo"

    raise ValueError(f"Unknown host platform: '{host}'. Choose a supported platform or specify --dest.")


def resolve_source(
    source: Optional[Path | str] = None,
    from_git: bool = False,
    git_url: Optional[str] = None,
) -> Tuple[Path, Optional[Callable[[], None]]]:
    """Find local skill source or pull the clean bundle from official Git repo."""
    if source:
        s_path = Path(source).expanduser().resolve()
        if (s_path / "SKILL.md").is_file() and (s_path / "pyproject.toml").is_file():
            return s_path, None
        raise ValueError(f"Specified source path is missing SKILL.md or pyproject.toml: {s_path}")

    # If from_git is False, first probe local candidates
    if not from_git:
        candidates = [
            Path.cwd().resolve(),
            Path(__file__).resolve().parents[3],
            Path.cwd().resolve().parent,
            Path.cwd().resolve().parent.parent,
        ]
        for candidate in candidates:
            if (candidate / "SKILL.md").is_file() and (candidate / "pyproject.toml").is_file():
                return candidate, None

    # Fetch from official GitHub repository
    target_repo = git_url or DEFAULT_GIT_REPO
    temp_dir = tempfile.mkdtemp(prefix="aevoraseo-git-")

    def cleanup():
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

    # Attempt 1: git clone --depth 1
    git_success = False
    try:
        proc = subprocess.run(
            ["git", "clone", "--depth", "1", target_repo, temp_dir],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0 and (Path(temp_dir) / "SKILL.md").is_file():
            git_success = True
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        git_success = False

    if git_success:
        return Path(temp_dir), cleanup

    # Attempt 2: download archive zip via HTTP
    try:
        zip_path = Path(temp_dir) / "aevoraseo-main.zip"
        req = urllib.request.Request(
            DEFAULT_ZIP_URL,
            headers={"User-Agent": "AevoraSEO-CLI-Installer/1.1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp, open(zip_path, "wb") as f:
            shutil.copyfileobj(resp, f)

        extract_dir = Path(temp_dir) / "extracted"
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)

        for child in extract_dir.iterdir():
            if child.is_dir() and (child / "SKILL.md").is_file():
                return child, cleanup

        if (extract_dir / "SKILL.md").is_file():
            return extract_dir, cleanup
    except Exception as err:
        cleanup()
        raise ValueError(
            f"Failed to fetch AevoraSEO skill from git repository ({target_repo}): {err}. "
            "Please clone the repository locally or specify --source."
        )

    cleanup()
    raise ValueError(f"Could not locate AevoraSEO skill bundle in git checkout at {target_repo}.")


def shell_command(arguments: List[Any]) -> str:
    """Format shell command string safely for current operating system."""
    values = [str(a) for a in arguments]
    if os.name == "nt":
        return "& " + " ".join("'" + value.replace("'", "''") + "'" for value in values)
    import shlex
    return shlex.join(values)


def install(
    source: Path,
    destination: Path,
    dry_run: bool = False,
    update: bool = False,
) -> Dict[str, Any]:
    """Copy a clean AevoraSEO skill bundle to destination with SHA-256 receipt."""
    source = source.resolve()
    destination = destination.expanduser().resolve()

    if destination.is_symlink():
        raise ValueError("Destination already exists as a symlink. Choose a regular skill folder.")

    if destination == source or source in destination.parents:
        raise ValueError("Choose a destination outside the source folder.")

    files = bundle_files(source)
    manifest = {
        p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    }
    result: Dict[str, Any] = {
        "destination": str(destination),
        "files": len(files),
        "dry_run": dry_run,
    }
    backup = None

    if destination.exists():
        receipt = destination / "aevoraseo-install.json"
        if not receipt.is_file():
            raise ValueError(
                "Destination already exists without an installation receipt. Preserve it and choose a new folder."
            )
        receipt_data = json.loads(receipt.read_text(encoding="utf-8"))
        old = receipt_data.get("files_sha256", {}) if isinstance(receipt_data, dict) else {}
        if not old or not isinstance(old, dict):
            raise ValueError(
                "Existing installation receipt is invalid. Preserve the folder before reinstalling."
            )
        if os.name == "nt":
            old = {name.replace("\\", "/"): digest for name, digest in old.items()}
        for name, digest in old.items():
            path = destination / name
            if (
                Path(name).is_absolute()
                or ".." in Path(name).parts
                or "\\" in name
                or not path.resolve().is_relative_to(destination.resolve())
                or path.is_symlink()
                or not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest
            ):
                raise ValueError(
                    "Existing installation has changed files. Preserve your edits before updating."
                )
        if old == manifest:
            result["status"] = "already installed"
            return result
        if not update:
            raise ValueError(
                "Destination already exists with a different version. Use --update to keep a backup and replace it."
            )
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        backup = destination.parent.parent / "aevoraseo-backups" / stamp / destination.name
        result["backup"] = str(backup)

    if dry_run:
        result["status"] = "dry_run"
        return result

    if backup:
        backup.parent.mkdir(parents=True, exist_ok=True)
        destination.rename(backup)

    created = False
    try:
        destination.mkdir(parents=True, exist_ok=False)
        created = True
        for path in files:
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            if (
                hashlib.sha256(target.read_bytes()).hexdigest()
                != manifest[path.relative_to(source).as_posix()]
            ):
                raise ValueError("Source changed during installation. Retry from a stable checkout.")
        (destination / "aevoraseo-install.json").write_text(
            json.dumps({"files_sha256": manifest}, indent=2) + "\n", encoding="utf-8"
        )
        previous_runtime = backup / ".venv" if backup else None
        if previous_runtime and previous_runtime.is_dir() and not previous_runtime.is_symlink():
            shutil.copytree(previous_runtime, destination / ".venv", symlinks=True)
            result["runtime_preserved"] = True
    except Exception:
        if created and destination.exists():
            shutil.rmtree(destination, ignore_errors=True)
        if backup and not destination.exists() and backup.exists():
            backup.rename(destination)
        raise

    result["status"] = "updated" if backup else "installed"
    return result


def install_skill(
    source: Optional[Path | str] = None,
    host: Optional[str] = None,
    dest: Optional[Path | str] = None,
    workspace: Optional[Path | str] = None,
    profile_home: Optional[Path | str] = None,
    setup: bool = False,
    http_only: bool = False,
    runtime: Optional[Path | str] = None,
    dry_run: bool = False,
    update: bool = False,
    from_git: bool = False,
    git_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Universal execution point for installing AevoraSEO skill into agent environments."""
    resolved_src, cleanup = resolve_source(source, from_git=from_git, git_url=git_url)
    try:
        destination = host_destination(
            host=host or "gemini",
            workspace=workspace,
            profile_home=profile_home,
            dest=dest,
        )
        if destination.name != "aevoraseo":
            raise ValueError(f"Skill destination folder name must be 'aevoraseo', got '{destination.name}'.")

        res = install(resolved_src, destination, dry_run=dry_run, update=update)
        res["host"] = host or "custom"
        res["source"] = str(resolved_src)

        # Generate workspace adapter instructions or files if workspace was provided
        if workspace and not dry_run:
            ws_path = Path(workspace).expanduser().resolve()
            h_key = (host or "").lower()
            if h_key in ("cursor", "windsurf"):
                cursorrules = ws_path / ".cursorrules"
                if not cursorrules.exists():
                    cursorrules.write_text(
                        "# AevoraSEO Cursor Rules\n\n"
                        "When working on SEO, AEO, GEO, and website optimization:\n"
                        "1. Always follow the evidence-first rules in `.agents/skills/aevoraseo/SKILL.md`.\n"
                        "2. Do not invent search rankings, volume, or citations without empirical data.\n"
                        "3. Run the native engine using `aevoraseo <command>` or `python .agents/skills/aevoraseo/scripts/run.py <command>`.\n"
                        "4. Check engine readiness with `aevoraseo doctor`.\n",
                        encoding="utf-8",
                    )
                    res["workspace_rule_file"] = str(cursorrules)

        # Optional setup of runtime
        if setup and not dry_run:
            setup_script = destination / "scripts/setup.py"
            if setup_script.is_file():
                cmd = [sys.executable, str(setup_script)]
                if http_only:
                    cmd.append("--http-only")
                if runtime:
                    cmd.extend(["--venv", str(Path(runtime).expanduser().resolve())])
                proc = subprocess.run(cmd, capture_output=True, text=True)
                res["setup_executed"] = True
                res["setup_code"] = proc.returncode
                if proc.returncode != 0:
                    res["setup_error"] = proc.stderr

        return res
    finally:
        if cleanup:
            cleanup()

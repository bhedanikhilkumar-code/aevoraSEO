#!/usr/bin/env python3
"""Automated, fast release script for AevoraSEO.

Executes validation, packages the skill bundle with SHA-256 sidecar,
tags git, pushes, and creates a GitHub Release with attached assets using `gh`.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def get_current_version() -> str:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"(.*?)"', pyproject)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1).strip()


def extract_changelog(version: str) -> str:
    changelog_path = ROOT / "CHANGELOG.md"
    if not changelog_path.exists():
        return f"Release {version}"
    content = changelog_path.read_text(encoding="utf-8")
    
    # Try finding section like '## 1.0.0' or '## 1.0.0 — ...'
    pattern = rf"(##\s+{re.escape(version)}[^\n]*\n)(.*?)(?=\n##\s+|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        header = match.group(1).strip()
        body = match.group(2).strip()
        return f"{header}\n\n{body}"
    return f"## Release {version}\n\nSee CHANGELOG.md for details."


def run_cmd(cmd: list[str], cwd=ROOT, check=True) -> subprocess.CompletedProcess:
    print(f"--> Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Override version to release (e.g. 1.0.0)")
    parser.add_argument("--dry-run", action="store_true", help="Build assets without creating git tag or GitHub release")
    parser.add_argument("--skip-push", action="store_true", help="Do not push git commits/tags to origin")
    parser.add_argument("-y", "--yes", action="store_true", help="Automatically confirm prompts (non-interactive mode)")
    parser.add_argument("-f", "--force", action="store_true", help="Force recreate tag at HEAD and update GitHub release notes")
    args = parser.parse_args()

    version = args.version or get_current_version()
    tag = f"v{version}"
    print(f"=== Starting AevoraSEO Release: {tag} ===")

    # 1. Validate skill bundle
    print("1. Validating skill package...")
    val_res = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_skill.py")], cwd=ROOT)
    if val_res.returncode != 0:
        sys.exit(f"Validation failed with code {val_res.returncode}")

    # 2. Build release archive and sha256 outside repository
    print(f"2. Building release archive for {tag}...")
    temp_dir = ROOT.parent / "aevoraseo-release-artifacts"
    temp_dir.mkdir(parents=True, exist_ok=True)
    zip_path = temp_dir / f"aevoraseo-{version}-skill.zip"
    sha_path = temp_dir / f"aevoraseo-{version}-skill.zip.sha256"

    # Remove existing artifacts if any
    if zip_path.exists():
        zip_path.unlink()
    if sha_path.exists():
        sha_path.unlink()

    build_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "build_skill.py"),
        "--out",
        str(zip_path),
    ]
    res = subprocess.run(build_cmd, cwd=ROOT)
    if res.returncode != 0:
        sys.exit(f"Build failed with code {res.returncode}")

    if not zip_path.exists() or not sha_path.exists():
        sys.exit(f"Failed to produce expected files: {zip_path}, {sha_path}")

    print(f"Assets generated successfully:")
    print(f"  - {zip_path} ({zip_path.stat().st_size:,} bytes)")
    print(f"  - {sha_path} ({sha_path.stat().st_size:,} bytes)")

    if args.dry_run:
        print("Dry run completed. Skipping git tagging and GitHub release.")
        return 0

    # 3. Check git status
    print("3. Checking git status...")
    status = run_cmd(["git", "status", "--porcelain"]).stdout.strip()
    if status:
        print("Working directory has unstaged or uncommitted changes:")
        print(status)
        confirm = "y" if args.yes else input("Commit these changes before release? [y/N]: ").strip().lower()
        if confirm == 'y':
            run_cmd(["git", "add", "-A"])
            run_cmd(["git", "commit", "-m", f"chore(release): prepare {tag}"])
        else:
            sys.exit("Aborting release due to uncommitted changes.")

    # 4. Git tag
    print(f"4. Tagging {tag}...")
    # Check if tag already exists locally
    existing_tags = run_cmd(["git", "tag", "-l", tag]).stdout.strip()
    if existing_tags:
        if args.force:
            print(f"Tag {tag} already exists locally. Recreating at current HEAD due to --force...")
            run_cmd(["git", "tag", "-f", "-a", tag, "-m", f"Release {tag}"])
            print(f"Recreated git tag {tag}")
        else:
            print(f"Tag {tag} already exists locally.")
    else:
        run_cmd(["git", "tag", "-a", tag, "-m", f"Release {tag}"])
        print(f"Created git tag {tag}")

    # 5. Push git commits and tags
    if not args.skip_push:
        print("5. Pushing to origin...")
        run_cmd(["git", "push", "origin", "main"])
        if args.force:
            run_cmd(["git", "push", "origin", tag, "--force"])
        else:
            run_cmd(["git", "push", "origin", tag])

    # 6. Extract release notes
    notes = extract_changelog(version)
    notes_file = temp_dir / f"RELEASE_NOTES_{version}.md"
    notes_file.write_text(notes, encoding="utf-8")

    # 7. Check gh CLI availability
    if shutil.which("gh"):
        # Check if release already exists on GitHub
        check_rel = subprocess.run(["gh", "release", "view", tag], capture_output=True, text=True)
        if check_rel.returncode == 0:
            print(f"7. Release {tag} exists on GitHub. Updating assets and notes...")
            if args.force:
                print(f"Updating release title and notes for {tag}...")
                run_cmd([
                    "gh",
                    "release",
                    "edit",
                    tag,
                    "--title",
                    f"AevoraSEO {tag}",
                    "--notes-file",
                    str(notes_file),
                ])
            gh_cmd = [
                "gh",
                "release",
                "upload",
                tag,
                str(zip_path),
                str(sha_path),
                "--clobber",
            ]
            gh_res = run_cmd(gh_cmd)
            print("Release assets updated successfully.")
        else:
            print(f"7. Creating GitHub Release via gh CLI for {tag}...")
            gh_cmd = [
                "gh",
                "release",
                "create",
                tag,
                str(zip_path),
                str(sha_path),
                "--title",
                f"AevoraSEO {tag}",
                "--notes-file",
                str(notes_file),
            ]
            gh_res = run_cmd(gh_cmd)
            print("GitHub Release created successfully:")
            print(gh_res.stdout)
    else:
        print("gh CLI not found. You can upload the assets manually:")
        print(f"  - {zip_path}")
        print(f"  - {sha_path}")

    print(f"=== Successfully published AevoraSEO {tag}! ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

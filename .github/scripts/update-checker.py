#!/usr/bin/env python3
"""
Update checker and updater for Antigravity App and IDE.
Queries Google update channels and updates RPM spec, install.sh, and README.md.
"""

import argparse
import datetime
import json
import os
import re
import sys
import urllib.request

ENDPOINTS = {
    "app": "https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/releases",
    "ide": "https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases",
}


def fetch_latest_release(target: str):
    url = ENDPOINTS[target]
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) update-checker/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        if not data or not isinstance(data, list):
            raise ValueError(f"Invalid response from {url}: {data}")
        return data[0]["version"], str(data[0]["execution_id"])


def get_current_spec_version(spec_path: str) -> str:
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"^Version:\s*([^\s]+)", content, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not find Version field in {spec_path}")
    return match.group(1).strip()


def set_github_output(key: str, value: str):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            if "\n" in value:
                delimiter = f"EOF_{key}"
                f.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{key}={value}\n")
    print(f"[GITHUB_OUTPUT] {key}={value}")


def update_app(repo_dir: str, new_ver: str, exec_id: str):
    spec_path = os.path.join(repo_dir, "antigravity2.spec")
    install_path = os.path.join(repo_dir, "install.sh")
    readme_path = os.path.join(repo_dir, "README.md")

    # 1. Update antigravity2.spec
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = f.read()

    spec = re.sub(r"^Version:\s*.*$", f"Version:        {new_ver}", spec, flags=re.MULTILINE)
    new_src0 = f"Source0:        https://storage.googleapis.com/antigravity-public/antigravity-hub/{new_ver}-{exec_id}/linux-x64/Antigravity.tar.gz#/Antigravity-x64.tar.gz"
    new_src1 = f"Source1:        https://storage.googleapis.com/antigravity-public/antigravity-hub/{new_ver}-{exec_id}/linux-arm/Antigravity.tar.gz#/Antigravity-arm64.tar.gz"
    spec = re.sub(r"^Source0:\s*.*$", new_src0, spec, flags=re.MULTILINE)
    spec = re.sub(r"^Source1:\s*.*$", new_src1, spec, flags=re.MULTILINE)

    # Insert changelog entry
    date_str = datetime.datetime.now().strftime("%a %b %d %Y")
    changelog_entry = (
        f"%changelog\n"
        f"* {date_str} github-actions[bot] <actions@github.com> - {new_ver}-1\n"
        f"- Update to version {new_ver} with new GCS download URLs\n\n"
    )
    spec = spec.replace("%changelog\n", changelog_entry, 1)

    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec)

    # 2. Update install.sh
    with open(install_path, "r", encoding="utf-8") as f:
        install = f.read()

    install = re.sub(r'^VERSION_APP=".*"', f'VERSION_APP="{new_ver}"', install, flags=re.MULTILINE)
    new_url_x64 = f'https://storage.googleapis.com/antigravity-public/antigravity-hub/{new_ver}-{exec_id}/linux-x64/Antigravity.tar.gz'
    new_url_arm = f'https://storage.googleapis.com/antigravity-public/antigravity-hub/{new_ver}-{exec_id}/linux-arm/Antigravity.tar.gz'
    install = re.sub(r'^DOWNLOAD_URL_APP_X64=".*"', f'DOWNLOAD_URL_APP_X64="{new_url_x64}"', install, flags=re.MULTILINE)
    install = re.sub(r'^DOWNLOAD_URL_APP_ARM64=".*"', f'DOWNLOAD_URL_APP_ARM64="{new_url_arm}"', install, flags=re.MULTILINE)

    with open(install_path, "w", encoding="utf-8") as f:
        f.write(install)

    # 3. Update README.md
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    readme = re.sub(
        r'antigravity2-[0-9.]+-',
        f'antigravity2-{new_ver}-',
        readme
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)


def update_ide(repo_dir: str, new_ver: str, exec_id: str):
    spec_path = os.path.join(repo_dir, "antigravity2-ide.spec")
    install_path = os.path.join(repo_dir, "install.sh")
    readme_path = os.path.join(repo_dir, "README.md")

    # 1. Update antigravity2-ide.spec
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = f.read()

    spec = re.sub(r"^Version:\s*.*$", f"Version:        {new_ver}", spec, flags=re.MULTILINE)
    new_src0 = f"Source0:        https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{new_ver}-{exec_id}/linux-x64/Antigravity%20IDE.tar.gz#/Antigravity-IDE-x64.tar.gz"
    new_src1 = f"Source1:        https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{new_ver}-{exec_id}/linux-arm/Antigravity%20IDE.tar.gz#/Antigravity-IDE-arm64.tar.gz"
    spec = re.sub(r"^Source0:\s*.*$", new_src0, spec, flags=re.MULTILINE)
    spec = re.sub(r"^Source1:\s*.*$", new_src1, spec, flags=re.MULTILINE)

    # Insert changelog entry
    date_str = datetime.datetime.now().strftime("%a %b %d %Y")
    changelog_entry = (
        f"%changelog\n"
        f"* {date_str} github-actions[bot] <actions@github.com> - {new_ver}-1\n"
        f"- Update to version {new_ver} with new download URLs\n\n"
    )
    spec = spec.replace("%changelog\n", changelog_entry, 1)

    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec)

    # 2. Update install.sh
    with open(install_path, "r", encoding="utf-8") as f:
        install = f.read()

    install = re.sub(r'^VERSION_IDE=".*"', f'VERSION_IDE="{new_ver}"', install, flags=re.MULTILINE)
    new_url_x64 = f'https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{new_ver}-{exec_id}/linux-x64/Antigravity%20IDE.tar.gz'
    new_url_arm = f'https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{new_ver}-{exec_id}/linux-arm/Antigravity%20IDE.tar.gz'
    install = re.sub(r'^DOWNLOAD_URL_IDE_X64=".*"', f'DOWNLOAD_URL_IDE_X64="{new_url_x64}"', install, flags=re.MULTILINE)
    install = re.sub(r'^DOWNLOAD_URL_IDE_ARM64=".*"', f'DOWNLOAD_URL_IDE_ARM64="{new_url_arm}"', install, flags=re.MULTILINE)

    with open(install_path, "w", encoding="utf-8") as f:
        f.write(install)

    # 3. Update README.md
    with open(readme_path, "r", encoding="utf-8") as f:
        readme = f.read()

    readme = re.sub(
        r'antigravity2-ide-[0-9.]+-',
        f'antigravity2-ide-{new_ver}-',
        readme
    )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)


def main():
    parser = argparse.ArgumentParser(description="Check and update Antigravity specifications")
    parser.add_argument(
        "--target",
        choices=["app", "ide", "all"],
        default="all",
        help="Target component to check (default: all)"
    )
    parser.add_argument("--repo-dir", default=".", help="Repository root directory")
    parser.add_argument("--apply", action="store_true", help="Apply updates to files if an update is available")
    args = parser.parse_args()

    repo_dir = os.path.abspath(args.repo_dir)

    targets_to_check = ["app", "ide"] if args.target == "all" else [args.target]
    updates = {}

    for t in targets_to_check:
        target_name = "Antigravity App" if t == "app" else "Antigravity IDE"
        spec_filename = "antigravity2.spec" if t == "app" else "antigravity2-ide.spec"
        spec_path = os.path.join(repo_dir, spec_filename)

        current_ver = get_current_spec_version(spec_path)
        latest_ver, exec_id = fetch_latest_release(t)

        print(f"[{target_name}] Current local: {current_ver} | Upstream latest: {latest_ver} (execution_id: {exec_id})")

        if current_ver != latest_ver:
            print(f"Update available for {target_name}: {current_ver} -> {latest_ver}")
            updates[t] = {
                "name": target_name,
                "current": current_ver,
                "latest": latest_ver,
                "exec_id": exec_id,
            }
        else:
            print(f"{target_name} is already up to date.")

    if not updates:
        set_github_output("update_needed", "false")
        print("No updates needed.")
        return

    set_github_output("update_needed", "true")

    # Determine title, branch, and PR body
    if "app" in updates and "ide" in updates:
        app_u = updates["app"]
        ide_u = updates["ide"]
        pr_title = f"feat: update Antigravity app to {app_u['latest']} and IDE to {ide_u['latest']}"
        branch_name = f"update/app-{app_u['latest']}-ide-{ide_u['latest']}"
        body_lines = [
            "Automated upstream release update for:",
            f"- **Antigravity App**: `{app_u['current']}` -> `{app_u['latest']}` (Execution ID: `{app_u['exec_id']}`)",
            f"- **Antigravity IDE**: `{ide_u['current']}` -> `{ide_u['latest']}` (Execution ID: `{ide_u['exec_id']}`)",
            "",
            "### Updated Files",
            "- `antigravity2.spec`",
            "- `antigravity2-ide.spec`",
            "- `install.sh`",
            "- `README.md`",
            "",
            "Auto-generated by GitHub Actions workflow in one go.",
        ]
    elif "app" in updates:
        app_u = updates["app"]
        pr_title = f"feat: update Antigravity app to {app_u['latest']}"
        branch_name = f"update/app-{app_u['latest']}"
        body_lines = [
            f"Automated upstream release update for **Antigravity App** to version **{app_u['latest']}** (Execution ID: `{app_u['exec_id']}`).",
            "",
            "### Updated Files",
            "- `antigravity2.spec`",
            "- `install.sh`",
            "- `README.md`",
            "",
            "Auto-generated by GitHub Actions workflow in one go.",
        ]
    else:
        ide_u = updates["ide"]
        pr_title = f"feat: update Antigravity IDE to {ide_u['latest']}"
        branch_name = f"update/ide-{ide_u['latest']}"
        body_lines = [
            f"Automated upstream release update for **Antigravity IDE** to version **{ide_u['latest']}** (Execution ID: `{ide_u['exec_id']}`).",
            "",
            "### Updated Files",
            "- `antigravity2-ide.spec`",
            "- `install.sh`",
            "- `README.md`",
            "",
            "Auto-generated by GitHub Actions workflow in one go.",
        ]

    pr_body = "\n".join(body_lines)
    set_github_output("pr_title", pr_title)
    set_github_output("branch_name", branch_name)
    set_github_output("pr_body", pr_body)

    if args.apply:
        if "app" in updates:
            print(f"Applying update for Antigravity App to {updates['app']['latest']}...")
            update_app(repo_dir, updates["app"]["latest"], updates["app"]["exec_id"])
        if "ide" in updates:
            print(f"Applying update for Antigravity IDE to {updates['ide']['latest']}...")
            update_ide(repo_dir, updates["ide"]["latest"], updates["ide"]["exec_id"])
        print("Files successfully updated.")


if __name__ == "__main__":
    main()

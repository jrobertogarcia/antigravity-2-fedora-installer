#!/usr/bin/env python3
"""
Authoritative dynamic release detection for Google Antigravity (Agent & IDE).
Fetches metadata directly from https://antigravity.google/download using
resilient pattern matching, heuristic fallback, and live URL verification.
"""

import sys
import os
import re
import json
import gzip
import argparse
import urllib.request
import urllib.error

OFFICIAL_DOWNLOAD_PAGE = "https://antigravity.google/download"
FALLBACK_PAGE = "https://antigravity.google"


def fetch_url_content(url, timeout=10):
    """Fetch URL content with gzip decompression support and browser headers."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            data = res.read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            return data.decode("utf-8", errors="ignore")
    except Exception as e:
        sys.stderr.write(f"Network error fetching {url}: {e}\n")
        return None


def verify_url_alive(url, timeout=5):
    """Send a lightweight HEAD request to verify that the download link is active."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        },
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status in (200, 206, 302, 304)
    except urllib.error.HTTPError as e:
        # Some CDNs reject HEAD; fallback to 0-byte range GET
        if e.code in (403, 405):
            try:
                range_req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-0"},
                )
                with urllib.request.urlopen(range_req, timeout=timeout) as res:
                    return res.status in (200, 206)
            except Exception:
                return False
        return False
    except Exception:
        return False


def parse_releases_from_html(html):
    """
    Parse Antigravity Agent and IDE Linux tarball releases from HTML using
    both strict canonical patterns and resilient semantic/heuristic patterns.
    """
    if not html:
        return None

    results = {}

    # --- Layer 1: Canonical Pattern Matching ---
    # 1. Antigravity Agent (Hub)
    hub_matches = re.findall(
        r'https://storage\.googleapis\.com/antigravity-public/antigravity-hub/([0-9]+\.[0-9]+\.[0-9]+)-([0-9]+)/linux-(x64|arm|arm64)/Antigravity\.tar\.gz',
        html,
    )
    for ver, build, arch in hub_matches:
        arch_key = "aarch64" if "arm" in arch else "x86_64"
        if "agent" not in results:
            results["agent"] = {"version": ver, "build": build, "urls": {}}
        results["agent"]["urls"][arch_key] = (
            f"https://storage.googleapis.com/antigravity-public/antigravity-hub/{ver}-{build}/linux-{arch}/Antigravity.tar.gz"
        )

    # 2. Antigravity IDE (Standalone)
    ide_matches = re.findall(
        r'https://edgedl\.me\.gvt1\.com/edgedl/release2/j0qc3/antigravity/stable/([0-9]+\.[0-9]+\.[0-9]+)-([0-9]+)/linux-(x64|arm|arm64)/Antigravity(?:%20|\s+)IDE\.tar\.gz',
        html,
    )
    for ver, build, arch in ide_matches:
        arch_key = "aarch64" if "arm" in arch else "x86_64"
        if "ide" not in results:
            results["ide"] = {"version": ver, "build": build, "urls": {}}
        results["ide"]["urls"][arch_key] = (
            f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{ver}-{build}/linux-{arch}/Antigravity%20IDE.tar.gz"
        )

    # --- Layer 2: Resilient Heuristic Pattern Extractor ---
    # If canonical patterns missed any component (e.g. Google changed CDN hostnames)
    if "agent" not in results or "ide" not in results or len(results.get("agent", {}).get("urls", {})) < 2 or len(results.get("ide", {}).get("urls", {})) < 2:
        all_tar_urls = re.findall(r'https?://[^\s"\'<>]+\.tar\.gz', html)
        for url in all_tar_urls:
            url_clean = url.replace(" ", "%20")
            url_lower = url.lower()

            # Detect architecture
            arch_key = None
            if "arm64" in url_lower or "linux-arm" in url_lower or "aarch64" in url_lower:
                arch_key = "aarch64"
            elif "linux-x64" in url_lower or "x86_64" in url_lower or "amd64" in url_lower:
                arch_key = "x86_64"

            if not arch_key:
                continue

            # Extract semver and optional build id
            ver_match = re.search(r'/([0-9]+\.[0-9]+\.[0-9]+)(?:-([0-9]+))?/', url)
            if not ver_match:
                continue
            ver = ver_match.group(1)
            build = ver_match.group(2) or ""

            # Distinguish between IDE vs Agent (Hub)
            is_ide = "ide" in url_lower
            target_key = "ide" if is_ide else "agent"

            if target_key not in results:
                results[target_key] = {"version": ver, "build": build, "urls": {}}
            if arch_key not in results[target_key]["urls"]:
                results[target_key]["urls"][arch_key] = url_clean

    return results if results else None


def get_latest_releases(verify_live=True):
    """
    Fetch releases directly from the authoritative Google download page.
    """
    # 1. Fetch official download page
    html = fetch_url_content(OFFICIAL_DOWNLOAD_PAGE)
    releases = parse_releases_from_html(html)

    # 2. Fallback to main page if needed
    if not releases or "agent" not in releases or "ide" not in releases:
        fallback_html = fetch_url_content(FALLBACK_PAGE)
        fb_releases = parse_releases_from_html(fallback_html)
        if fb_releases:
            releases = releases or {}
            for k, v in fb_releases.items():
                if k not in releases:
                    releases[k] = v

    if not releases or "agent" not in releases or "ide" not in releases:
        sys.stderr.write("Error: Failed to parse latest releases from authoritative Google sources.\n")
        return None, "error"

    # 3. Verify URLs live if requested
    if verify_live:
        for comp in ("agent", "ide"):
            for arch, url in releases[comp]["urls"].items():
                if not verify_url_alive(url):
                    sys.stderr.write(f"Warning: Discovered {comp} ({arch}) URL {url} failed live verification.\n")

    return releases, "online"


def update_spec_files(releases, repo_dir):
    """
    Automatically updates antigravity2.spec, antigravity2-ide.spec, and install.sh
    to match the latest detected versions.
    """
    agent_ver = releases["agent"]["version"]
    agent_x64 = releases["agent"]["urls"]["x86_64"]
    agent_arm = releases["agent"]["urls"]["aarch64"]

    ide_ver = releases["ide"]["version"]
    ide_x64 = releases["ide"]["urls"]["x86_64"]
    ide_arm = releases["ide"]["urls"]["aarch64"]

    updated_files = []

    # 1. Update antigravity2.spec
    agent_spec_path = os.path.join(repo_dir, "antigravity2.spec")
    if os.path.exists(agent_spec_path):
        with open(agent_spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r"^Version:\s+.*$", f"Version:        {agent_ver}", content, flags=re.MULTILINE)
        content = re.sub(r"^Source0:\s+.*Antigravity-x64\.tar\.gz$", f"Source0:        {agent_x64}#/Antigravity-x64.tar.gz", content, flags=re.MULTILINE)
        content = re.sub(r"^Source1:\s+.*Antigravity-arm64\.tar\.gz$", f"Source1:        {agent_arm}#/Antigravity-arm64.tar.gz", content, flags=re.MULTILINE)

        with open(agent_spec_path, "w", encoding="utf-8") as f:
            f.write(content)
        updated_files.append(agent_spec_path)

    # 2. Update antigravity2-ide.spec
    ide_spec_path = os.path.join(repo_dir, "antigravity2-ide.spec")
    if os.path.exists(ide_spec_path):
        with open(ide_spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r"^Version:\s+.*$", f"Version:        {ide_ver}", content, flags=re.MULTILINE)
        content = re.sub(r"^Source0:\s+.*Antigravity-IDE-x64\.tar\.gz$", f"Source0:        {ide_x64}#/Antigravity-IDE-x64.tar.gz", content, flags=re.MULTILINE)
        content = re.sub(r"^Source1:\s+.*Antigravity-IDE-arm64\.tar\.gz$", f"Source1:        {ide_arm}#/Antigravity-IDE-arm64.tar.gz", content, flags=re.MULTILINE)

        with open(ide_spec_path, "w", encoding="utf-8") as f:
            f.write(content)
        updated_files.append(ide_spec_path)

    # 3. Update install.sh
    install_sh_path = os.path.join(repo_dir, "install.sh")
    if os.path.exists(install_sh_path):
        with open(install_sh_path, "r", encoding="utf-8") as f:
            content = f.read()

        content = re.sub(r'^VERSION_IDE="[^"]*"', f'VERSION_IDE="{ide_ver}"', content, flags=re.MULTILINE)
        content = re.sub(r'^VERSION_AGENT="[^"]*"', f'VERSION_AGENT="{agent_ver}"', content, flags=re.MULTILINE)
        content = re.sub(r'^DOWNLOAD_URL_IDE_X64="[^"]*"', f'DOWNLOAD_URL_IDE_X64="{ide_x64}"', content, flags=re.MULTILINE)
        content = re.sub(r'^DOWNLOAD_URL_IDE_ARM64="[^"]*"', f'DOWNLOAD_URL_IDE_ARM64="{ide_arm}"', content, flags=re.MULTILINE)
        content = re.sub(r'^DOWNLOAD_URL_AGENT_X64="[^"]*"', f'DOWNLOAD_URL_AGENT_X64="{agent_x64}"', content, flags=re.MULTILINE)
        content = re.sub(r'^DOWNLOAD_URL_AGENT_ARM64="[^"]*"', f'DOWNLOAD_URL_AGENT_ARM64="{agent_arm}"', content, flags=re.MULTILINE)

        with open(install_sh_path, "w", encoding="utf-8") as f:
            f.write(content)
        updated_files.append(install_sh_path)

    return updated_files


def main():
    parser = argparse.ArgumentParser(
        description="Authoritative release detector for Google Antigravity Agent & IDE."
    )
    parser.add_argument("--json", action="store_true", help="Output metadata in JSON format")
    parser.add_argument("--env", action="store_true", help="Output metadata as eval-ready shell variables")
    parser.add_argument("--mode", choices=["agent", "ide", "all"], default="all", help="Target component")
    parser.add_argument("--arch", choices=["x86_64", "aarch64", "arm64", "all"], default="all", help="Target architecture")
    parser.add_argument("--update-specs", action="store_true", help="Update spec files and install.sh")
    parser.add_argument("--repo-dir", default=os.path.dirname(os.path.abspath(__file__)), help="Path to repository root")
    parser.add_argument("--no-verify", action="store_true", help="Skip live HTTP HEAD verification")

    args = parser.parse_args()

    releases, source = get_latest_releases(verify_live=not args.no_verify)
    if not releases:
        sys.exit(1)

    if args.update_specs:
        updated = update_spec_files(releases, args.repo_dir)
        print(f"Successfully updated repository files to Agent v{releases['agent']['version']} / IDE v{releases['ide']['version']} from {source}:")
        for u in updated:
            print(f"  - {os.path.relpath(u, args.repo_dir)}")
        return

    if args.json:
        output = {
            "source": source,
            "releases": releases,
        }
        print(json.dumps(output, indent=2))
        return

    if args.env:
        print(f'DETECTED_SOURCE="{source}"')
        print(f'DETECTED_AGENT_VERSION="{releases["agent"]["version"]}"')
        print(f'DETECTED_AGENT_BUILD="{releases["agent"]["build"]}"')
        print(f'DETECTED_AGENT_URL_X64="{releases["agent"]["urls"].get("x86_64", "")}"')
        print(f'DETECTED_AGENT_URL_ARM64="{releases["agent"]["urls"].get("aarch64", "")}"')
        print(f'DETECTED_IDE_VERSION="{releases["ide"]["version"]}"')
        print(f'DETECTED_IDE_BUILD="{releases["ide"]["build"]}"')
        print(f'DETECTED_IDE_URL_X64="{releases["ide"]["urls"].get("x86_64", "")}"')
        print(f'DETECTED_IDE_URL_ARM64="{releases["ide"]["urls"].get("aarch64", "")}"')
        return

    # Default human-readable output
    print(f"Release Source: {source} (Authoritative: {OFFICIAL_DOWNLOAD_PAGE})")
    print("=" * 65)
    for comp in ["agent", "ide"]:
        if args.mode in ("all", comp):
            data = releases.get(comp, {})
            name = "Antigravity Agent (Hub)" if comp == "agent" else "Antigravity IDE (Standalone)"
            print(f"\n[{name}]")
            print(f"  Version: v{data.get('version')}")
            print(f"  Build:   {data.get('build')}")
            print("  Downloads:")
            for arch, url in data.get("urls", {}).items():
                print(f"    - {arch}: {url}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate dashboard/index.html with GitHub Actions badges
for all public, non-archived repositories of kotaoue.
"""

import base64
import html
import json
import os
import re
import subprocess

OWNER = "kotaoue"
OUTPUT_FILE = "dashboard/index.html"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Actions Dashboard</title>
  <link rel="stylesheet" href="style.css">
  <script src="theme.js"></script>
</head>
<body>
  <h1>Actions Dashboard</h1>
  <p>GitHub Actions status dashboard for all repositories.</p>
  <table>
    <thead>
      <tr><th>Repository</th><th>Status</th></tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>
"""


def gh_api(path):
    """Run gh api command and return parsed JSON, or None on error."""
    result = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def gh_api_paginate(path, jq_filter):
    """Run gh api with pagination, applying a jq filter, and return lines."""
    result = subprocess.run(
        ["gh", "api", "--paginate", "--jq", jq_filter, path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def get_public_repos():
    """Return sorted list of public, non-archived repo names for OWNER."""
    names = gh_api_paginate(
        f"/users/{OWNER}/repos",
        '.[] | select(.private == false and .archived == false) | .name',
    )
    return sorted(names)


def get_workflow_files(repo):
    """Return sorted list of workflow filenames (.yml/.yaml) for a repo."""
    data = gh_api(f"/repos/{OWNER}/{repo}/contents/.github/workflows")
    if not isinstance(data, list):
        return []
    return sorted(
        entry["name"]
        for entry in data
        if isinstance(entry, dict)
        and entry.get("name", "").endswith((".yml", ".yaml"))
    )


def get_workflow_name(repo, workflow_file):
    """Return the 'name:' field from a workflow file, falling back to filename stem."""
    data = gh_api(
        f"/repos/{OWNER}/{repo}/contents/.github/workflows/{workflow_file}"
    )
    if isinstance(data, dict) and "content" in data:
        try:
            content = base64.b64decode(data["content"]).decode("utf-8")
            match = re.search(
                r'^name:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE
            )
            if match:
                name = match.group(1).strip().strip("'\"").strip()
                if name:
                    return name
        except Exception:
            pass
    return os.path.splitext(workflow_file)[0]


def generate_row(repo, workflow_file, workflow_name):
    """Return an HTML table row for a single workflow badge."""
    safe_name = html.escape(workflow_name)
    base_url = f"https://github.com/{OWNER}/{repo}"
    workflow_url = f"{base_url}/actions/workflows/{workflow_file}"
    badge_url = f"{workflow_url}/badge.svg"
    return (
        f'      <tr>'
        f'<td><a href="{base_url}">{repo}</a></td>'
        f'<td><a href="{workflow_url}">'
        f'<img src="{badge_url}" alt="{safe_name}"></a></td>'
        f'</tr>'
    )


def main():
    print(f"Fetching public repos for {OWNER}...")
    repos = get_public_repos()
    print(f"Found {len(repos)} public repo(s)")

    rows = []
    for repo in repos:
        workflow_files = get_workflow_files(repo)
        if not workflow_files:
            continue
        print(f"  {repo}: {len(workflow_files)} workflow(s)")
        for workflow_file in workflow_files:
            name = get_workflow_name(repo, workflow_file)
            rows.append(generate_row(repo, workflow_file, name))

    output_dir = os.path.dirname(OUTPUT_FILE)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    content = HTML_TEMPLATE.format(rows="\n".join(rows))
    with open(OUTPUT_FILE, "w", newline="\n") as fh:
        fh.write(content)

    print(f"\nWrote {len(rows)} badge row(s) to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

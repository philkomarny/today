#!/usr/bin/env python3
"""
post_intel_to_slack.py — Posts the Industry Intel section from today's briefing to Slack.

Usage:
    python3 scripts/post_intel_to_slack.py              # posts today's intel
    python3 scripts/post_intel_to_slack.py 2026-03-09   # posts a specific date's intel

Requires: pip install requests
Environment: SLACK_WEBHOOK_URL in .env file
"""

import sys
import re
import json
import os
import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip3 install requests")
    sys.exit(1)

VAULT_DIR = Path(__file__).parent.parent
ENV_FILE = VAULT_DIR / ".env"


def load_env():
    """Load variables from .env file."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
    return env


def extract_industry_intel(briefing_path):
    """Extract the Industry Intel section from a briefing markdown file."""
    if not briefing_path.exists():
        return None

    content = briefing_path.read_text()

    match = re.search(
        r"## Industry Intel\s*\n(.*?)(?=\n## |\n---\s*\n|\Z)",
        content,
        re.DOTALL,
    )
    if not match:
        return None

    return match.group(1).strip()


def parse_bullet_line(line):
    """Parse a markdown bullet line into rich_text_section elements."""
    line = re.sub(r"^- ", "", line)

    line = re.sub(
        r"\*\(\[([^\]]+)\]\(([^)]+)\)\)\*",
        r"__ILINK__\1__IURL__\2__IEND__",
        line,
    )

    elements = []
    remaining = line
    while remaining:
        bold_match = re.search(r"\*\*(.+?)\*\*", remaining)
        italic_match = re.search(r"(?<!\*)\*([^*]+)\*(?!\*)", remaining)
        link_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", remaining)
        ilink_match = re.search(r"__ILINK__(.+?)__IURL__(.+?)__IEND__", remaining)

        candidates = []
        if bold_match:
            candidates.append((bold_match.start(), bold_match, "bold"))
        if italic_match:
            candidates.append((italic_match.start(), italic_match, "italic"))
        if link_match:
            candidates.append((link_match.start(), link_match, "link"))
        if ilink_match:
            candidates.append((ilink_match.start(), ilink_match, "ilink"))

        if candidates:
            candidates.sort(key=lambda x: x[0])
            _, next_match, match_type = candidates[0]

            if next_match.start() > 0:
                elements.append({"type": "text", "text": remaining[: next_match.start()]})

            if match_type == "link":
                elements.append(
                    {
                        "type": "link",
                        "url": next_match.group(2),
                        "text": next_match.group(1),
                    }
                )
            elif match_type == "ilink":
                elements.append({"type": "text", "text": "("})
                elements.append(
                    {
                        "type": "link",
                        "url": next_match.group(2),
                        "text": next_match.group(1),
                        "style": {"italic": True},
                    }
                )
                elements.append({"type": "text", "text": ")"})
            else:
                elements.append(
                    {
                        "type": "text",
                        "text": next_match.group(1),
                        "style": {"bold": True} if match_type == "bold" else {"italic": True},
                    }
                )
            remaining = remaining[next_match.end() :]
        else:
            elements.append({"type": "text", "text": remaining})
            break

    return elements


def build_rich_text_blocks(intel_text, date_str):
    """Build Slack rich_text blocks from the Industry Intel markdown."""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Industry Intel — {date_str}",
                "emoji": True,
            },
        },
    ]

    source_match = re.search(r"\*Sources?:.*?\*", intel_text)
    if source_match:
        source_text = source_match.group(0).strip("*")
        blocks.append(
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"_{source_text}_"}],
            }
        )

    body = intel_text
    if source_match:
        body = body.replace(source_match.group(0), "")

    # Strip meeting tie-ins — internal context
    body = re.sub(
        r"\*\*Meeting tie-ins?:\*\*\s*\n(?:- .*\n?)*",
        "",
        body,
    )

    # Split into sections by ### headers
    section_pattern = re.compile(r"^###\s+(.+)$", re.MULTILINE)
    parts = section_pattern.split(body)

    # Handle intro text
    intro = parts[0].strip()
    if intro:
        intro_elements = []
        for line in intro.split("\n"):
            line = line.strip()
            if not line:
                continue
            bl_match = re.match(r"\*\*(.+?)\*\*\s*(.*)", line)
            if bl_match:
                intro_elements.append(
                    {"type": "text", "text": bl_match.group(1), "style": {"bold": True}}
                )
                if bl_match.group(2):
                    intro_elements.append(
                        {"type": "text", "text": " " + bl_match.group(2)}
                    )
            else:
                if intro_elements:
                    intro_elements.append({"type": "text", "text": " " + line})
                else:
                    intro_elements.append({"type": "text", "text": line})

        if intro_elements:
            blocks.append(
                {
                    "type": "rich_text",
                    "elements": [
                        {"type": "rich_text_section", "elements": intro_elements}
                    ],
                }
            )

    # Process each section
    for i in range(1, len(parts), 2):
        header_name = parts[i].strip()
        section_body = parts[i + 1].strip() if i + 1 < len(parts) else ""

        if not section_body:
            continue

        blocks.append({"type": "divider"})

        rt_elements = []

        rt_elements.append(
            {
                "type": "rich_text_section",
                "elements": [
                    {"type": "text", "text": header_name, "style": {"bold": True}}
                ],
            }
        )

        bullet_items = []
        for line in section_body.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                bullet_items.append(parse_bullet_line(line))

        if bullet_items:
            rt_elements.append(
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "elements": [
                        {"type": "rich_text_section", "elements": item}
                        for item in bullet_items
                    ],
                }
            )

        non_bullet_lines = [
            l.strip()
            for l in section_body.split("\n")
            if l.strip() and not l.strip().startswith("- ")
        ]
        if non_bullet_lines and not bullet_items:
            rt_elements.append(
                {
                    "type": "rich_text_section",
                    "elements": [
                        {"type": "text", "text": "\n".join(non_bullet_lines)}
                    ],
                }
            )

        blocks.append({"type": "rich_text", "elements": rt_elements})

    # Footer
    blocks.append({"type": "divider"})
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Posted from Daily Briefing system",
                }
            ],
        }
    )

    return blocks


def post_to_slack(webhook_url, blocks):
    """Post blocks to Slack via incoming webhook."""
    payload = {"blocks": blocks}
    resp = requests.post(
        webhook_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"ERROR: Slack returned {resp.status_code}: {resp.text}")
        return False
    print("Posted to Slack successfully.")
    return True


def main():
    env = load_env()
    webhook_url = env.get("SLACK_WEBHOOK_URL") or os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("ERROR: SLACK_WEBHOOK_URL not found in .env or environment")
        sys.exit(1)

    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = datetime.date.today().isoformat()

    briefing_path = VAULT_DIR / "output" / "briefings" / f"{date_str}-briefing.md"
    print(f"Reading intel from {briefing_path}...")

    intel_text = extract_industry_intel(briefing_path)
    if not intel_text:
        print(f"No Industry Intel section found in {briefing_path}")
        sys.exit(1)

    blocks = build_rich_text_blocks(intel_text, date_str)
    post_to_slack(webhook_url, blocks)


if __name__ == "__main__":
    main()

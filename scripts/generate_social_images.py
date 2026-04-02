#!/usr/bin/env python3
"""Generate social media post images using OpenRouter API.

Usage:
    python3 scripts/generate_social_images.py --post 3                  # single post, today
    python3 scripts/generate_social_images.py --post 3 2026-03-29       # single post, specific date
    python3 scripts/generate_social_images.py                           # all posts

Reads image_prompt fields from social posts markdown and generates images
using OpenRouter (Gemini 3 Pro).

Requires OPENROUTER_API_KEY in .env file.
"""

import sys
import re
import json
import base64
import os
import requests
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
MODEL = "google/gemini-3-pro-image-preview"


def load_api_key() -> str:
    """Load OpenRouter API key from .env file or environment."""
    # Check environment first
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key:
        return key

    # Check .env files
    for parent in [VAULT, VAULT.parent, Path.home()]:
        env_file = parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip("'\"")
                    key = key.split()[0] if key else ""
                    return key
    print("No OPENROUTER_API_KEY found in .env or environment.")
    print("Get one at https://openrouter.ai")
    sys.exit(1)


def generate_image(prompt: str, output_path: Path, api_key: str) -> bool:
    """Generate an image using OpenRouter API."""
    print(f"  Generating: {output_path.name}")
    print(f"  Prompt: {prompt[:80]}...")

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        },
        timeout=120,
    )

    if resp.status_code != 200:
        print(f"  FAILED: {resp.status_code} — {resp.text[:200]}")
        return False

    data = resp.json()

    try:
        for choice in data.get("choices", []):
            msg = choice.get("message", {})

            for img in msg.get("images", []):
                if isinstance(img, dict) and img.get("type") == "image_url":
                    url = img["image_url"]["url"]
                    if url.startswith("data:"):
                        _, b64data = url.split(",", 1)
                        output_path.write_bytes(base64.b64decode(b64data))
                        print(f"  Saved: {output_path}")
                        return True

            content = msg.get("content")
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "image_url":
                        url = part["image_url"]["url"]
                        if url.startswith("data:"):
                            _, b64data = url.split(",", 1)
                            output_path.write_bytes(base64.b64decode(b64data))
                            print(f"  Saved: {output_path}")
                            return True
            elif isinstance(content, str) and "data:image" in content:
                match = re.search(r"data:image/\w+;base64,([A-Za-z0-9+/=]+)", content)
                if match:
                    output_path.write_bytes(base64.b64decode(match.group(1)))
                    print(f"  Saved: {output_path}")
                    return True

    except Exception as e:
        print(f"  FAILED to parse response: {e}")
        return False

    print(f"  FAILED: No image found in response")
    return False


def extract_prompts(posts_file: Path) -> dict[int, str]:
    """Extract image_prompt fields from a social posts markdown file."""
    content = posts_file.read_text()
    prompts = {}

    sections = re.split(r"### (?:LI|X)-\d+:", content)
    headers = re.findall(r"### ((?:LI|X)-(\d+)):", content)

    for i, (header_full, num_str) in enumerate(headers):
        section = sections[i + 1] if i + 1 < len(sections) else ""
        prompt_match = re.search(r'image_prompt:\s*["\'](.+?)["\']', section)
        if prompt_match:
            num = int(num_str)
            if header_full.startswith("X-"):
                num += 5
            prompts[num] = prompt_match.group(1)

    return prompts


def main():
    target_date = None
    single_post = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--post" and i + 1 < len(args):
            single_post = int(args[i + 1])
            i += 2
        elif not args[i].startswith("-"):
            target_date = args[i]
            i += 1
        else:
            i += 1

    if not target_date:
        target_date = date.today().isoformat()

    posts_file = VAULT / "output" / "social-posts" / f"{target_date}-social-posts.md"
    images_dir = VAULT / "output" / "images"
    images_dir.mkdir(exist_ok=True)

    if not posts_file.exists():
        print(f"No posts file found: {posts_file}")
        sys.exit(1)

    api_key = load_api_key()
    prompts = extract_prompts(posts_file)

    if not prompts:
        print("No image_prompt fields found in the posts file.")
        sys.exit(1)

    if single_post:
        if single_post not in prompts:
            print(f"No image_prompt found for post {single_post}")
            print(f"Available: {sorted(prompts.keys())}")
            sys.exit(1)
        prompts = {single_post: prompts[single_post]}

    print(f"Generating {len(prompts)} image(s) for {target_date}\n")

    success = 0
    for num, prompt in sorted(prompts.items()):
        output = images_dir / f"{target_date}-social-{num}.png"
        if generate_image(prompt, output, api_key):
            success += 1
        print()

    print(f"Done: {success}/{len(prompts)} images generated")


if __name__ == "__main__":
    main()

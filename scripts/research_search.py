#!/usr/bin/env python3
"""
research_search.py — Daily search for new academic papers.
Queries arXiv based on config/research_keywords.yaml.
Outputs a daily digest markdown file.

Usage: python3 scripts/research_search.py

Requires: pip install arxiv pyyaml
"""

import os
import yaml
import datetime
import json
import hashlib
from pathlib import Path

VAULT_DIR = Path(__file__).parent.parent
CONFIG_PATH = VAULT_DIR / "config" / "research_keywords.yaml"
DIGESTS_DIR = VAULT_DIR / "research" / "digests"
SEEN_FILE = VAULT_DIR / "research" / ".seen_papers.json"

today = datetime.date.today()


def load_config():
    """Load research topics from config."""
    if not CONFIG_PATH.exists():
        print(f"No config found at {CONFIG_PATH}.")
        print("Run /today first — the setup wizard will create your research keywords.")
        return {"topics": []}

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f) or {"topics": []}


def load_seen():
    """Load the set of paper IDs we've already shown."""
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    """Save the set of seen paper IDs."""
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def paper_id(title, authors_str):
    """Generate a unique ID for a paper."""
    key = f"{title.lower().strip()}|{authors_str.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def search_arxiv(keywords, max_results=5):
    """Search arXiv for papers matching keywords."""
    try:
        import arxiv
    except ImportError:
        print("arxiv package not installed. Run: pip install arxiv")
        return []

    results = []
    for kw in keywords:
        try:
            search = arxiv.Search(
                query=kw,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )
            client = arxiv.Client()
            for paper in client.results(search):
                authors = ", ".join(a.name for a in paper.authors[:3])
                if len(paper.authors) > 3:
                    authors += " et al."

                results.append(
                    {
                        "title": paper.title,
                        "authors": authors,
                        "abstract": paper.summary[:300] + "..."
                        if len(paper.summary) > 300
                        else paper.summary,
                        "url": paper.entry_id,
                        "pdf_url": paper.pdf_url,
                        "published": paper.published.strftime("%Y-%m-%d"),
                        "source": "arXiv",
                        "id": paper_id(paper.title, authors),
                    }
                )
        except Exception as e:
            print(f"Error searching arXiv for '{kw}': {e}")

    return results


def generate_digest(config):
    """Generate the daily research digest markdown file."""
    seen = load_seen()
    all_papers = {}

    for topic in config.get("topics", []):
        name = topic["name"]
        keywords = topic.get("keywords", [])
        sources = topic.get("sources", ["arxiv"])
        papers = []

        if "arxiv" in sources:
            arxiv_papers = search_arxiv(keywords, max_results=3)
            for p in arxiv_papers:
                if p["id"] not in seen:
                    papers.append(p)
                    seen.add(p["id"])

        if papers:
            all_papers[name] = papers

    # Build markdown
    lines = []
    lines.append(f"# Research Digest — {today.strftime('%B %-d, %Y')}")
    lines.append("")

    if not all_papers:
        lines.append("*No new papers found today. Try expanding your keywords in `config/research_keywords.yaml`.*")
    else:
        lines.append("## New Papers")
        lines.append("")
        for topic_name, papers in all_papers.items():
            lines.append(f"### {topic_name}")
            for p in papers:
                lines.append(f"- **\"{p['title']}\"**")
                lines.append(f"  - Authors: {p['authors']} ({p['published']})")
                lines.append(f"  - Source: {p['source']}")
                lines.append(f"  - [View Paper]({p['url']})")
                if p.get("pdf_url"):
                    lines.append(f"  - [Download PDF]({p['pdf_url']})")
                lines.append(f"  - *{p['abstract']}*")
                lines.append("")
            lines.append("")

    # Write digest file
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DIGESTS_DIR / f"{today.isoformat()}.md"
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    save_seen(seen)

    paper_count = sum(len(p) for p in all_papers.values())
    print(f"Research digest generated: {output_path}")
    print(f"  {paper_count} new papers across {len(all_papers)} topics")

    return output_path


if __name__ == "__main__":
    config = load_config()
    if config.get("topics"):
        generate_digest(config)
    else:
        print("No research topics configured. Run /today to set up.")

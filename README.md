# Get Your Own /today

A daily AI-powered intelligence briefing system built on [Claude Code](https://claude.ai/claude-code). Ten specialized agents gather news, research, social trends, legal developments, and your calendar — then assemble everything into a personalized briefing with social posts and an interactive dashboard.

## What You Get

Every morning, one command (`/today`) runs a 10-agent pipeline:

1. **Research Agent** — Pulls academic papers from arXiv matching your interests
2. **Calendar Agent** — Fetches your schedule (supports Google, Outlook, Apple, or none)
3. **Intel Agent** — Scans 20+ news sources, deduplicates against yesterday
4. **Social Agent** — Monitors influencers across 6 platforms, scores trends
5. **Legal Agent** — Searches court filings and rulings in your domain
6. **Briefing Agent** — Assembles everything into a structured daily briefing
7. **Social Posts Agent** — Generates ready-to-publish posts from today's trends
8. **Self-Update Agent** — Learns from each run, tunes sources and scoring
9. **Dashboard Agent** — Regenerates an interactive HTML dashboard
10. **Publish Agent** — Pushes to GitHub/Vercel (optional)

The system improves itself daily — bad sources get paused, new ones get discovered, scoring weights adapt.

## Quick Start

### Prerequisites

- [Claude Code](https://claude.ai/claude-code) installed and working
- Python 3.10+ with pip
- A topic domain you care about (the setup wizard will ask)

### Install

```bash
# 1. Copy this folder as "daily-briefing" into your working directory
cp -r DISTRO /path/to/your/project/daily-briefing

# 2. Copy the Claude Code command so /today works
mkdir -p /path/to/your/project/.claude/commands
cp daily-briefing/.claude/commands/today.md /path/to/your/project/.claude/commands/today.md

# 3. Copy the Claude Code permissions
cp daily-briefing/.claude/settings.local.json /path/to/your/project/.claude/settings.local.json

# 4. Install Python dependencies
pip3 install arxiv pyyaml requests

# 5. Set up your environment
cp daily-briefing/.env.example daily-briefing/.env
# Edit .env with your API keys

# 6. Run it
cd /path/to/your/project
claude
# Then type: /today
```

**On first run**, the system detects empty configs and walks you through setup:
- **Your domain** — What industry/topic do you want intelligence on?
- **Your calendar** — Which provider? (Google Calendar works out of the box with Claude Code's built-in MCP. Outlook needs Azure credentials. Apple Calendar uses an ICS feed. Or skip it.)
- **Your voice** — How do you write on social media?
- **Your mission areas** — What products/projects should intel map to?

It then auto-generates starter configs (news sources, influencers, research keywords, legal queries) tailored to your domain and runs the first briefing.

### Environment Variables

| Variable | Required? | Used By |
|----------|-----------|---------|
| `ANTHROPIC_API_KEY` | Yes (Claude Code needs it) | Runtime |
| `FIRECRAWL_API_KEY` | Recommended | Intel, Social, Legal agents (web scraping) |
| `OPENROUTER_API_KEY` | Optional | Social post image generation |
| `SLACK_WEBHOOK_URL` | Optional | Post intel to Slack |
| `VAULT_PASSPHRASE` | Optional | Dashboard password protection |

Calendar credentials are configured during the first-run setup wizard.

## How It Works

```
config/*.yaml → [5 gather agents] → output/.staging/*.json → [assembly agents] → output/briefings/ + output/dashboard/
                                                                      ↓
                                                             config/*.yaml (self-update writes back)
```

Each agent reads a config, fetches data, writes a staging JSON with a standard contract, and reports its status. The briefing agent combines everything. The self-update agent makes the whole system smarter over time.

### Mission Board

While running, you see a live status display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DAILY BRIEFING — 2026-04-02 — IN PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 PHASE 1: GATHER INTELLIGENCE
 ├─ 🟢 Research         ✓  14 papers pulled
 ├─ 🟢 Calendar         ✓  5 events loaded
 ├─ ⏳ Intel            …  Fetching sources (8/13)
 ├─ ⬜ Social           ·  Waiting
 └─ ⬜ Legal            ·  Waiting

 PHASE 2: ASSEMBLE
 ├─ ⬜ Briefing         ·  Waiting
 └─ ⬜ Social Posts     ·  Waiting

 PHASE 3: LEARN & PUBLISH
 ├─ ⬜ Self-Update      ·  Waiting
 ├─ ⬜ Dashboard        ·  Waiting
 └─ ⬜ Publish          ·  Waiting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Customization

### Change your domain

Edit these files to shift to any industry:

| File | What to change |
|------|---------------|
| `config/mission.yaml` | Your products/projects and mission areas |
| `config/intel_sources.yaml` | News sources for your industry |
| `config/social_sources.yaml` | Influencers and companies to track |
| `config/research_keywords.yaml` | arXiv search terms |
| `config/legal_queries.yaml` | Court search queries |
| `config/voice.md` | Your writing style for social posts |

### Add/remove agents

Each agent is a standalone markdown file in `commands/agents/`. The orchestrator (`commands/today-v2.md`) reads and executes them in order. Add a new `.md` file, add it to the orchestrator's phase list, done.

## Architecture

| Agent | Config File | Output |
|-------|------------|--------|
| research | `config/research_keywords.yaml` | `research.json` |
| calendar | `config/calendar_config.yaml` | `calendar.json` |
| intel | `config/intel_sources.yaml` | `intel.json` |
| social | `config/social_sources.yaml` | `social.json` |
| legal | `config/legal_queries.yaml` | `legal.json` |
| briefing | `config/briefing_prefs.yaml` | `briefing-meta.json` |
| social-posts | `config/post_performance.yaml` | `posts-meta.json` |
| self-update | All configs | `updates.json` |
| dashboard | Templates | Dashboard HTML |
| publish | `scripts/sync_dashboard.sh` | `ops.json` |

## Cost

Each `/today` run uses roughly $1-3 of Claude API credits depending on how many sources are fetched and how much content is processed.

## Credits

Built by [Phil Komarny](https://www.linkedin.com/in/philkomarny/) using Claude Code. Open-sourced so anyone can have their own AI-powered daily briefing.

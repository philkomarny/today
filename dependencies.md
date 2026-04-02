# Dependencies & Setup Requirements

Everything the agent system needs to run.

---

## Environment Variables

Set these in your `.env` file (copy `.env.example` to get started).

| Variable | Required? | Used By |
|----------|-----------|---------|
| `ANTHROPIC_API_KEY` | Yes (Claude Code needs it) | Runtime |
| `FIRECRAWL_API_KEY` | Recommended | Intel, Social, Legal agents (web scraping) |
| `OPENROUTER_API_KEY` | Optional | Social post image generation |
| `SLACK_WEBHOOK_URL` | Optional | Post intel to Slack |
| `VAULT_PASSPHRASE` | Optional | Dashboard password protection |
| `MS_CLIENT_ID` | If using Outlook | Calendar agent |
| `MS_TENANT_ID` | If using Outlook | Calendar agent |
| `MS_CLIENT_SECRET` | If using Outlook | Calendar agent |
| `MS_USER_EMAIL` | If using Outlook | Calendar agent |

---

## External Services & APIs

### Tier 1: Core (briefing won't work without these)

| Service | Auth Method | Agent(s) | Notes |
|---------|-----------|----------|-------|
| **Anthropic Claude** | `ANTHROPIC_API_KEY` | All (runtime) | The engine |
| **ArXiv API** | None (public) | `research` | Free, no key needed |
| **WebSearch** | Built-in Claude tool | `intel`, `social`, `legal` | For paywalled sites and social sweeps |

### Tier 2: Enhanced (briefing works without, but degraded)

| Service | Auth Method | Agent(s) | Notes |
|---------|-----------|----------|-------|
| **Firecrawl** | `FIRECRAWL_API_KEY` | `intel`, `social`, `legal` | Web scraping. Falls back to WebFetch/WebSearch. |
| **Calendar provider** | Varies | `calendar` | Google (MCP), Outlook (Graph API), or ICS feed |
| **Perplexity Search** | MCP skill | `social` | Multi-platform social sweeps. Falls back to WebSearch. |
| **OpenRouter** | `OPENROUTER_API_KEY` | `social-posts` | Image generation. Optional. |

### Tier 3: Distribution (post-briefing)

| Service | Auth Method | Agent(s) | Notes |
|---------|-----------|----------|-------|
| **Slack Webhook** | `SLACK_WEBHOOK_URL` | `publish` | Posts intel to Slack channel |
| **GitHub** | Local SSH keys | `publish` | Pushes dashboard (optional) |
| **Vercel/Netlify** | Auto-deploy on push | `publish` | Hosts dashboard (optional) |

---

## Python Packages

```bash
pip3 install arxiv pyyaml requests
```

For Outlook calendar, also install:
```bash
pip3 install msal
```

---

## Claude Code Permissions

The system needs these tools allowed in `.claude/settings.local.json`:

- **Bash commands** for Python scripts
- **WebFetch** for news domains in your `intel_sources.yaml`
- **WebSearch** for social and legal sweeps
- **MCP tools** for Google Calendar (if using Google)

The first-run setup will prompt you to approve these as needed.

---

## Local File Dependencies

| File | Purpose | Agent(s) |
|------|---------|----------|
| Previous day's briefing | Dedup (don't repeat stories) | `intel`, `social`, `legal` |
| `config/mission.yaml` | Your domain, products, mission areas | All agents |
| `config/voice.md` | Your writing style | `social-posts` |
| `config/intel_sources.yaml` | Which news sites to fetch | `intel` |
| `config/social_sources.yaml` | Which influencers to monitor | `social` |
| `config/relevance_index.yaml` | Source scoring data | `intel`, `social`, `self-update` |
| `config/research_keywords.yaml` | arXiv search keywords | `research` |

---

## Cost

Each `/today` run costs pennies in API credits. A full month of daily runs has been measured at under **$0.50 total** using Claude Haiku. Cost varies by model — Opus will cost more, but even heavy usage stays well under $5/month.

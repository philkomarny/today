# Get Your Own /today — Agent Architecture

## Quick Reference

| Agent | File | Config It Owns | Staging Output |
|-------|------|---------------|----------------|
| research | `commands/agents/research.md` | `config/research_keywords.yaml` | `research.json` |
| calendar | `commands/agents/calendar.md` | `config/calendar_config.yaml` | `calendar.json` |
| intel | `commands/agents/intel.md` | `config/intel_sources.yaml` | `intel.json` |
| social | `commands/agents/social.md` | `config/social_sources.yaml` | `social.json` |
| legal | `commands/agents/legal.md` | `config/legal_queries.yaml` | `legal.json` |
| briefing | `commands/agents/briefing.md` | `config/briefing_prefs.yaml` | `briefing-meta.json` |
| social-posts | `commands/agents/social-posts.md` | `config/post_performance.yaml` | `posts-meta.json` |
| self-update | `commands/agents/self-update.md` | All configs | `updates.json` |
| dashboard | `commands/agents/dashboard.md` | Templates | Dashboard HTML |
| publish | `commands/agents/publish.md` | `scripts/sync_dashboard.sh` | `ops.json` |

## Adding a Feature

| If you want to... | Edit these |
|-------------------|------------|
| Add a news source | `config/intel_sources.yaml` (or let self-update do it) |
| Add a social influencer | `config/social_sources.yaml` (or let self-update do it) |
| Change briefing section order | `config/briefing_prefs.yaml` |
| Add a research topic | `config/research_keywords.yaml` |
| Change social post voice/count | `config/voice.md` + `commands/agents/social-posts.md` |
| Add a new legal search query | `config/legal_queries.yaml` |
| Add a new briefing section | `commands/agents/briefing.md` |
| Change scoring formula | `commands/agents/self-update.md` (Step 7) |
| Track a new product | `config/mission.yaml` |
| Add a whole new intelligence source type | Create a new agent in `commands/agents/`, add to orchestrator |

## Data Flow

```
config/*.yaml → [tier-1 agents] → output/.staging/*.json → [tier-2 agents] → output/briefings/ + output/dashboard/
                                                                    ↓
                                                           config/*.yaml (self-update writes back)
```

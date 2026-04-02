Generate my full daily briefing using the modular agent system. Run these phases in order.

**Base path:** `daily-briefing`

## First-Run Setup Detection

Before starting, check if `daily-briefing/config/mission.yaml` has empty values (domain, products, mission_areas). If so, this is a first run — execute the setup wizard:

1. **Ask:** "What industry or domain do you want intelligence on?" → Write to `mission.yaml`
2. **Ask:** "What products or projects are you building? (or skip)" → Write to `mission.yaml`
3. **Ask:** "What are your key mission areas or strategic themes?" → Write to `mission.yaml`
4. **Ask:** "Which calendar provider do you use? (Google / Outlook / Apple Calendar / None)"
   - **Google:** "Great — I'll use Claude Code's built-in Google Calendar MCP. No extra setup needed."
   - **Outlook:** "I'll need your Microsoft Azure app credentials. Do you have a CLIENT_ID, TENANT_ID, CLIENT_SECRET, and email? (These go in your .env file)" → Guide them to set env vars, update `calendar_config.yaml`
   - **Apple Calendar:** "Apple Calendar doesn't have a public API, but you can export an ICS feed URL from iCloud. Want to set that up?" → Guide them to get ICS URL
   - **None:** "No problem — the calendar section will be skipped. You can add one later in `config/calendar_config.yaml`."
   - **Save their choice** to `config/calendar_config.yaml` so you remember it next run.
5. **Populate starter configs:**
   - Generate 10-15 intel sources for their domain → `intel_sources.yaml`
   - Generate 10-15 social influencers for their domain → `social_sources.yaml`
   - Generate research keywords for their domain → `research_keywords.yaml`
   - Generate legal search queries for their domain → `legal_queries.yaml`
6. **Ask:** "How do you write on social media? Describe your voice in a sentence or two." → Write to `config/voice.md`
7. Confirm setup is complete and proceed with the first `/today` run.

## Progress Display

Throughout this run, maintain a **live mission board** that you display after each agent completes. Update and re-display it as status changes. Use this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 DAILY BRIEFING — YYYY-MM-DD — IN PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 PHASE 1: GATHER INTELLIGENCE
 ├─ 🟢 Research         ✓  22 papers pulled
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

**Status icons:**
- ⬜ Waiting (not started)
- ⏳ In progress (with brief status note)
- 🟢 Complete (with result summary)
- 🟡 Complete with warnings
- 🔴 Failed (with error note)

**Display rules:**
1. Show the initial board with all agents "Waiting" before starting Phase 1
2. Update and re-display after EACH agent completes (not just each phase)
3. When an agent starts, change it to ⏳ with a brief note of what it's doing
4. When it finishes, change to 🟢/🟡/🔴 with the result from its staging JSON `status_detail`
5. At the end, display the final board with all agents resolved — this becomes the Operations Status Report

## Phase 0: Setup & Self-Improvement Check

1. Clear any stale files from `daily-briefing/output/.staging/` (delete all JSON files)
2. **CRITICAL: Get DATE from the system clock.** Run `date +%Y-%m-%d` via Bash and use that output as DATE for the entire run. Do NOT use any date from system context — it may be stale. Every filename, every staging JSON, every output must use this DATE.
3. **Read mission config:** Load `daily-briefing/config/mission.yaml` to understand the user's domain, products, and mission areas. This context informs all agents.
4. **Self-improvement check:** Read `daily-briefing/output/dashboard/updates.html` (if it exists). Extract all suggestion cards (critical, recommended, consider). For each actionable suggestion:
   - Summarize what it proposes and which config files it would change
   - Group into a numbered plan
   - **Present the plan to the user and WAIT for approval.**
   - Only execute approved items. Apply config changes before starting Phase 2.
5. Display the initial mission board (all agents ⬜ Waiting)

## Phase 1: Friday Check-In (Fridays Only)

If today is Friday:
1. Ask the user: "How was your week? What were the big wins?"
2. **Wait for the user's response** before proceeding.
3. Read `daily-briefing/output/wins/YYYY-WXX.md` for the current ISO week (if it exists)
4. Save both the user's response and the wins to `daily-briefing/output/.staging/YYYY-MM-DD-friday.md`

If not Friday, skip entirely.

## Phase 2: Gather Intelligence (Tier 1 — Independent Agents)

These 5 agents have NO dependencies on each other. Run them all.

**IMPORTANT: Web-dependent agents (intel, social, legal) use a tiered fallback strategy. If you have a FIRECRAWL_API_KEY in your environment, Firecrawl CLI is tried first via Bash, then WebFetch/WebSearch as fallback. Without Firecrawl, agents go straight to WebFetch/WebSearch.**

For each agent:
1. Update the mission board: agent → ⏳ with "Starting..."
2. Read and execute the agent file
3. Read the agent's staging JSON to get its `status` and `status_detail`
4. Update the mission board: agent → 🟢/🟡/🔴 with the `status_detail`
5. Re-display the full mission board

Agent files:
1. `daily-briefing/commands/agents/research.md`
2. `daily-briefing/commands/agents/calendar.md`
3. `daily-briefing/commands/agents/intel.md`
4. `daily-briefing/commands/agents/social.md`
5. `daily-briefing/commands/agents/legal.md`

After all 5 complete, verify staging files exist. If any are missing, note the failure but proceed.

## Phase 3: Assemble Briefing

Update board: Briefing → ⏳
Read and execute `daily-briefing/commands/agents/briefing.md`
Update board: Briefing → result. Re-display.

## Phase 4: Generate Social Posts

Update board: Social Posts → ⏳
Read and execute `daily-briefing/commands/agents/social-posts.md`
Update board: Social Posts → result. Re-display.

## Phase 5: Learn & Update

Update board: Self-Update → ⏳
Read and execute `daily-briefing/commands/agents/self-update.md`
Update board: Self-Update → result. Re-display.

## Phase 6: Dashboard Regeneration & Publish

Update board: Dashboard → ⏳

**Dashboard HTML pages use fixed templates** stored in `daily-briefing/templates/`. Each template has a CSS/JS/nav section that NEVER changes and a data section that gets regenerated each run.

Read and execute `daily-briefing/commands/agents/dashboard.md` — this agent:
1. Reads templates from `daily-briefing/templates/` (briefing-template.html, social-template.html, landing-template.html)
2. Reads today's staging JSONs for data
3. Regenerates the data sections while preserving all CSS, JS, and navigation exactly
4. For **briefing.html** and **social.html**: full data replacement (new content each day)
5. For **landing.html**: updates stats, quote, and date
6. For **index.html** and **network.html**: adds/updates data rows (accumulative — these grow over time)
7. Never touches system-diagram.html (static reference)

**CRITICAL:** The template files in `daily-briefing/templates/` are the source of truth for styling and layout.

Update board: Dashboard → result. Re-display.

Update board: Publish → ⏳
If `daily-briefing/scripts/sync_dashboard.sh` exists and is configured, run it. Otherwise skip publishing.
Update board: Publish → result.

**Display the FINAL mission board** — all agents resolved. Add file paths below:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📋 Briefing:  daily-briefing/output/briefings/YYYY-MM-DD-briefing.md
 📱 Posts:     daily-briefing/output/social-posts/YYYY-MM-DD-social-posts.md
 📊 Dashboard: daily-briefing/output/dashboard/index.html
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Append the final status to `daily-briefing/output/ops-log.md`.

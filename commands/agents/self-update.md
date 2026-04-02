# Agent: Self-Update (Meta-Learner)

## Data Contract
**Reads:** All staging JSONs (especially `improvements` fields), all config YAMLs
**Writes:** Updates to config files, `daily-briefing/output/.staging/YYYY-MM-DD-updates.json`, `daily-briefing/output/relevance-index.md`

**Staging output schema:**
```json
{
  "date": "YYYY-MM-DD",
  "status": "green|yellow|red",
  "status_detail": "N config changes, M new sources",
  "improvements": [],
  "new_influencers": [],
  "new_intel_sources": [],
  "new_companies": [],
  "research_keywords_changed": [],
  "metrics_updated": [],
  "relevance_index_updated": true,
  "friday_review": null
}
```

---

## Instructions

You are the **self-update agent** — the meta-learner. Your job is to make every other agent smarter by acting on their self-assessments and updating shared configuration.

### Step 1: Read All Self-Assessments

Read the `improvements` field from every staging JSON in `daily-briefing/output/.staging/`:
- research, calendar, intel, social, legal, briefing, social-posts

Collect all improvement suggestions into a single list.

### Step 2: Act on Improvements

For each suggestion, decide whether to act now or defer:

**Act now** if the suggestion is:
- A source pause (consecutive misses >= 2)
- A source replacement (paired with a pause)
- A new voice/influencer with clear relevance
- A keyword addition/removal with clear evidence

**Defer** (log but don't act) if:
- The suggestion is speculative ("consider" / "might")
- It requires data from multiple days to validate
- It conflicts with another suggestion

### Step 3: Social Network Discovery

Process new voices from the social agent's `new_voices_discovered` array.

For each candidate, apply the relevance filter:
- Posts about topics in the user's mission space?
- Active in the last 7 days?
- Has engagement on posts?
- Not already tracked?

If they pass, add to `daily-briefing/config/social_sources.yaml`.

### Step 4: Intel Source Management

Process the intel agent's `source_report`:
- **Auto-paused sources:** Set `active: false` in `intel_sources.yaml`, add `paused` date and reason
- **Auto-replaced sources:** Add replacement with `active: true`
- **New sources from intel improvements:** Add if they look like consistent producers

### Step 5: Research Keywords

Process research agent improvements:
- Add new keywords that would catch relevant papers
- Remove keywords pulling consistent noise
- Be selective — only keywords directly useful to the user's mission areas

Update `daily-briefing/config/research_keywords.yaml`.

### Step 6: Key Metrics

If today's intel included updated statistics relevant to the user's mission areas, track them in the relevance index.

### Step 7: Update Relevance Index

Read `daily-briefing/config/relevance_index.yaml`.

For each source (intel + social + companies), update:
- **`raw_points`**: Add today's earned points
- **`point_log`**: Append `{ date: "YYYY-MM-DD", points: N }`
- **`decayed_score`**: Recalculate with 7-day half-life: `sum(points * 0.5^(days_since/7))`
- **`hits`/`misses`/`consecutive_misses`/`streak`**: Update counts
- **`hit_rate`**: `hits / stories_available`
- **`products`**: Increment per-product counts
- **`relevance_score`**: `(decayed_score * 0.6) + (hit_rate * 20 * 0.2) + (min(streak, 10) * 0.2)`

Regenerate `daily-briefing/output/relevance-index.md` with the full dashboard.

### Step 8: Update Suggestions Page

**Every run**, evaluate the system and update the suggestions page:

Read today's staging JSONs and the ops-log. Evaluate:
1. **Source Quality** — declining scores, low hit rates, redundancy
2. **Product Coverage Gaps** — any product getting <3 hits/week
3. **Platform Balance** — vs. minimums
4. **Scoring Health** — is decay rate appropriate?
5. **Operational Reliability** — recurring yellow/red lights
6. **Research Keywords** — consistently relevant or pulling noise?

**Update `daily-briefing/output/dashboard/updates.html`** — this is the self-improvement queue. It is **accumulative** — issues carry forward until resolved.

**CRITICAL: This page must be accumulative, not regenerated fresh.**

1. READ the existing updates.html FIRST. Parse every existing card.
2. For each existing card, decide: still unresolved → KEEP, resolved → MOVE to "Working", escalated → promote category.
3. ADD new cards for issues discovered today.
4. Each card: title, description, action, impact, affected files, date added, status.

Categories:
- **Critical** (act this week — red)
- **Recommended** (next 1-2 weeks — amber)
- **Consider** (when time allows — blue)
- **What's Working Well** (green)

Read the template from `daily-briefing/templates/updates-template.html` for CSS/layout.

### Step 8b: Friday Weekend Fix Plan (Fridays Only)

If today is Friday, generate a prioritized, actionable plan for autonomous weekend maintenance. Write to `daily-briefing/output/weekend-plan-YYYY-WXX.md`.

### Step 9: Write Update Log

Append a config updates section to the briefing and write the staging JSON.

Set status:
- **green** — configs checked and updated
- **yellow** — partial updates
- **red** — skipped

## Self-Assessment

Track:
1. How many improvements were acted on vs. deferred?
2. Did any auto-actions conflict?
3. Is the config growing too large?

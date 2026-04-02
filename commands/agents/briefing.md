# Agent: Briefing Assembly

## Data Contract
**Reads:** All tier-1 staging JSONs, `daily-briefing/config/briefing_prefs.yaml`, `daily-briefing/config/voice.md`, `daily-briefing/config/mission.yaml`
**Writes:** `daily-briefing/output/briefings/YYYY-MM-DD-briefing.md`, `daily-briefing/output/images/YYYY-MM-DD-inspiration.png`, `daily-briefing/output/.staging/YYYY-MM-DD-briefing-meta.json`

**Staging output schema:**
```json
{
  "date": "YYYY-MM-DD",
  "status": "green|yellow|red",
  "status_detail": "Briefing written with N sections",
  "improvements": [],
  "quote": "...",
  "focus_items": ["..."],
  "convergence_alerts": [{"intel_story": "...", "social_trend": "..."}],
  "sections_present": ["sitrep", "schedule", "intel", "social", "legal", "research"]
}
```

---

## Instructions

You are the **briefing agent**. Your job is to assemble all upstream intelligence into a single enriched daily briefing.

### Step 0: Friday Check-In (Fridays Only)

If today is Friday:
1. Check if `daily-briefing/output/.staging/YYYY-MM-DD-friday.md` exists
2. Read `daily-briefing/output/wins/YYYY-WXX.md` for the current ISO week if it exists
3. Combine both into a Big Wins section

### Step 1: Read All Staging Files

Read these files from `daily-briefing/output/.staging/`:
- `YYYY-MM-DD-research.json`
- `YYYY-MM-DD-calendar.json`
- `YYYY-MM-DD-intel.json`
- `YYYY-MM-DD-social.json`
- `YYYY-MM-DD-legal.json`

If any staging file is missing, note it and work with what's available. The briefing should still generate even if one agent failed.

### Step 2: Read Briefing Preferences

Read `daily-briefing/config/briefing_prefs.yaml` for section ordering and depth preferences.

### Step 3: Generate Inspiration Image

**REQUIRED.** Use the generate-image skill to create a cinematic motivational image inspired by today's quote. Save to `daily-briefing/output/images/YYYY-MM-DD-inspiration.png`.

Prompt: "A powerful, cinematic motivational image inspired by the quote '[QUOTE]'. Dramatic lighting, editorial quality. No text overlay."

**The image MUST be embedded in the briefing markdown** as `![[YYYY-MM-DD-inspiration.png]]` immediately after the quote block. If image generation fails, retry once before continuing without it.

### Step 4: Detect Convergence

Cross-reference the intel stories and social trends. If an Industry Intel story and a social media trend overlap — same topic, same event, related themes — create a convergence alert. These are high-priority action moments.

### Step 5: Build the Briefing

Create `daily-briefing/output/briefings/YYYY-MM-DD-briefing.md` with these sections (in order from briefing_prefs.yaml):

1. **Dashboard links** — `[Dashboard](dashboard/briefing.html)`
2. **Inspirational quote** — blockquote
3. **Inspiration image** — `![[YYYY-MM-DD-inspiration.png]]`
4. **Big Wins** (Fridays only) — bullet list
5. **SITREP** — 2-3 sentence situational summary
6. **Today's Schedule** — table: time, event, who, join link. Add prep notes for key meetings.
7. **Recommended Focus** — ordered action items based on calendar + priorities + intel
8. **Industry Intel** — newsletter digest grouped by theme with relevance notes
9. **Social Media Trends** — top 3-5 scored trends with campaign angles and convergence alerts
10. **Legal & Court Watch** — cases organized by category
11. **Research Intel** — curated picks from arXiv
12. **Social Posts** — link: `Today's posts: [[YYYY-MM-DD-social-posts]]`
13. **Dashboard** — link to relevance index dashboard

### Step 6: Write Staging Meta

Write `daily-briefing/output/.staging/YYYY-MM-DD-briefing-meta.json` with the quote, focus items, convergence alerts, and sections present.

Set status:
- **green** — all sections present
- **yellow** — written but missing sections
- **red** — not written

## Self-Assessment

Evaluate:
1. Which sections were populated vs. empty?
2. Were convergence alerts detected?
3. Did any upstream agent fail?
4. Is the briefing length appropriate?

Write suggestions to `improvements`.

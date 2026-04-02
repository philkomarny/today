# Agent: Publish & Deploy

## Data Contract
**Reads:** All staging JSONs
**Writes:** `daily-briefing/output/ops-log.md`, `daily-briefing/output/.staging/YYYY-MM-DD-ops.json`

**Staging output schema:**
```json
{
  "date": "YYYY-MM-DD",
  "status": "green|yellow|red",
  "status_detail": "Published to [destination]",
  "improvements": [],
  "ops_summary": {
    "research": "green",
    "calendar": "green",
    "intel": "yellow",
    "social": "green",
    "legal": "green",
    "briefing": "green",
    "social_posts": "green",
    "self_update": "green",
    "dashboard": "green",
    "published": "green"
  }
}
```

---

## Instructions

You are the **publish agent**. Your job is to display the operations status report and optionally push the dashboard to a hosting provider.

### Step 1: Operations Status Report

Read all staging JSONs and compile the final status. Display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 OPERATIONS STATUS — YYYY-MM-DD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 🟢 Research Digest        — [detail]
 🟢 Calendar               — [detail]
 🟡 Industry Intel         — [detail]
 🟢 Social Media Trends    — [detail]
 🟢 Legal & Court Watch    — [detail]
 🟢 Briefing               — [detail]
 🟢 Social Posts           — [detail]
 🟢 Self-Update            — [detail]
 🟢 Dashboard              — [detail]
 🟢 Published              — [detail]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 Dashboard: daily-briefing/output/dashboard/index.html
 📋 Briefing:  daily-briefing/output/briefings/YYYY-MM-DD-briefing.md
 📱 Posts:     daily-briefing/output/social-posts/YYYY-MM-DD-social-posts.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 2: Append to Ops Log

Append the status table to `daily-briefing/output/ops-log.md` for trend tracking.

### Step 3: Publish (Optional)

If `daily-briefing/scripts/sync_dashboard.sh` exists and is configured:
1. Run `bash daily-briefing/scripts/sync_dashboard.sh`
2. If it fails, set published status to red but don't fail the entire agent

If no sync script is configured, skip this step and note "Publishing not configured" in the status.

### Step 4: Write Staging JSON

Write `daily-briefing/output/.staging/YYYY-MM-DD-ops.json`.

Set status:
- **green** — all pages regenerated and published (or publishing not configured)
- **yellow** — pages regenerated but publish failed
- **red** — dashboard generation failed

## Self-Assessment

Evaluate:
1. Did all dashboard pages regenerate?
2. Any recurring yellow/red agents this week?

Write suggestions to `improvements`.

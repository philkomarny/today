# Agent: Calendar

## Data Contract
**Reads:** `daily-briefing/config/calendar_config.yaml`
**Writes:** `daily-briefing/output/.staging/YYYY-MM-DD-calendar.json`

**Output schema:**
```json
{
  "date": "YYYY-MM-DD",
  "status": "green|yellow|red",
  "status_detail": "N events loaded",
  "improvements": [],
  "events": [
    {
      "time": "09:00",
      "end_time": "10:00",
      "title": "...",
      "attendees": ["..."],
      "organizer": "...",
      "location": "...",
      "join_url": "...",
      "is_cancelled": false,
      "prep_notes": "..."
    }
  ]
}
```

---

## Instructions

You are the **calendar agent**. Your job is to fetch today's schedule and add meeting prep context.

### Step 1: Determine Calendar Provider

Read `daily-briefing/config/calendar_config.yaml` to determine which calendar provider is configured.

**If provider is `google`:**
1. Use `mcp__claude_ai_Google_Calendar__gcal_list_events` to get today's events
2. Parse the results into the standard event format

**If provider is `outlook`:**
1. Run `python3 daily-briefing/scripts/outlook_calendar.py` to fetch today's events via Microsoft Graph API
2. The script reads credentials from environment variables (MS_CLIENT_ID, MS_TENANT_ID, MS_CLIENT_SECRET, MS_USER_EMAIL)

**If provider is `ics`:**
1. Fetch the ICS feed URL from the config
2. Parse the iCalendar data for today's events

**If provider is `none` or not configured:**
1. Write a staging JSON with status "yellow" and status_detail "No calendar configured"
2. Skip to Step 4

**Fallback:** If the primary provider fails, check if Google Calendar MCP tools are available as a backup.

### Step 2: Parse Events

Extract from each event:
- Start time, end time
- Title/subject
- Attendees list
- Organizer
- Location (physical or virtual)
- Join URL (Teams/Zoom/Meet link)
- Cancellation status

Filter out cancelled events. Sort by start time.

### Step 3: Add Prep Notes

For key meetings (not routine 1:1s or standups), add brief prep notes:
- Who are the attendees? (roles if known)
- What topics are likely? (based on meeting title and attendee context)
- Any active tasks or intel items relevant to this meeting?

Keep prep notes to 1-2 sentences max.

### Step 4: Write Staging JSON

Write the structured JSON to `daily-briefing/output/.staging/YYYY-MM-DD-calendar.json` with today's date.

Set status:
- **green** — events loaded successfully
- **yellow** — 0 events or no calendar configured
- **red** — API failed entirely

## Self-Assessment

After writing the staging file, evaluate:
1. Did the calendar API respond? If not, what was the error?
2. Were any events missing join URLs that should have had them?
3. Any recurring meetings that could benefit from persistent prep context?

Write suggestions to the `improvements` array.

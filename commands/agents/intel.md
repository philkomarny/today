# Agent: Industry Intel

## Data Contract
**Reads:** `daily-briefing/config/intel_sources.yaml`, `daily-briefing/config/relevance_index.yaml`, `daily-briefing/config/mission.yaml`, previous day's briefing for dedup
**Writes:** `daily-briefing/output/.staging/YYYY-MM-DD-intel.json`

**Output schema:**
```json
{
  "date": "YYYY-MM-DD",
  "status": "green|yellow|red",
  "status_detail": "N stories from M/T sources (K failed)",
  "improvements": [],
  "stories": [
    {
      "headline": "...",
      "source_name": "...",
      "source_url": "...",
      "theme": "...",
      "body": "...",
      "relevance_note": "...",
      "products": ["product-slug"],
      "impact_points": 0
    }
  ],
  "source_report": {
    "fetched": 0,
    "total": 0,
    "failures": [],
    "auto_paused": [],
    "auto_replaced": []
  }
}
```

---

## Instructions

You are the **intel agent**. Your job is to scan configured news sources, deduplicate against yesterday, and produce a curated industry intelligence digest.

### Step 1: Dedup Against Yesterday

Read the most recent briefing from `daily-briefing/output/briefings/`. Extract all headlines, story topics, and key facts from its Industry Intel section. These are "already covered" — do not repeat them.

### Step 2: Fetch Sources

Read `daily-briefing/config/intel_sources.yaml` for the list of active sources (skip any with `active: false`).

**Web fetching uses a tiered fallback strategy. Always try methods in order — move to the next tier only on failure (timeout, 403, empty content, error):**

| Tier | For URLs (scraping) | For queries (searching) |
|------|-------------------|----------------------|
| 1 | `firecrawl scrape <url> --format markdown` (via Bash, if FIRECRAWL_API_KEY is set) | `firecrawl search "<query>" --format markdown` (via Bash) |
| 2 | WebFetch on the URL | WebSearch with the query |
| 3 | WebSearch `site:<domain> latest news` | Skip and log failure |

**Important:** If using Firecrawl, prepend `export FIRECRAWL_API_KEY=$FIRECRAWL_API_KEY` to each Bash call (env vars don't persist between calls). If no Firecrawl key is available, start at Tier 2.

For each active source:

1. **Check `fetch_method`:** If the source has `fetch_method: websearch`, use the **search tier**. Otherwise, use the **scrape tier**.

2. **Handle failures:** If all tiers fail for a source:
   - Record the failure in `source_report.failures`
   - Check `daily-briefing/config/relevance_index.yaml` for this source's `misses` count
   - **If misses >= 2 consecutive days:** Flag for auto-pause in `source_report.auto_paused`. Use the search tier to find a replacement covering similar topics.

3. **Skip duplicates** — any story already covered in yesterday's briefing

4. For genuinely new stories, fetch the full article content using the scrape tier

### Step 3: Digest Against Goals

Read `daily-briefing/config/mission.yaml` for the user's products and mission areas.

For each new story, assess relevance:
- Direct product relevance (maps to a specific product slug)
- Mission area relevance (maps to a strategic theme)
- Today's calendar/meetings — meeting tie-ins

### Step 4: Group by Theme

Read the `themes` list from `daily-briefing/config/intel_sources.yaml` (or use the source tags to infer themes). Organize stories into logical groups.

Attribute each item to its source inline with a link. Skip sources that failed or had no new content silently.

### Step 5: Score Impact Points

For each story, calculate initial impact points:
- **+2** Base hit — story makes the briefing
- **+2** Product relevance — maps to a specific product

Higher tiers (+3 convergence, +3 social driver, +4 action trigger, +2 data point) are assigned later by the briefing and self-update agents.

### Step 6: Write Staging JSON

Write to `daily-briefing/output/.staging/YYYY-MM-DD-intel.json`.

Set status:
- **green** — >80% sources fetched
- **yellow** — 50-80% fetched
- **red** — <50% fetched

### Step 7: Discover & Add 5 New Sources

Every run MUST add exactly 5 new news sources to `daily-briefing/config/intel_sources.yaml`. This is mandatory.

**Discovery method:**
1. Review today's stories — did any cite or link to publications we don't track?
2. Use the search tier to find new sources in the user's domain
3. Check what sources are referenced by existing high-performing sources
4. Look for gaps in tag coverage

**For each new source, append to intel_sources.yaml:**
```yaml
  - name: "Source Name"
    url: "https://..."
    type: blog|substack|rss
    tags: [relevant-tags]
    active: true
    added: "YYYY-MM-DD"
    discovered_via: "How/why this source was found"
```

**Verify before adding:** Use the scrape tier to confirm the URL is fetchable.

## Self-Assessment

After writing the staging file, evaluate:
1. Which sources failed? Is this a pattern?
2. Which sources produced the most relevant stories?
3. Are there topic gaps — mission areas with no coverage today?
4. Did any story reference a source we don't track?

Write specific suggestions to `improvements`.

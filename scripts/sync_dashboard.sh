#!/bin/bash
# Sync dashboard to a GitHub repo for Vercel/Netlify/GitHub Pages deployment.
# Run after each /today run.
#
# CONFIGURE THESE PATHS for your setup:
#   SRC  = where the dashboard HTML lives (output/dashboard/)
#   DEST = where to copy files for deployment
#   REPO = your GitHub repo root
#
# RULES:
#   1. DATE is always from the system clock — never hardcoded
#   2. All "Last Updated" dates are stamped with today's DATE
#   3. Templates are NEVER regenerated — only data sections are updated

set -e

# ─── CONFIGURE THESE ───
SRC="$(dirname "$0")/../output/dashboard"    # Source: local dashboard files
DEST=""                                       # Destination: path in your GitHub repo
REPO=""                                       # GitHub repo root directory
# ───────────────────────

if [ -z "$DEST" ] || [ -z "$REPO" ]; then
  echo "Publish script not configured."
  echo "Edit scripts/sync_dashboard.sh and set DEST and REPO paths."
  echo "  DEST = where to copy dashboard HTML in your GitHub repo"
  echo "  REPO = your GitHub repo root directory"
  exit 0
fi

DATE=$(date +%Y-%m-%d)
DATE_PRETTY=$(date +"%B %-d, %Y")
DAY_OF_WEEK=$(date +%A)

echo "Syncing dashboard..."
echo "  DATE: $DATE ($DAY_OF_WEEK)"

# Create destination
mkdir -p "$DEST/images"

# ─── Size check: verify source files aren't suspiciously small ───
MIN_SIZE=2000
TEMPLATE_OK=true
for f in landing.html index.html briefing.html social.html network.html; do
  FPATH="$SRC/$f"
  if [ ! -f "$FPATH" ]; then
    echo "  WARNING: Missing $f — skipping copy"
    TEMPLATE_OK=false
    continue
  fi
  FSIZE=$(wc -c < "$FPATH" | tr -d ' ')
  if [ "$FSIZE" -lt "$MIN_SIZE" ]; then
    echo "  WARNING: $f is only ${FSIZE} bytes (min ${MIN_SIZE}) — possible template clobber. Skipping."
    TEMPLATE_OK=false
    continue
  fi
done

if [ "$TEMPLATE_OK" = false ]; then
  echo "  Some templates look wrong. Proceeding with valid files only."
fi

# ─── Copy dashboard HTML files ───
for f in landing.html index.html briefing.html social.html network.html updates.html; do
  FPATH="$SRC/$f"
  if [ -f "$FPATH" ]; then
    FSIZE=$(wc -c < "$FPATH" | tr -d ' ')
    if [ "$FSIZE" -ge "$MIN_SIZE" ] || [ "$f" = "updates.html" ]; then
      cp "$FPATH" "$DEST/$f"
    fi
  fi
done

# ─── Copy images ───
if [ -d "$SRC/../images" ]; then
  LATEST=$(ls "$SRC/../images/" 2>/dev/null | grep -oE '^[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort -r | head -1)
  if [ -n "$LATEST" ]; then
    cp "$SRC/../images/${LATEST}"-* "$DEST/images/" 2>/dev/null || true
  fi
fi

# ─── Enforce correct dates across all pages ───
echo "  Enforcing date $DATE across all pages..."

for f in "$DEST"/*.html; do
  [ -f "$f" ] || continue
  sed -i '' "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $DATE/g" "$f"
  sed -i '' "s/Last run: <span>[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last run: <span>$DATE/g" "$f"
  sed -i '' "s/Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Updated: $DATE/g" "$f"
done

# ─── Rewrite image paths for deployed structure ───
for f in "$DEST"/*.html; do
  [ -f "$f" ] || continue
  sed -i '' 's|\.\./images/|images/|g' "$f"
done

# ─── Optional: Password protection ───
if [ -n "$VAULT_PASSPHRASE" ]; then
  HASH=$(echo -n "$VAULT_PASSPHRASE" | shasum -a 256 | cut -d' ' -f1)
  # Inject auth if you have an auth.js template
  if [ -f "$DEST/auth.js" ]; then
    sed -i '' "s|%%VAULT_HASH%%|$HASH|g" "$DEST/auth.js"
  fi
fi

echo "Files synced. Committing and pushing..."

cd "$REPO"
git add .
git commit -m "Dashboard update — $DATE" 2>/dev/null || echo "No changes to commit."
git push origin main 2>/dev/null || echo "Push failed."

echo "Done."

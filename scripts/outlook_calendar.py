#!/usr/bin/env python3
"""
outlook_calendar.py — Fetches today's Outlook calendar events via Microsoft Graph API.
Uses client credentials flow (Application permissions) — fully automated, no browser needed.

Usage: python3 scripts/outlook_calendar.py

Requires:
  - pip install msal requests
  - Environment variables: MS_CLIENT_ID, MS_TENANT_ID, MS_CLIENT_SECRET, MS_USER_EMAIL
"""

import json
import os
import datetime
import re
import sys
from pathlib import Path

import msal
import requests

SCRIPTS_DIR = Path(__file__).parent
CALENDAR_EVENTS_FILE = SCRIPTS_DIR / ".calendar_events.json"

# Read credentials from environment variables
CLIENT_ID = os.environ.get("MS_CLIENT_ID", "")
TENANT_ID = os.environ.get("MS_TENANT_ID", "")
CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET", "")
USER_EMAIL = os.environ.get("MS_USER_EMAIL", "")

if not all([CLIENT_ID, TENANT_ID, CLIENT_SECRET, USER_EMAIL]):
    print("Missing Microsoft Graph API credentials.")
    print("Set these environment variables in your .env file:")
    print("  MS_CLIENT_ID, MS_TENANT_ID, MS_CLIENT_SECRET, MS_USER_EMAIL")
    print()
    print("To get these credentials:")
    print("  1. Go to https://portal.azure.com → Azure Active Directory → App registrations")
    print("  2. Create a new registration (or use existing)")
    print("  3. Add API permission: Microsoft Graph → Application → Calendars.Read")
    print("  4. Create a client secret under Certificates & secrets")
    sys.exit(1)

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"


def authenticate():
    """Authenticate using client credentials (app-only, no user interaction)."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

    result = app.acquire_token_for_client(scopes=SCOPES)

    if "access_token" not in result:
        print(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
        sys.exit(1)

    return result["access_token"]


def fetch_today_events(token):
    """Fetch today's calendar events from Microsoft Graph."""
    today = datetime.date.today()
    start = f"{today.isoformat()}T00:00:00"
    end = f"{today.isoformat()}T23:59:59"

    headers = {
        "Authorization": f"Bearer {token}",
        "Prefer": 'outlook.timezone="America/Chicago"',
    }
    params = {
        "startDateTime": start,
        "endDateTime": end,
        "$orderby": "start/dateTime",
        "$top": 50,
        "$select": "subject,start,end,location,isAllDay,isCancelled,isOnlineMeeting,onlineMeetingUrl,attendees,body,organizer,showAs,responseStatus",
    }

    resp = requests.get(
        f"{GRAPH_ENDPOINT}/users/{USER_EMAIL}/calendarView",
        headers=headers,
        params=params,
    )

    if resp.status_code != 200:
        print(f"Graph API error ({resp.status_code}): {resp.text}")
        sys.exit(1)

    return resp.json().get("value", [])


def is_initials_only(subject: str) -> bool:
    """Return True if the subject is only capital-letter initials (with optional separators).

    Matches patterns like: "PK / ML", "PK/ML", "PK - ML"
    Does NOT match: "Revenue Opportunities", "Team Standup"
    """
    cleaned = re.sub(r'[\s/\-–—·•,&+]+', '', subject.strip())
    return bool(cleaned) and cleaned.isalpha() and cleaned.isupper() and len(cleaned) <= 8


def format_events(events):
    """Format events as markdown lines for the daily briefing."""
    if not events:
        return ["*No meetings today. Deep work day.*"]

    lines = []
    for event in events:
        subject = event.get("subject", "No subject")

        if is_initials_only(subject):
            continue

        start_raw = event["start"].get("dateTime", "")
        end_raw = event["end"].get("dateTime", "")
        is_all_day = event.get("isAllDay", False)
        is_cancelled = event.get("isCancelled", False)
        location = event.get("location", {}).get("displayName", "")
        is_online = event.get("isOnlineMeeting", False)
        online_url = event.get("onlineMeetingUrl", "")

        if is_all_day:
            time_str = "All day"
        else:
            try:
                start_dt = datetime.datetime.fromisoformat(start_raw)
                end_dt = datetime.datetime.fromisoformat(end_raw)
                time_str = f"{start_dt.strftime('%-I:%M %p')} – {end_dt.strftime('%-I:%M %p')}"
            except (ValueError, TypeError):
                time_str = "TBD"

        if is_cancelled:
            line = f"- ~~**{time_str}** — {subject}~~ CANCELED"
        else:
            line = f"- **{time_str}** — {subject}"

        if not is_cancelled:
            if location:
                line += f" 📍 {location}"
            if is_online and online_url:
                line += f" [Join]({online_url})"
            elif is_online:
                line += " (online)"

        attendees = event.get("attendees", [])
        attendee_names = []
        for att in attendees:
            name = att.get("emailAddress", {}).get("name", "")
            email = att.get("emailAddress", {}).get("address", "")
            status = att.get("status", {}).get("response", "")
            if name:
                # Skip the calendar owner's own entry
                if email and email.lower() == USER_EMAIL.lower():
                    continue
                if status == "declined":
                    attendee_names.append(f"~~{name}~~")
                elif status == "tentativelyAccepted":
                    attendee_names.append(f"{name} (?)")
                else:
                    attendee_names.append(name)

        lines.append(line)

        if attendee_names and not is_cancelled:
            lines.append(f"  - With: {', '.join(attendee_names[:10])}")

        organizer = event.get("organizer", {}).get("emailAddress", {})
        org_email = organizer.get("address", "").lower()
        if org_email and org_email != USER_EMAIL.lower():
            org_name = organizer.get("name", org_email)
            lines.append(f"  - Organized by: {org_name}")

    return lines


def export_for_briefing(events):
    """Export events as JSON for the briefing pipeline."""
    exported = []
    for event in events:
        subject = event.get("subject", "")

        if is_initials_only(subject):
            continue

        start_raw = event["start"].get("dateTime", "")
        end_raw = event["end"].get("dateTime", "")
        is_all_day = event.get("isAllDay", False)

        if is_all_day:
            start_str = "All day"
            end_str = ""
            sort_key = f"{datetime.date.today().isoformat()}T00:00:00"
        else:
            try:
                start_dt = datetime.datetime.fromisoformat(start_raw)
                end_dt = datetime.datetime.fromisoformat(end_raw)
                start_str = start_dt.strftime("%-I:%M %p")
                end_str = end_dt.strftime("%-I:%M %p")
                sort_key = start_dt.isoformat()
            except (ValueError, TypeError):
                start_str = ""
                end_str = ""
                sort_key = ""

        attendees = []
        for att in event.get("attendees", []):
            name = att.get("emailAddress", {}).get("name", "")
            email = att.get("emailAddress", {}).get("address", "")
            status = att.get("status", {}).get("response", "")
            display = name if name else email
            if email and email.lower() == USER_EMAIL.lower():
                continue
            if status == "declined":
                display = f"~~{display}~~"
            elif status == "tentativelyAccepted":
                display = f"{display} (?)"
            attendees.append(display)

        organizer = event.get("organizer", {}).get("emailAddress", {})
        org_email = organizer.get("address", "").lower()
        org_name = organizer.get("name", "") if org_email != USER_EMAIL.lower() else ""

        exported.append({
            "subject": event.get("subject", ""),
            "start": start_str,
            "end": end_str,
            "is_all_day": is_all_day,
            "is_cancelled": event.get("isCancelled", False),
            "location": event.get("location", {}).get("displayName", ""),
            "description": event.get("body", {}).get("content", "")[:500],
            "attendees": attendees,
            "organizer": org_name,
            "is_online": event.get("isOnlineMeeting", False),
            "join_url": event.get("onlineMeetingUrl", ""),
            "source": "Outlook-Graph",
            "_sort_key": sort_key,
        })

    with open(CALENDAR_EVENTS_FILE, "w") as f:
        json.dump(exported, f, indent=2, default=str)


if __name__ == "__main__":
    token = authenticate()
    events = fetch_today_events(token)

    export_for_briefing(events)

    visible_events = [e for e in events if not is_initials_only(e.get("subject", ""))]

    if "--json" in sys.argv:
        print(json.dumps(visible_events, indent=2, default=str))
    else:
        lines = format_events(events)
        print(f"Today's Schedule ({len(visible_events)} events):")
        for line in lines:
            print(line)

# Developers Guide for F1 Calendar CLI

This document explains the full architecture and key logic of the `f1Calendar.py` script for contributors and developers looking to modify or extend its functionality.

---

## 🧱 Structure Overview

The script performs the following steps:

1. Authenticates with the Google Calendar API.
2. Scrapes F1 session data from [https://www.f1latam.com/horarios.php](https://www.f1latam.com/horarios.php).
3. Parses schedule info for a given city.
4. Extracts the Grand Prix name.
5. Converts dates to timezone-aware `datetime` objects.
6. Deduplicates events.
7. Adds reminders and colors.
8. Optionally writes to calendar or just previews via `--dry-run`.

---

## 🔐 Authentication (`get_calendar_service`)

Handles the OAuth2 flow:

- Loads from `token.json` if it exists and is valid.
- If not, launches a browser for user auth.
- Stores refreshed token data in `token.json`.

Uses the full `https://www.googleapis.com/auth/calendar` scope to access and write to calendars.

---

## 🌐 Web Scraping (`scrape_f1_schedule`)

- Fetches and parses the page HTML.
- Navigates all `<table>` blocks, each of which contains a GMT group of cities.
- Extracts cities and session times from the first column and subsequent `<td>` elements.
- Uses the `<thead>` row to identify session names.
- Returns a list of `(session_name, time_str)` tuples for the matched city.

---

## 🏁 Grand Prix Title (`fetch_grand_prix_title`)

- Looks for `<p class="titsecc"><a class="titnotautos">GP de...</a></p>`.
- Returns the clean title to be appended to all event names.
- If not found, falls back to "Grand Prix".

---

## 🧠 Time Parsing (`parse_event_time`)

- Converts strings like `"06:30 Junio 27"` to a localized `datetime`.
- Extracts hour, minute, day and Spanish month.
- Applies the timezone using `pytz.timezone(...).localize(...)`.

---

## 🗓️ Event Insertion (`add_event_to_calendar`)

- Checks for duplicates with a Calendar API `events().list(...)` call.
- Builds event body including:

  - Summary with session and GP name
  - ISO8601 start and end times
  - Color ID `11` (Tomato Red)
  - Reminder override (12h, 30min, 10min pop-ups)

- Submits via `events().insert()`.

Special handling:

- The race session ("Carrera") is given a 2-hour duration.

---

## 🧪 CLI Entrypoint

Command-line options:

- `--city`: Required for schedule matching.
- `--dry-run`: Skips Calendar API writes.
- `--check-calendar`: Auth test.
- `--list-cities`: Scrapes and prints all available cities.
- `--timezone`: Force specific timezone.

---

## 🧼 Cron Job Integration

Output and errors print cleanly for redirection.
No UI or input prompts in non-authenticated flow.

---

## 🛡 Error Handling & Robustness

- Validates structure and contents of HTML before accessing.
- Defensive parsing (splits, `.get()`, try/catch).
- Uses fallback values like "Grand Prix" for robustness.

---

## 📁 File Structure

- `f1Calendar.py`: Main script
- `requirements.txt`: Python deps
- `credentials.json`: OAuth client ID file
- `token.json`: Auto-generated after login
- `.env`: Optional for client secrets
- `cron.log`: Optional output from cron

---

## 💡 Key Functions Summary

- parse_args() → CLI interface
- scrape_f1_schedule(city) → Parses schedule table and session times
- get_gp_title() → Extracts GP name (used in event summary)
- get_calendar_service() → Auth flow and returns service
- add_event_to_calendar(service, schedule, gp_title) → Adds deduped events with reminders

------

## 🧪 Testing Tips

- Use --dry-run frequently during dev to avoid filling calendar
- Delete token.json to reset OAuth scopes if needed
- Use print(schedule) or print(args) for quick inspection

---

## 💬 Questions?

Reach out to [@an-dr32](https://github.com/an-dr32) or open an issue on GitHub.

Happy hacking! 🏎️

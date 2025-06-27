# F1 Calendar to Google Calendar CLI

Automatically fetch Formula 1 session times from F1Latam.com and add them to your Google Calendar.

---

## 🏁 Features

- ⏱ Parses session times for your selected city (e.g., Bogotá, Lima, Madrid).
- 📅 Adds events to Google Calendar with reminders.
- 📍 Tags each entry with the actual Grand Prix name (e.g., "GP de Austria - Red Bull Ring").
- 🔁 Deduplicates calendar entries.
- 🕒 Supports dry-run mode to preview schedule without creating events.
- 🔔 Adds reminders (12h, 30min, 10min before each session)
- 🎨 Colors events Tomato red
- 🧠 Validates your Google Calendar connection (--check-calendar)
- 📝 Automatically logs execution for scheduled cron jobs

---

## ✅ Requirements

- Python 3.7+
- Google Calendar API credentials

## 🌱 Virtual Environment Setup

Use a virtual environment to isolate dependencies:

```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Windows (CMD): .venv\Scripts\activate.bat
                         # Windows (PowerShell): .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
```
To deactivate the environment:
```bash
    deactivate
```
To reactivate later:
```bash
    source .venv/bin/activate  # Or use the appropriate path for Windows
```

If requirements.txt is missing, you can generate it with:

Your `requirements.txt` should include:

```txt
beautifulsoup4
python-dotenv
requests
google-auth
google-auth-oauthlib
google-api-python-client
pytz
```

---

## 🔐 Setup

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Create a project or use an existing one
3. Enable the **Google Calendar API**

   - Go to APIs & Services > OAuth consent screen, and:
   - Ensure the app is in Testing mode.
   - Under "Scopes for Google APIs", confirm that Calendar API is listed:
     .../auth/calendar.events — Manage your calendars
   - Make sure your Google account is listed as a Test user under "Test users".

   - Click **Create Credentials > OAuth client ID**
   - Select **Desktop App**
   - Download the `credentials.json` file

4. Place the `credentials.json` file in the same directory as the script
5. Add `.env` file (optional if not using custom env vars)

## 🧠 setup.sh Script (Optional)

Run the helper setup script:

```bash
    chmod +x setup.sh
    ./setup.sh
```

---

## 🚀 Usage

### List available cities:

```bash
python3 f1Calendar.py --list-cities
```

### Preview the schedule for your city (dry run):

```bash
python3 f1Calendar.py --city "Bogotá" --dry-run
```

### Add events to your Google Calendar:

```bash
python3 f1Calendar.py --city "Bogotá"
```

### Check Google Calendar connectivity:

```bash
python3 f1Calendar.py --check-calendar
```
> The first time you run the script, it will open a browser window to authenticate your Google account. A `token.json` file will be created.

## CLI Options:

* --city "City Name" → Required for schedule

* --dry-run → Preview events without adding to calendar

* --timezone America/Bogota → Override timezone if needed

* --list-cities → List all available cities (scraped from site)

* --check-calendar → Validate Google Calendar access



## ✅ Example Output

📍 Detected Grand Prix: GP de Austria 🏁 Red Bull Ring
📅 Parsed Events:

- Libres 1: 2025-06-27 06:30 -05
  📌 Adding to calendar: F1: Libres 1 - GP de Austria 🏁 Red Bull Ring at 2025-06-27 06:30
  ...

## 📅 Automate with Cron (Linux/macOS)

To run the script every Thursday at 10 AM and log output:

```bash
    crontab -e
```

Add this line:

```bash
    0 10 \* \* 4 cd /path/to/your/project && .venv/bin/python f1Calendar.py --city "Bogotá" >> cron.log 2>&1
```

    Make sure the .venv is activated correctly in the path.
    cron.log will store the output of each run.

To remove or edit the cron job:

```bash
    crontab -e
```

Then delete or modify the line related to f1Calendar.py.

To view current cron jobs:

```bash
    crontab -l
```

## To completely clear all cron jobs:
```bash
    crontab -r
```

## 🗂 Diagram

f1Calendar.py
├── parse_args()           # Handle CLI input and options
├── scrape_f1_schedule()   # Extract F1 schedule for the given city
├── get_gp_title()         # Extract Grand Prix name from the webpage
├── get_calendar_service() # Authenticate with Google Calendar
├── add_event_to_calendar()# Insert events with deduplication and reminders
├── main()                 # Orchestrates CLI, scraping, parsing, and calendar sync



## 📌 How It Works

- Scrapes [https://www.f1latam.com/horarios.php](https://www.f1latam.com/horarios.php)
- Extracts the actual Grand Prix name from the heading
- Matches your selected city with the correct GMT row
- Parses event dates (localized to your time zone)
- Adds reminders:

  - 12 hours before
  - 30 minutes before
  - 10 minutes before

- Event color is set to tomato red
- The race event ("Carrera") lasts 2 hours

---

## 💡 Tips

- Use `--dry-run` to debug event parsing without making changes
- Change time zone using `--timezone` (e.g., `America/Mexico_City`)
- You can run this as a cron job before race weekends

---

## 📫 Author - an-dr32

---

Enjoy your races ⚡️!

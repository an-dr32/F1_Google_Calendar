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
- 🧠 Validates your Google Calendar connection (--check-calendar)

---

## ✅ Requirements

- Python 3.7+
- Google Calendar API credentials

## 🌱 Virtual Environment Setup

Use a virtual environment to isolate dependencies:

```bash
    python3 -m venv .venv
    source .venv/bin/activate # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
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

## ✅ Example Output

📍 Detected Grand Prix: GP de Austria 🏁 Red Bull Ring
📅 Parsed Events:

- Libres 1: 2025-06-27 06:30 -05
  📌 Adding to calendar: F1: Libres 1 - GP de Austria 🏁 Red Bull Ring at 2025-06-27 06:30
  ...

---

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

Feel free to fork, improve, and contribute!

---

Enjoy your races ⚡️!

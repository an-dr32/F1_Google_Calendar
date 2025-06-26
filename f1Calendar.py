import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
import re

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

# Required Google Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def authenticate_google():
    # Handles Google OAuth2 authentication and token storage
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if (
            not creds
            or not creds.valid
            or not set(SCOPES).issubset(set(creds.scopes or []))
        ):
            print("⚠️ Invalid or insufficient token scopes, deleting token.json...")
            os.remove("token.json")
            creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def get_primary_calendar_id(service):
    # Retrieves the user's primary calendar ID
    calendar_list = service.calendarList().list().execute()
    for cal in calendar_list.get("items", []):
        if cal.get("primary", False):
            return cal["id"]
    print("⚠️ No primary calendar found. Using the first available one.")
    return calendar_list["items"][0]["id"] if calendar_list["items"] else "primary"


def check_google_calendar_connection():
    # Tests if the calendar API connection works and lists calendar name
    try:
        service = authenticate_google()
        calendar_list = service.calendarList().list().execute()
        primary_id = get_primary_calendar_id(service)
        primary_name = next(
            (
                cal["summary"]
                for cal in calendar_list["items"]
                if cal["id"] == primary_id
            ),
            primary_id,
        )
        print("\n✅ Google Calendar API connected. Primary calendar:")
        print(f"   {primary_name}")
        return True
    except Exception as e:
        print(f"\n❌ Failed to connect to Google Calendar API: {e}")
        return False


def extract_available_cities():
    # Scrapes F1Latam site to extract the list of available cities and GMT blocks
    url = "https://www.f1latam.com/horarios.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    cities_set = set()
    for table in soup.find_all("table"):
        tbody = table.find("tbody")
        if not tbody:
            continue

        rows = tbody.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            first_cell_lines = cells[0].get_text(separator="\n", strip=True).split("\n")
            if not any("GMT" in line for line in first_cell_lines):
                continue

            for line in first_cell_lines:
                if "GMT" in line:
                    break
                if line and not any(char.isdigit() for char in line):
                    city_clean = line.split("(")[0].strip()
                    if city_clean and len(city_clean) > 1:
                        cities_set.add(city_clean)

    return sorted(cities_set)


def scrape_f1_schedule(city_input):
    # Fetches the race schedule for a given city, along with the name of the GP
    url = "https://www.f1latam.com/horarios.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    city_key = city_input.lower().strip()
    default_session_names = [
        "Libres 1",
        "Libres 2",
        "Libres 3",
        "Clasificación",
        "Carrera",
    ]

    # Extract GP name
    gp_anchor = soup.select_one("p.titsecc > a.titnotautos")
    gp_city_name = "Grand Prix"
    if gp_anchor:
        gp_text = gp_anchor.get_text(strip=True)
        if " - " in gp_text:
            gp_name, circuit = map(str.strip, gp_text.split(" - ", 1))
            gp_city_name = f"{gp_name} 🏁 {circuit}"
        else:
            gp_city_name = f"{gp_text.strip()} 🏁"

    print(f"\n📍 Detected Grand Prix: {gp_city_name}")

    for table in soup.find_all("table"):
        thead = table.find("thead")
        tbody = table.find("tbody")
        if not tbody or not thead:
            continue

        rows = tbody.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            first_cell_lines = cells[0].get_text(separator="\n", strip=True).split("\n")
            gmt_label = next((line for line in first_cell_lines if "GMT" in line), None)
            city_lines = [
                line.split("(")[0].strip().lower()
                for line in first_cell_lines
                if line != gmt_label
            ]

            if city_key not in city_lines:
                continue

            schedule = []
            for i in range(1, len(cells)):
                session_time = cells[i].get_text(strip=True)
                session_name = (
                    default_session_names[i - 1]
                    if i - 1 < len(default_session_names)
                    else f"Session {i}"
                )
                if session_time:
                    schedule.append((session_name, session_time))
            return schedule, gp_city_name

    print(f"\n❌ City '{city_input}' not found in any GMT block.")
    return []


def event_exists(service, calendar_id, summary, start_time):
    # Checks if the event already exists on the calendar to prevent duplicates
    time_min = start_time.isoformat()
    time_max = (start_time + timedelta(minutes=1)).isoformat()

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            q=summary,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return len(events_result.get("items", [])) > 0


def create_event(service, summary, start_time, timezone="America/Bogota"):
    # Creates a calendar event with reminders and deduplication
    calendar_id = get_primary_calendar_id(service)

    if event_exists(service, calendar_id, summary, start_time):
        print(
            f"🔁 Skipping duplicate: {summary} at {start_time.strftime('%Y-%m-%d %H:%M')}"
        )
        return

    start = start_time.isoformat()
    duration = 2 if "Carrera" in summary else 1
    end = (start_time + timedelta(hours=duration)).isoformat()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end,
            "timeZone": timezone,
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 720},  # 12 hours
                {"method": "popup", "minutes": 30},  # 30 minutes
                {"method": "popup", "minutes": 10},  # 10 minutes
            ],
        },
        "colorId": "11",  # Tomato red
    }

    print(
        f"📌 Adding to calendar: {calendar_id} -> {summary} at {start_time.strftime('%Y-%m-%d %H:%M')}"
    )
    service.events().insert(calendarId=calendar_id, body=event).execute()


def parse_and_add_events(schedule_data, timezone, dry_run):
    # Parses scraped schedule and inserts them to the calendar or prints them
    if not schedule_data:
        print("\n⚠️ No events to process.")
        return

    schedule, gp_city = schedule_data
    tz = pytz.timezone(timezone)
    today = tz.localize(datetime.today())
    year = today.year

    print("\n📅 Parsed Events:")
    month_map = {
        "ene": 1,
        "feb": 2,
        "mar": 3,
        "abr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "ago": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dic": 12,
    }

    service = authenticate_google() if not dry_run else None

    for session, time_str in schedule:
        try:
            time_str = re.sub(r"(\d{1,2}:\d{2})([A-Za-z])", r"\1 \2", time_str)
            parts = time_str.strip().split()

            if len(parts) != 3:
                raise ValueError("Invalid format")

            time_part, month_name, day_str = parts
            hour, minute = map(int, time_part.split(":"))
            month = month_map[month_name[:3].lower()]
            day = int(day_str)

            dt = tz.localize(datetime(year, month, day, hour, minute))
            if abs((dt - today).days) > 365:
                raise ValueError("Date is more than a year away. Possibly invalid.")

            print(f"- {session}: {dt.strftime('%Y-%m-%d %H:%M %Z')}")

            if not dry_run:
                create_event(service, f"F1: {session} - {gp_city}", dt, timezone)

        except Exception as e:
            print(f"❌ Failed to parse '{session} - {time_str}': {e}")


def main():
    # Entry point for CLI usage and argument parsing
    parser = argparse.ArgumentParser(description="F1 Schedule to Google Calendar")
    parser.add_argument(
        "--city", type=str, help="City name (e.g., Bogotá)", required=False
    )
    parser.add_argument(
        "--timezone",
        type=str,
        default="America/Bogota",
        help="Timezone for calendar events",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview events without inserting to calendar",
    )
    parser.add_argument(
        "--list-cities", action="store_true", help="List available cities"
    )
    parser.add_argument(
        "--check-calendar",
        action="store_true",
        help="Check if Google Calendar credentials are valid",
    )

    args = parser.parse_args()

    if args.check_calendar:
        print("\n🔎 Checking Google Calendar credentials...")
        check_google_calendar_connection()
        return

    if args.list_cities:
        print("\n🌍 Available cities:")
        cities = extract_available_cities()
        for city in cities:
            print(f"- {city}")
        return

    if not args.city:
        print(
            "\n❌ You must specify a city with --city or use --list-cities to see options."
        )
        return

    if not args.dry_run:
        if not check_google_calendar_connection():
            print("⚠️ Exiting due to failed Calendar connection.")
            return

    print(f"\n🌐 Fetching F1 schedule for: {args.city}")
    schedule_data = scrape_f1_schedule(args.city)
    parse_and_add_events(schedule_data, args.timezone, args.dry_run)


if __name__ == "__main__":
    main()


# f1Calendar.py
# This script is designed to scrape the F1 schedule from a website, parse the events for a specified city,
# and optionally add them to a Google Calendar. It includes functionality to list available cities,
# authenticate with Google, and handle timezones. The script can be run with command-line arguments
# to specify the city, timezone, and whether to perform a dry run (preview events without adding them to the calendar).
# It uses BeautifulSoup for web scraping, pytz for timezone handling, and the Google Calendar API for event management.
# The script also includes error handling for parsing issues and provides feedback on the success or failure of operations.
# Make sure to have the necessary credentials.json file for Google Calendar API authentication
# and the required libraries installed in your Python environment.
# To run the script, use the command line with appropriate arguments, e.g.:
# python f1Calendar.py --city "Bogotá" --timezone "America/Bogota" --dry-run
# or to list available cities:
# python f1Calendar.py --list-cities
# Ensure you have the required libraries installed:
# pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client
# and have your Google Calendar API credentials set up correctly.
# You can also run the script without any arguments to see the help message:
# python f1Calendar.py --help
# This will show you the available options and how to use the script.
# Make sure to have a valid `credentials.json` file in the same directory as this script
# for Google Calendar API authentication.
# The script is designed to be user-friendly and provides clear output for each step,
# including any errors encountered during parsing or event creation.
# If you encounter any issues, check the console output for error messages and ensure your environment is set up correctly.
# You can also modify the script to suit your needs, such as changing the default timezone or adding more error handling.
# Happy coding! 🚀

# import datetime
import os
import os.path
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
from typing import Optional
import typer
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing_extensions import Annotated
from rich.console import Console

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CALENDAR_ID = os.getenv("CALENDAR_ID")

console = Console()


@dataclass
class Event:
    title: str
    start: str
    end: str


@dataclass
class Calendar:
    title: str
    events: List[Event]


def get_calendar() -> Calendar:
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        events_result = (service.events().list(calendarId=CALENDAR_ID).execute())
        calendar_name = events_result.get("summary")

        events = []
        for event in events_result.get("items", []):
            try:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                events.append(Event(event["summary"], start, end))
            except KeyError:
                pass

        calendar = Calendar(calendar_name, events)
        return calendar

    except HttpError as error:
        print(f"An error occurred: {error}")


def check_title_to_skip(title: str, to_skip: Optional[List[str]] = None) -> bool:
    if to_skip is None:
        return False

    return any(title.startswith(skip) for skip in to_skip)


def get_selected_date(event_start: str, year: Optional[int] = None, month: Optional[int] = None) -> bool:
    if (year is not None and month is not None):
        start_time = datetime.fromisoformat(event_start)
        if start_time.year != year or start_time.month != month:
            return False
    return True


def calculate_total_time_grouped_by_event_name(events: List[Event], year: Optional[int] = None,
                                               month: Optional[int] = None,
                                               to_skip: Optional[List[str]] = None) -> Dict[str, float]:
    total_time_by_event = defaultdict(float)

    for event in events:
        if not get_selected_date(event.start, year, month):
            continue

        if check_title_to_skip(event.title, to_skip):
            continue

        start_time = datetime.fromisoformat(event.start)
        end_time = datetime.fromisoformat(event.end)
        duration_seconds = (end_time - start_time).total_seconds()
        total_time_by_event[event.title] += duration_seconds / 3600

    return dict(total_time_by_event)


def calculate_total_time_grouped_by_month(
        events: List[Event],
        year: Optional[int] = None,
        month: Optional[int] = None,
to_skip: Optional[List[str]] = None
) -> Dict[str, float]:
    total_time_by_month = defaultdict(float)

    for event in events:
        if not get_selected_date(event.start, year, month):
            continue

        if check_title_to_skip(event.title, to_skip):
            continue

        start_time = datetime.fromisoformat(event.start)
        end_time = datetime.fromisoformat(event.end)
        duration_seconds = (end_time - start_time).total_seconds()
        month_year_key = (start_time.year, start_time.month)
        total_time_by_month[month_year_key] += duration_seconds / 3600

    total_time_by_month_str = {
        f"{datetime(year, month, 1).strftime('%B')}-{year}": hours
        for (year, month), hours in total_time_by_month.items()
    }

    return total_time_by_month_str


def calculate_total_time_grouped_by_day(
        events: List[Event],
        year: int = None,
        month: int = None,
to_skip: Optional[List[str]] = None
) -> Dict[str, float]:
    total_time_by_day = defaultdict(float)

    for event in events:
        if not get_selected_date(event.start, year, month):
            continue

        if check_title_to_skip(event.title, to_skip):
            continue

        start_time = datetime.fromisoformat(event.start)
        end_time = datetime.fromisoformat(event.end)
        duration_seconds = (end_time - start_time).total_seconds()
        day_key = start_time.date()
        total_time_by_day[day_key] += duration_seconds / 3600

    total_time_by_day_str = {
        day.strftime("%A %d %B %Y"): hours for day, hours in total_time_by_day.items()
    }

    return total_time_by_day_str


def main(
        skip: Annotated[str, typer.Option()] = None,
        year: Annotated[int, typer.Option()] = None,
        month: Annotated[int, typer.Option(min=1, max=12)] = None
) -> None:
    to_skip = skip
    if skip is not None:
        to_skip = skip.split(",")

    if year and not month or month and not year:
        raise typer.BadParameter("Both year and month must be provided.")

    calendar = get_calendar()

    total_time_by_event_name = calculate_total_time_grouped_by_event_name(calendar.events, year, month, to_skip)
    total_time_by_month = calculate_total_time_grouped_by_month(calendar.events, year, month, to_skip)
    total_time_by_day = calculate_total_time_grouped_by_day(calendar.events, year, month, to_skip)


    console.print("Total time by event name", style="bold green")

    for event_name, hours in total_time_by_event_name.items():
        console.print(f" -> {event_name}: {hours:.2f} hours", style="bold green")

    console.print("\n")

    console.print("Total time by event name", style="bold green")

    for date, hours in total_time_by_month.items():
        console.print(f" -> {date}: {hours:.2f} hours", style="bold green")

    console.print("\n")

    console.print("Total time by event name", style="bold green")

    for date, hours in total_time_by_day.items():
        console.print(f" -> {date}: {hours:.2f} hours", style="bold green")


if __name__ == "__main__":
    typer.run(main)

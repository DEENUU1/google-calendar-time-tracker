# import datetime
import os
import os.path
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict
from collections import defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass


load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

CALENDAR_ID = os.getenv("CALENDAR_ID")


@dataclass
class Event:
    title: str
    start: str
    end: str


@dataclass
class Calendar:
    title: str
    events: List[Event]


def main():
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


def calculate_total_time_grouped_by_event_name(events: List[Event]) -> Dict[str, float]:
    total_time_by_event = defaultdict(float)

    for event in events:
        start_time = datetime.fromisoformat(event.start)
        end_time = datetime.fromisoformat(event.end)
        duration_seconds = (end_time - start_time).total_seconds()
        total_time_by_event[event.title] += duration_seconds / 3600

    return dict(total_time_by_event)


def calculate_total_time_grouped_by_month(events: List[Event]) -> dict:
    pass


def calculate_total_time_grouped_by_day(events: List[Event]) -> dict:
    pass


if __name__ == "__main__":
    calendar = main()

    print(calendar.title)

    for event in calendar.events:
        print(f"{event.title} - {event.start} - {event.end}")

    total_time_by_event_name = calculate_total_time_grouped_by_event_name(calendar.events)
    print(total_time_by_event_name)
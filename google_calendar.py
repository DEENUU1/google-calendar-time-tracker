import os
import os.path
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils import get_selected_date, check_title_to_skip

load_dotenv()


@dataclass
class Event:
    title: str
    start: str
    end: str


@dataclass
class Calendar:
    title: str
    events: List[Event]


class GoogleCalendar:
    def __init__(self):
        self.token_file = "token.json"
        self.credentials_file = "credentials.json"
        self.calendar_id = os.getenv("CALENDAR_ID")
        self.scopes = ["https://www.googleapis.com/auth/calendar.readonly"]

    def write_token(self, creds) -> None:
        with open(self.token_file, "w") as token:
            token.write(creds.to_json())

    def get_credentials(self) -> Optional[Credentials]:
        creds = None

        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)

                self.write_token(creds)

        return creds

    @staticmethod
    def get_processed_events(
            events: List[Event],
            year: Optional[int] = None,
            month: Optional[int] = None,
            to_skip: Optional[List[str]] = None
    ) -> List[Event]:
        res = []
        for event in events:
            if not get_selected_date(event.start, year, month):
                continue

            if check_title_to_skip(event.title, to_skip):
                continue

            res.append(event)
        return res

    def get_calendar(self) -> Optional[Calendar]:
        creds = self.get_credentials()

        try:
            service = build("calendar", "v3", credentials=creds)
            events_result = (service.events().list(calendarId=self.calendar_id).execute())
            calendar_name = events_result.get("summary")

            events = []
            for event in events_result.get("items", []):
                try:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    end = event["end"].get("dateTime", event["end"].get("date"))
                    events.append(Event(event["summary"], start, end))
                except KeyError:
                    continue

            calendar = Calendar(calendar_name, events)
            return calendar

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

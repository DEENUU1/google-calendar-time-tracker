from collections import defaultdict
from datetime import datetime
from typing import List, Dict

from google_calendar import Event


def calculate_total_time_grouped_by_event_name(events: List[Event]) -> Dict[str, float]:
    total_time_by_event = defaultdict(float)

    for event in events:
        start_time = datetime.fromisoformat(event.start)
        end_time = datetime.fromisoformat(event.end)
        duration_seconds = (end_time - start_time).total_seconds()
        total_time_by_event[event.title] += duration_seconds / 3600

    return dict(total_time_by_event)


def calculate_total_time_grouped_by_month(events: List[Event]) -> Dict[str, float]:
    total_time_by_month = defaultdict(float)

    for event in events:
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


def calculate_total_time_grouped_by_day(events: List[Event]) -> Dict[str, float]:
    total_time_by_day = defaultdict(float)

    for event in events:
        start_time = datetime.fromisoformat(event.start)
        end_time = datetime.fromisoformat(event.end)
        duration_seconds = (end_time - start_time).total_seconds()
        day_key = start_time.date()
        total_time_by_day[day_key] += duration_seconds / 3600

    total_time_by_day_str = {
        day.strftime("%A %d %B %Y"): hours for day, hours in total_time_by_day.items()
    }

    return total_time_by_day_str

import typer
from rich.console import Console
from typing_extensions import Annotated

from calcs import (
    calculate_total_time_grouped_by_event_name,
    calculate_total_time_grouped_by_month,
    calculate_total_time_grouped_by_day
)
from google_calendar import GoogleCalendar

console = Console()


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

    google_calendar = GoogleCalendar()
    calendar = google_calendar.get_calendar()

    if not calendar:
        raise typer.Abort("Failed to get calendar.")

    events = google_calendar.get_processed_events(calendar.events, year, month, to_skip)

    total_time_by_event_name = calculate_total_time_grouped_by_event_name(events)
    total_time_by_month = calculate_total_time_grouped_by_month(events)
    total_time_by_day = calculate_total_time_grouped_by_day(events)

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

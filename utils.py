from datetime import datetime
from typing import List
from typing import Optional


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

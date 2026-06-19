"""Result-conversion helpers shared by the MySQL and SQLite db layers."""

import re
from DateTime import DateTime


# DateTime(str) is slow. As the date format is part of the specifications,
# parse it ourselves to save time.
def DATETIME_to_DateTime_or_None(s):
    try:
        date, time = s.split(' ')
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        return DateTime(
            int(year), int(month), int(day),
            int(hour), int(minute), float(second),
            'UTC',
        )
    except Exception:
        return None


def DATE_to_DateTime_or_None(s):
    try:
        year, month, day = s.split('-')
        return DateTime(int(year), int(month), int(day), 0, 0, 0, 'UTC')
    except Exception:
        return None


def ord_or_None(s):
    if s is not None:
        return ord(s)


match_select = re.compile(
    br'(?:SET\s+STATEMENT\s+(.+?)\s+FOR\s+)?SELECT\s+(.+)',
    re.IGNORECASE | re.DOTALL,
).match

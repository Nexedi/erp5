"""
    Returns a duration, in days, for stock cache management.
    If data in stock cache is older than lag compared to query's date
    (at_date or to_date), then it becomes a "soft miss": use found value,
    but add a new entry to cache at query's date minus half the lag.
    So this value should be:
    - Small enough that few enough rows need to be table-scanned for
    verage queries (probably queries against current date).
    - Large enough that few enough documents get modified past that date,
    therwise cache entries would be removed from cache all the time.
"""

return 60

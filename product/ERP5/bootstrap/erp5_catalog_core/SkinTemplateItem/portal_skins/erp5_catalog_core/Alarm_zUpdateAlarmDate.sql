REPLACE INTO
  alarm (uid, alarm_date)
VALUES
  (<dtml-sqlvar uid type="int">, <dtml-sqlvar alarm_date type="datetime" optional>)
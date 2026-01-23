SELECT priority AS pri,
  TIME_FORMAT(TIMEDIFF(UTC_TIMESTAMP(6), MAX(date)), '%T') AS min,
  TIME_FORMAT(TIMEDIFF(UTC_TIMESTAMP(6), AVG(date)), '%T') AS avg,
  TIME_FORMAT(TIMEDIFF(UTC_TIMESTAMP(6), MIN(date)), '%T') AS max
FROM <dtml-var table> GROUP BY priority
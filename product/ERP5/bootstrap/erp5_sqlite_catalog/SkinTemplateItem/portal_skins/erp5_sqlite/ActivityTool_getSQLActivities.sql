SELECT 
  priority AS pri,
  time(
    (julianday('now') - julianday(MAX(date))) * 86400,
    'unixepoch'
  ) AS min,
  time(
    (julianday('now') - julianday(AVG(date))) * 86400,
    'unixepoch'
  ) AS avg,
  time(
    (julianday('now') - julianday(MIN(date))) * 86400,
    'unixepoch'
  ) AS max
FROM <dtml-var table>
GROUP BY priority;

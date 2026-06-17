SELECT
  uid, path
FROM
  record
WHERE
  played = 0
  AND catalog = <dtml-sqlvar catalog type="int"> 
ORDER BY
  date

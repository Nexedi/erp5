SELECT 
  alarm_date
FROM
  alarm
WHERE
  uid = <dtml-sqlvar uid type="int">
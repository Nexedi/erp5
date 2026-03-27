<dtml-let column_list="['alarm_date']">
INSERT INTO
  alarm (`uid`, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
VALUES
  (<dtml-sqlvar uid type="int">, <dtml-sqlvar alarm_date type="datetime" optional>)
ON DUPLICATE KEY UPDATE
<dtml-in column_list>
  `<dtml-var sequence-item>` = VALUES(<dtml-var sequence-item>)<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
</dtml-let>

REPLACE INTO
  alarm (uid, alarm_date)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getAlarmDate[loop_item]" type="datetime" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>

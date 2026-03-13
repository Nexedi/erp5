<dtml-let column_list="['frequency_index', 'creation_date_index']">
INSERT INTO
  crawler (uid, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="getFrequencyIndex[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getCreationDateIndex[loop_item]" type="int" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>
ON DUPLICATE KEY UPDATE
<dtml-in column_list>
  `<dtml-var sequence-item>` = VALUES(<dtml-var sequence-item>)<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
</dtml-let>

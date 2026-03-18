<dtml-let column_list="['title', 'description']">
INSERT INTO
  catalog_full_text (`uid`, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="getTitle[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDescription[loop_item]" type="string" optional>
)<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>
ON DUPLICATE KEY UPDATE
<dtml-in column_list>
  `<dtml-var sequence-item>` = VALUES(<dtml-var sequence-item>)<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
</dtml-let>

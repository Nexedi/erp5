<dtml-let column_list="['gid', 'data']">
INSERT INTO
  syncml (`path`, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(getPath))">
(
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,
  <dtml-sqlvar expr="getId[loop_item]" type="string">,
  <dtml-sqlvar expr="getData[loop_item]" type="string">
)<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>
ON DUPLICATE KEY UPDATE
<dtml-in column_list>
  `<dtml-var sequence-item>` = VALUES(`<dtml-var sequence-item>`)<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
</dtml-let>

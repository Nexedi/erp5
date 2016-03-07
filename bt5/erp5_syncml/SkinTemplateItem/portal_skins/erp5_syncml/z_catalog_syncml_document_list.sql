REPLACE INTO
  syncml (`path`, `gid`, `data`)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(getPath))">
(
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,
  <dtml-sqlvar expr="getId[loop_item]" type="string">,
  <dtml-sqlvar expr="getData[loop_item]" type="string">
)<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>

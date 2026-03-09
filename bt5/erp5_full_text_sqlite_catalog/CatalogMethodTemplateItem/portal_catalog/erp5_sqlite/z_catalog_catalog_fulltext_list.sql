REPLACE INTO
  catalog_full_text (`uid`, `title`, `description`)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="getTitle[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDescription[loop_item]" type="string" optional>
)<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>

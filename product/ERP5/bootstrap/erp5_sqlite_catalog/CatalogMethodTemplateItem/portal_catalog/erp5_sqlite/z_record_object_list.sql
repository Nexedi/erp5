INSERT INTO
  record (path, catalog, played, date)
VALUES
<dtml-in path_list>
(
  <dtml-sqlvar sequence-item type="string">,
  <dtml-sqlvar catalog type="int">,
  0,
  CURRENT_TIMESTAMP
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>

CREATE TABLE portal_ids (
  id_group TEXT PRIMARY KEY,
  last_id INTEGER
);

<dtml-var sql_delimiter>
<dtml-in expr="getPortalObject().portal_ids.getDictLengthIdsItems()">
INSERT INTO portal_ids (id_group, last_id) 
VALUES (<dtml-sqlvar sequence-key type="string">, <dtml-sqlvar sequence-item type="int">);
<dtml-var sql_delimiter>
</dtml-in>

COMMIT
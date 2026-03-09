<dtml-let column_list="['path', 'relative_url', 'security_uid', 'portal_type', 'parent_uid']">
INSERT INTO
  catalog (`uid`, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
VALUES
  (<dtml-sqlvar uid type="int">, 'deleted','',NULL,'',NULL)
ON DUPLICATE KEY UPDATE
<dtml-in column_list>
  `<dtml-var sequence-item>` = VALUES(<dtml-var sequence-item>)<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
</dtml-let>
<dtml-var sql_delimiter>
<dtml-if expr="'deleted_catalog' in portal_catalog.getSQLCatalog().getTableIds()">
<dtml-let column_list="['path']">
INSERT INTO
  deleted_catalog (`uid`, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
VALUES
  (<dtml-sqlvar uid type="int">, <dtml-sqlvar path type="string">)
ON DUPLICATE KEY UPDATE
<dtml-in column_list>
  `<dtml-var sequence-item>` = VALUES(<dtml-var sequence-item>),
</dtml-in>
  `deletion_timestamp` = DEFAULT
</dtml-let>
<dtml-var sql_delimiter>
</dtml-if>
<dtml-comment>
  Note on "UPDATE stock" query: this query preserve transactionality of movement
  deletion: all movements deleted in a single transaction will be either
  simultaneously found by Inventory Tool API, or simultaneously not found.
  This does not change anything WRT inventories, modulo unindexation lag.
</dtml-comment>
UPDATE stock
SET simulation_state=''
WHERE uid=<dtml-sqlvar uid type="int">

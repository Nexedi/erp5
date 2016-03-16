REPLACE INTO
  catalog (uid, path,relative_url,security_uid,portal_type,parent_uid)
VALUES
  (<dtml-sqlvar uid type="int">, 'deleted','',NULL,'',NULL)
<dtml-var sql_delimiter>
<dtml-comment>
  Note on "UPDATE stock" query: this query preserve transactionality of movement
  deletion: all movements deleted in a single transaction will be either
  simultaneously found by Inventory Tool API, or simultaneously not found.
  This does not change anything WRT inventories, modulo unindexation lag.
</dtml-comment>
UPDATE stock
SET simulation_state=''
WHERE uid=<dtml-sqlvar uid type="int">

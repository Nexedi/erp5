BEGIN
<dtml-var sql_delimiter>
INSERT INTO portal_ids (`id_group`, `last_id`)
 VALUES (<dtml-sqlvar id_group type="string">, <dtml-sqlvar last_id type="int">)
 ON DUPLICATE KEY UPDATE `last_id` = <dtml-sqlvar last_id type="int">
<dtml-var sql_delimiter>
COMMIT
# DO NOT FORGET TO COMMIT AFTER !!
# commit ZSQL method should be z_portal_ids_commit

BEGIN
<dtml-var sql_delimiter>
INSERT INTO portal_ids (`id_group`, `last_id`) VALUES (<dtml-sqlvar id_group type="string">, LAST_INSERT_ID(<dtml-sqlvar default type="int">)) ON DUPLICATE KEY UPDATE `last_id` = LAST_INSERT_ID(`last_id` + 1)
<dtml-var sql_delimiter>
SELECT LAST_INSERT_ID()
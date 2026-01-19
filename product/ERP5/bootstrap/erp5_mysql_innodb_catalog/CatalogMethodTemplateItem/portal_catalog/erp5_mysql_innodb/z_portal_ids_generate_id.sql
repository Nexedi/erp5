# Warning : This method is obsolete, the new method is IdTool_zGenerateId
#           it's kept for backward compatiblity

# DO NOT FORGET TO COMMIT AFTER !!
# commit ZSQL method should be z_portal_ids_commit

BEGIN
<dtml-var sql_delimiter>
INSERT INTO portal_ids (`id_group`, `last_id`)
 VALUES (<dtml-sqlvar id_group type="string">, <dtml-sqlvar expr="id_count + default" type="int">)
 ON DUPLICATE KEY UPDATE `last_id` = `last_id` + <dtml-sqlvar id_count type="int">
<dtml-var sql_delimiter>
SELECT `last_id` AS `LAST_INSERT_ID` FROM portal_ids
 WHERE `id_group` = <dtml-sqlvar id_group type="string">

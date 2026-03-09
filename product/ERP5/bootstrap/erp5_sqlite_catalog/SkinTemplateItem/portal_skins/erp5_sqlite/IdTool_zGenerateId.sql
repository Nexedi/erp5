-- DO NOT FORGET TO COMMIT AFTER !!
-- commit ZSQL method should be IdTool_zCommit

BEGIN

<dtml-var sql_delimiter>
INSERT INTO portal_ids (id_group, last_id)
VALUES (<dtml-sqlvar id_group type="string">,
        <dtml-sqlvar expr="id_count - 1 + default" type="int">)
ON CONFLICT(id_group) DO UPDATE SET
    last_id = last_id + <dtml-sqlvar id_count type="int">
<dtml-var sql_delimiter>

SELECT `last_id` AS `LAST_INSERT_ID` FROM portal_ids
 WHERE `id_group` = <dtml-sqlvar id_group type="string">

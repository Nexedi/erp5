<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>id_group\r\n
id_count:int=1\r\n
default:int=1</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_transactionless_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_portal_ids_generate_id</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

# Warning : This method is obsolete, the new method is IdTool_zGenerateId\n
#           it\'s kept for backward compatiblity\n
\n
# DO NOT FORGET TO COMMIT AFTER !!\n
# commit ZSQL method should be z_portal_ids_commit\n
\n
BEGIN\n
<dtml-var sql_delimiter>\n
INSERT INTO portal_ids (`id_group`, `last_id`)\n
 VALUES (<dtml-sqlvar id_group type="string">, <dtml-sqlvar expr="id_count + default" type="int">)\n
 ON DUPLICATE KEY UPDATE `last_id` = `last_id` + <dtml-sqlvar id_count type="int">\n
<dtml-var sql_delimiter>\n
SELECT `last_id` AS `LAST_INSERT_ID()` FROM portal_ids\n
 WHERE `id_group` = <dtml-sqlvar id_group type="string">\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>

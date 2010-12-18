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
last_id:int=0</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_transactionless_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IdTool_zSetLastId</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

BEGIN\n
<dtml-var sql_delimiter>\n
INSERT INTO portal_ids (`id_group`, `last_id`)\n
 VALUES (<dtml-sqlvar id_group type="string">, <dtml-sqlvar last_id type="int">)\n
 ON DUPLICATE KEY UPDATE `last_id` = <dtml-sqlvar last_id type="int">\n
<dtml-var sql_delimiter>\n
COMMIT

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

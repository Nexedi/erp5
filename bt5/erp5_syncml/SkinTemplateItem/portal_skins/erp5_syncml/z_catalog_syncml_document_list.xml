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
            <value> <string>getId\r\n
getPath\r\n
getData\r\n
</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_catalog_syncml_document_list</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

REPLACE INTO\n
  syncml (`path`, `gid`, `data`)\n
VALUES\n
<dtml-in prefix="loop" expr="_.range(_.len(getPath))">\n
(\n
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,\n
  <dtml-sqlvar expr="getId[loop_item]" type="string">,\n
  <dtml-sqlvar expr="getData[loop_item]" type="string">\n
)<dtml-unless sequence-end>,</dtml-unless>\n
</dtml-in>\n


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

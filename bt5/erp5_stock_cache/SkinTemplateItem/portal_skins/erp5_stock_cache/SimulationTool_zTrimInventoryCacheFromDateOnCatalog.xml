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
            <value> <string>uid_list\r\n
min_date</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SimulationTool_zTrimInventoryCacheFromDateOnCatalog</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

DELETE \n
FROM \n
  inventory_cache \n
WHERE \n
  date > (SELECT min(date) from stock where <dtml-sqltest uid_list column=uid type=int multiple>)\n
<dtml-if min_date>\n
OR\n
  date > <dtml-sqlvar expr="min_date" type="datetime">\n
</dtml-if>\n
\n


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

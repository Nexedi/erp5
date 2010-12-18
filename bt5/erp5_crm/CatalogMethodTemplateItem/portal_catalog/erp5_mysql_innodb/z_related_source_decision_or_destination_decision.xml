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
            <value> <string>table_0\r\n
table_1\r\n
table_2</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_related_source_decision_or_destination_decision</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-comment>\n
table_0 : category as source_decision or destination_decision\n
table_1 : catalog as category\n
table_2 : catalog as object_uid\n
</dtml-comment>\n
\n
( \n
  <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.source_decision.getUid()">\n
  OR \n
  <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.destination_decision.getUid()">\n
)\n
AND\n
<dtml-var table_0>.category_uid = <dtml-var table_2>.uid AND\n
<dtml-var table_0>.uid = <dtml-var table_1>.uid AND\n
<dtml-var table_1>.uid = catalog.uid\n


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

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
            <value> <string>cmf_activity_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_related_explanation_destination_section</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-var table_0>.uid = catalog.uid\n
 AND <dtml-var table_0>.explanation_uid = <dtml-var table_1>.uid\n
 AND <dtml-var table_1>.base_category_uid = <dtml-var "portal_categories.destination_section.getUid()">\n
 AND <dtml-var table_1>.category_uid = <dtml-var table_2>.uid\n


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

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
RELATED_QUERY_SEPARATOR=" AND "\r\n
query_table="catalog"</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_related_preferred_gap</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-var table_1>.uid = <dtml-var table_0>.category_uid\n
<dtml-if expr="portal_preferences.getPreferredAccountingTransactionGap()">\n
  AND <dtml-var table_1>.relative_url LIKE <dtml-sqlvar expr="portal_preferences.getPreferredAccountingTransactionGap()+\'%\'" type="string">\n
</dtml-if>\n
<dtml-var RELATED_QUERY_SEPARATOR>\n
 <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.gap.getUid()">\n
AND <dtml-var table_0>.uid = <dtml-var query_table>.uid

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

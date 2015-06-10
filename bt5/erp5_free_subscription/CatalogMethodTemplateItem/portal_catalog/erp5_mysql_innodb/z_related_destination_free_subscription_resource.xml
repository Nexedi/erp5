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
table_2\r\n
table_3\r\n
table_4\r\n
RELATED_QUERY_SEPARATOR=" AND "\r\n
query_table="catalog"</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_related_destination_free_subscription_resource</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.destination.getUid()">\n
AND <dtml-var table_1>.uid = <dtml-var table_0>.uid\n
AND <dtml-var table_1>.portal_type = \'Free Subscription\'\n
AND <dtml-var table_1>.validation_state = \'validated\'\n
\n
<dtml-var RELATED_QUERY_SEPARATOR>\n
<dtml-var table_0>.category_uid = <dtml-var query_table>.uid\n
\n
<dtml-var RELATED_QUERY_SEPARATOR>\n
<dtml-var table_0>.uid = <dtml-var table_2>.uid\n
AND <dtml-var table_2>.base_category_uid = <dtml-var "portal_categories.resource.getUid()">\n
\n
<dtml-var RELATED_QUERY_SEPARATOR>\n
<dtml-var table_2>.category_uid = <dtml-var table_4>.uid\n
AND <dtml-var table_4>.portal_type = \'Service\'\n
\n
<dtml-var RELATED_QUERY_SEPARATOR>\n
<dtml-var table_3>.uid = <dtml-var table_1>.uid\n
<dtml-let now="DateTime()">\n
  AND ( <dtml-var table_3>.effective_date is NULL OR <dtml-var table_3>.effective_date <= <dtml-sqlvar now type="datetime"> ) \n
  AND ( <dtml-var table_3>.expiration_date is NULL OR <dtml-var table_3>.expiration_date >= <dtml-sqlvar now type="datetime"> )\n
</dtml-let>\n


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

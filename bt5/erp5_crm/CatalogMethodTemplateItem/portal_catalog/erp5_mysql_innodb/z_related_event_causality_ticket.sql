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
table_3</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_related_event_causality_ticket</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-var table_3>.uid = <dtml-var table_2>.category_uid\n
AND <dtml-var table_1>.uid = <dtml-var table_2>.uid\n
AND <dtml-var table_1>.uid = <dtml-var table_0>.category_uid\n
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.causality.getUid()">\n
AND catalog.uid = <dtml-var table_0>.uid\n
AND (<dtml-in "portal_catalog.getPortalEventTypeList()">\n
  <dtml-if sequence-start>\n
    <dtml-var table_1>.portal_type = \'<dtml-var sequence-item>\'\n
  <dtml-else>\n
    OR <dtml-var table_1>.portal_type = \'<dtml-var sequence-item>\'\n
  </dtml-if>\n
</dtml-in>)\n
AND\n
  (SELECT count(*) from category as sub_category\n
    WHERE sub_category.uid = catalog.uid\n
    AND sub_category.base_category_uid = <dtml-var "portal_categories.follow_up.getUid()">\n
    AND sub_category.category_uid = <dtml-var table_3>.uid\n
    LIMIT 1 ) = 0\n


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

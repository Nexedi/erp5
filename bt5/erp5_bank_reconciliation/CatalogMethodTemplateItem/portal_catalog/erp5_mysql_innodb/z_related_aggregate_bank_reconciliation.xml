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
query_table\r\n
RELATED_QUERY_SEPARATOR=" AND "</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_related_aggregate_bank_reconciliation</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-var table_1>.uid = <dtml-var table_0>.category_uid\n
AND <dtml-var table_1>.portal_type = "Bank Reconciliation"\n
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.aggregate.getUid()">\n
<dtml-if table_2><dtml-comment>This related key can also be used with a criterion on delivery.date, in this case we join with a 3rd table</dtml-comment>\n
  <dtml-var RELATED_QUERY_SEPARATOR>\n
  <dtml-var table_2>.uid = <dtml-var table_1>.uid\n
</dtml-if>\n
<dtml-var RELATED_QUERY_SEPARATOR>\n
<dtml-var table_0>.uid = <dtml-var query_table>.uid

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

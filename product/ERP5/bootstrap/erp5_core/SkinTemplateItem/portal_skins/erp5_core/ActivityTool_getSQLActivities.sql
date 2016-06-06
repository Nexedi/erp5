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
            <value> <string>table</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>cmf_activity_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ActivityTool_getSQLActivities</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

SELECT priority as pri, MIN(timediff(NOW(), date)) AS min, AVG(timediff(NOW() , date)) AS avg, MAX(timediff(NOW() , date)) AS max FROM <dtml-var table> GROUP BY priority;

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

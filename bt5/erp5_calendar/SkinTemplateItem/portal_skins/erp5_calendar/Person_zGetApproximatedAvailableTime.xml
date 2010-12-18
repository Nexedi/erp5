<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Use_Database_Methods_Permission</string> </key>
            <value>
              <list>
                <string>Member</string>
              </list>
            </value>
        </item>
        <item>
            <key> <string>allow_simple_one_argument_traversal</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>from_date\r\n
to_date\r\n
node:list\r\n
resource:list\r\n
portal_type:list</string> </value>
        </item>
        <item>
            <key> <string>cache_time_</string> </key>
            <value> <int>0</int> </value>
        </item>
        <item>
            <key> <string>class_file_</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>class_name_</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>connection_hook</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_zGetApproximatedAvailableTime</string> </value>
        </item>
        <item>
            <key> <string>max_cache_</string> </key>
            <value> <int>100</int> </value>
        </item>
        <item>
            <key> <string>max_rows_</string> </key>
            <value> <int>1000</int> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

SELECT\n
  CASE \n
    WHEN (mirror_date=date) THEN \n
      SUM(quantity)\n
    ELSE\n
      SUM(quantity * TIME_TO_SEC(TIMEDIFF(LEAST(<dtml-sqlvar expr="to_date" type="datetime">, mirror_date), \n
                                          GREATEST(date, <dtml-sqlvar expr="from_date" type="datetime">))) / \n
                     TIME_TO_SEC(TIMEDIFF(mirror_date, date)))\n
  END AS total_quantity,\n
  <dtml-sqlvar expr="from_date" type="datetime"> AS from_date,\n
  <dtml-sqlvar expr="to_date" type="datetime"> AS to_date\n
FROM\n
  stock\n
WHERE\n
  (date < <dtml-sqlvar expr="to_date" type="datetime">) \n
AND \n
  (mirror_date >= <dtml-sqlvar expr="from_date" type="datetime">)\n
AND\n
  node_uid in (\n
    <dtml-in node>\n
      <dtml-sqlvar sequence-item type="int">\n
      <dtml-unless sequence-end>, </dtml-unless> \n
    </dtml-in node> )\n
\n
<dtml-if resource>\n
  AND\n
  resource_uid in (\n
    <dtml-in resource>\n
      <dtml-sqlvar sequence-item type="int">\n
      <dtml-unless sequence-end>, </dtml-unless> \n
    </dtml-in resource> )\n
</dtml-if>\n
\n
AND\n
  portal_type in (\n
    <dtml-in portal_type>\n
      <dtml-sqlvar sequence-item type="string">\n
      <dtml-unless sequence-end>, </dtml-unless> \n
    </dtml-in portal_type> )

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

<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>allow_simple_one_argument_traversal</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>arguments_src</string> </key>
            <value> <string>isMovement\n
uid\n
getExplanationUid\n
getSourceUid\n
getDestinationUid\n
getResourceUid\n
getQuantity\n
getStartDate\n
getStopDate\n
getPrice\n
isAccountable\n
isDivergent\n
getVariationText</string> </value>
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
            <value> <string>z_catalog_movement_list</string> </value>
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

DELETE FROM\n
  movement\n
WHERE\n
<dtml-in uid>\n
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>\n
</dtml-in>\n
;\n
\n
<dtml-var "\'\\0\'"><dtml-let movement_list="[]">\n
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">\n
    <dtml-if "isMovement[loop_item]">\n
      <dtml-call expr="movement_list.append(loop_item)">\n
    </dtml-if>\n
  </dtml-in>\n
  <dtml-if expr="_.len(movement_list) > 0">\n
INSERT INTO\n
  movement\n
VALUES\n
    <dtml-in prefix="loop" expr="movement_list">\n
( \n
  <dtml-sqlvar expr="uid[loop_item]" type="int">,\n
  <dtml-sqlvar expr="getExplanationUid[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getSourceUid[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getDestinationUid[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getResourceUid[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getQuantity[loop_item]" type="float" optional>,\n
  <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getStopDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getPrice[loop_item]" type="float" optional>,\n
  <dtml-sqlvar expr="isAccountable[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="isDivergent[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getVariationText[loop_item]" type="string" optional>\n
)\n
<dtml-if sequence-end><dtml-else>,</dtml-if>\n
    </dtml-in>\n
  </dtml-if>\n
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

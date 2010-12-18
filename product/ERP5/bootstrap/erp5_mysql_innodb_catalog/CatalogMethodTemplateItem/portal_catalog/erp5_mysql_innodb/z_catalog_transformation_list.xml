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
            <value> <string>row_dict_dict_list</string> </value>
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
            <value> <string>z_catalog_transformation_list</string> </value>
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

<dtml-let row_list="[]">\n
<dtml-in row_dict_dict_list prefix="outer">\n
DELETE FROM `transformation` WHERE\n
  <dtml-sqltest expr="outer_item[\'uid\']" column="uid" type="int">\n
  AND\n
  <dtml-sqltest expr="outer_item[\'variation_text\']" column="variation_text" type="string">;\n
<dtml-var sql_delimiter>\n
<dtml-call "row_list.extend(outer_item[\'row_dict_list\'])">\n
</dtml-in>\n
\n
<dtml-if "len(row_list)>0">\n
<dtml-var sql_delimiter>\n
\n
INSERT INTO `transformation`\n
VALUES\n
    <dtml-in row_list prefix="loop">\n
(\n
  <dtml-sqlvar expr="loop_item[\'uid\']" type="int">,\n
  <dtml-sqlvar expr="loop_item[\'variation_text\']" type="string">,\n
  <dtml-sqlvar expr="loop_item[\'transformed_uid\']" type="int">,\n
  <dtml-sqlvar expr="loop_item[\'transformed_variation_text\']" type="string">,\n
  <dtml-sqlvar expr="loop_item[\'quantity\']" type="float">\n
)\n
<dtml-unless sequence-end>,</dtml-unless>\n
    </dtml-in>\n
</dtml-if>\n
</dtml-let>

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

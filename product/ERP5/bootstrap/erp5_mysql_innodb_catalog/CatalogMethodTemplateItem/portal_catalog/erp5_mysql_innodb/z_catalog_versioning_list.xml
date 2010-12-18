<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="SQL" module="Products.ZSQLMethods.SQL"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_col</string> </key>
            <value>
              <tuple/>
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
            <value> <string>uid\r\n
getLanguage\r\n
getVersion\r\n
getRevision\r\n
subject_set_uid\r\n
getEffectiveDate\r\n
getExpirationDate\r\n
getCreationDateIndex\r\n
getFrequencyIndex\r\n
</string> </value>
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
            <value> <string>z_catalog_versioning_list</string> </value>
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

REPLACE INTO\n
  versioning\n
  (`uid`, `version`, `language`, `revision`, `subject_set_uid`, `effective_date`,\n
   `expiration_date`, `creation_date_index`, `frequency_index`)\n
VALUES\n
<dtml-in prefix="loop" expr="_.range(_.len(uid))">\n
(\n
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  \n
  <dtml-sqlvar expr="getVersion[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getLanguage[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getRevision[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="subject_set_uid[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getEffectiveDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getExpirationDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getCreationDateIndex[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getFrequencyIndex[loop_item]" type="int" optional>\n
)\n
<dtml-if sequence-end>\n
<dtml-else>\n
,\n
</dtml-if>\n
</dtml-in>\n


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

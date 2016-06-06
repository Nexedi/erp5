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
            <value> <string>uid\r\n
security_uid\r\n
getViewPermissionOwner\r\n
getPath\r\n
getRelativeUrl\r\n
getParentUid\r\n
id\r\n
getDescription\r\n
getTitle\r\n
getPortalType\r\n
getSimulationState\r\n
getValidationState\r\n
getReference\r\n
getSourceReference\r\n
getStringIndex\r\n
getIntIndex\r\n
hasCellContent\r\n
getCreationDate\r\n
getModificationDate\r\n
getStartDate\r\n
getStopDate</string> </value>
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
            <value> <string>z_catalog_object_list</string> </value>
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
  catalog\n
  (`uid`, `security_uid`, `path`, `owner`, `relative_url`, `parent_uid`, `id`, `description`, `title`,\n
   `portal_type`, `validation_state`, `simulation_state`,\n
   `reference`,\n
   `source_reference`, `string_index`, `int_index`, `has_cell_content`, `creation_date`,\n
   `modification_date`, `start_date`, `stop_date`, `indexation_date`)\n
VALUES\n
<dtml-in prefix="loop" expr="_.range(_.len(uid))">\n
(\n
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  \n
  <dtml-sqlvar expr="security_uid[loop_item]" type="int">,\n
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,\n
  <dtml-sqlvar expr="(getViewPermissionOwner[loop_item] is not None) and getViewPermissionOwner[loop_item] or \'\'" type="string" optional>,\n
  <dtml-sqlvar expr="getRelativeUrl[loop_item]" type="string">,\n
  <dtml-sqlvar expr="getParentUid[loop_item]" type="int">,\n
  <dtml-sqlvar expr="id[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getDescription[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getTitle[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getPortalType[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getValidationState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getSimulationState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getReference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getSourceReference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getStringIndex[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getIntIndex[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="hasCellContent[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getCreationDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getModificationDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getStopDate[loop_item]" type="datetime" optional>,\n
  null\n
)\n
<dtml-if sequence-end><dtml-else>,</dtml-if>\n
</dtml-in>

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

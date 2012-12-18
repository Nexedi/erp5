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
getOwnerInfo\r\n
getViewPermissionOwner\r\n
getPath\r\n
getRelativeUrl\r\n
getParentUid\r\n
id\r\n
getDescription\r\n
getTitle\r\n
meta_type\r\n
getPortalType\r\n
getOpportunityState\r\n
getCorporateRegistrationCode\r\n
getEan13Code\r\n
getSimulationState\r\n
getCausalityState\r\n
getInvoiceState\r\n
getValidationState\r\n
getPaymentState\r\n
getEventState\r\n
getImmobilisationState\r\n
getReference\r\n
getGroupingReference\r\n
getGroupingDate\r\n
getSourceReference\r\n
getDestinationReference\r\n
getStringIndex\r\n
getIntIndex\r\n
getFloatIndex\r\n
hasCellContent\r\n
getCreationDate\r\n
getModificationDate</string> </value>
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
  (`uid`, `security_uid`, `owner`, `viewable_owner`, `path`, `relative_url`, `parent_uid`, `id`, `description`, `title`, `meta_type`,\n
   `portal_type`, `opportunity_state`, `corporate_registration_code`, `ean13_code`, `validation_state`, `simulation_state`,\n
   `causality_state`, `invoice_state`, `payment_state`, `event_state`, `immobilisation_state`, `reference`, `grouping_reference`, `grouping_date`,\n
   `source_reference`, `destination_reference`, `string_index`, `int_index`, `float_index`, `has_cell_content`, `creation_date`,\n
   `modification_date`)\n
VALUES\n
<dtml-in prefix="loop" expr="_.range(_.len(uid))">\n
(\n
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  \n
  <dtml-sqlvar expr="security_uid[loop_item]" type="int">,\n
  <dtml-sqlvar expr="getOwnerInfo[loop_item][\'id\']" type="string">,\n
  <dtml-sqlvar expr="(getViewPermissionOwner[loop_item] is not None) and getViewPermissionOwner[loop_item] or \'\'" type="string" optional>,\n
  <dtml-sqlvar expr="getPath[loop_item]" type="string">,\n
  <dtml-sqlvar expr="getRelativeUrl[loop_item]" type="string">,\n
  <dtml-sqlvar expr="getParentUid[loop_item]" type="int">,\n
  <dtml-sqlvar expr="id[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getDescription[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getTitle[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="meta_type[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getPortalType[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getOpportunityState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getCorporateRegistrationCode[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getEan13Code[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getValidationState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getSimulationState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getCausalityState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getInvoiceState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getPaymentState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getEventState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getImmobilisationState[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getReference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getGroupingReference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getGroupingDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getSourceReference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getDestinationReference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getStringIndex[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="getIntIndex[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getFloatIndex[loop_item]" type="float" optional>,\n
  <dtml-sqlvar expr="hasCellContent[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="getCreationDate[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="getModificationDate[loop_item]" type="datetime" optional>\n
)\n
<dtml-if sequence-end><dtml-else>,</dtml-if>\n
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

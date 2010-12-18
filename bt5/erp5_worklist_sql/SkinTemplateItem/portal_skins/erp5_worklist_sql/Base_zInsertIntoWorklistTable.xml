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
            <value> <string>count\r\n
security_uid\r\n
portal_type\r\n
simulation_state\r\n
validation_state\r\n
owner\r\n
viewable_owner\r\n
parent_uid\r\n
title\r\n
opportunity_state\r\n
causality_state\r\n
invoice_state\r\n
payment_state\r\n
event_state\r\n
immobilisation_state\r\n
reference\r\n
grouping_reference\r\n
source_reference\r\n
destination_reference\r\n
string_index\r\n
int_index\r\n
float_index\r\n
has_cell_content\r\n
creation_date\r\n
modification_date</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_zInsertIntoWorklistTable</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

INSERT INTO\n
  worklist_cache\n
  (`count`, `owner`, `viewable_owner`, `security_uid`, `portal_type`, `validation_state`, `simulation_state`, `parent_uid`, `title`,`opportunity_state`, `causality_state`, `invoice_state`, `payment_state`, `event_state`, `immobilisation_state`, `reference`, `grouping_reference`,\n
   `source_reference`, `destination_reference`, `string_index`, `int_index`, `float_index`, `has_cell_content`, `creation_date`,\n
   `modification_date`)\n
VALUES\n
<dtml-in prefix="loop" expr="_.range(_.len(count))">\n
  (\n
  <dtml-sqlvar expr="count[loop_item]" type="int">,\n
  <dtml-sqlvar expr="owner[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="viewable_owner[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="security_uid[loop_item]" type="int">,\n
  <dtml-sqlvar expr="portal_type[loop_item]" type="string">,\n
  <dtml-sqlvar expr="validation_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="simulation_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="parent_uid[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="title[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="opportunity_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="causality_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="invoice_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="payment_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="event_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="immobilisation_state[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="reference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="grouping_reference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="source_reference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="destination_reference[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="string_index[loop_item]" type="string" optional>,\n
  <dtml-sqlvar expr="int_index[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="float_index[loop_item]" type="float" optional>,\n
  <dtml-sqlvar expr="has_cell_content[loop_item]" type="int" optional>,\n
  <dtml-sqlvar expr="creation_date[loop_item]" type="datetime" optional>,\n
  <dtml-sqlvar expr="modification_date[loop_item]" type="datetime" optional>\n
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

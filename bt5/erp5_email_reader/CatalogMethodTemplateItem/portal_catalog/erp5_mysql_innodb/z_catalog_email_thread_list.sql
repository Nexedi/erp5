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
            <value> <string>uid\r\n
getPortalType\r\n
getSender\r\n
getRecipient\r\n
getCcRecipient\r\n
getBccRecipient\r\n
getStartDate\r\n
getValidationState</string> </value>
        </item>
        <item>
            <key> <string>connection_id</string> </key>
            <value> <string>erp5_sql_connection</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>z_catalog_email_thread_list</string> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<dtml-let email_list="[]">\n
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">\n
    <dtml-if expr="getPortalType[loop_item]==\'Email Thread\'">\n
      <dtml-call expr="email_list.append(loop_item)">\n
    </dtml-if>\n
  </dtml-in>\n
  <dtml-if expr="_.len(email_list) > 0">\n
    REPLACE INTO\n
      email_thread\n
    VALUES\n
      <dtml-in prefix="loop" expr="email_list">\n
      (\n
        <dtml-sqlvar expr="uid[loop_item]" type="int">,  \n
        <dtml-sqlvar expr="getSender[loop_item]" type="string" optional>,\n
        <dtml-sqlvar expr="getRecipient[loop_item]" type="string" optional>,\n
        <dtml-sqlvar expr="getCcRecipient[loop_item]" type="string" optional>,\n
        <dtml-sqlvar expr="getBccRecipient[loop_item]" type="string" optional>,\n
        <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>,\n
        <dtml-sqlvar expr="getValidationState[loop_item]" type="string" optional>\n
      )\n
      <dtml-if sequence-end><dtml-else>,</dtml-if>\n
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

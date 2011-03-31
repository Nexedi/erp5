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
getResourceUid\r\n
getInventoriatedQuantity\r\n
getBaobabSourceUid\r\n
getBaobabDestinationUid\r\n
getBaobabSourceSectionUid\r\n
getBaobabDestinationSectionUid\r\n
isMovement\r\n
isCancellationAmount\r\n
isInventoryMovement\r\n
getBaobabSourcePaymentUid\r\n
getBaobabDestinationPaymentUid\r\n
getExplanationUid\r\n
getSimulationState\r\n
getSourceInventoriatedTotalAssetPrice\r\n
getDestinationInventoriatedTotalAssetPrice\r\n
getStartDate\r\n
getStopDate\r\n
isAccountable\r\n
getPortalType\r\n
getBaobabDestinationVariationText\r\n
getBaobabSourceVariationText\r\n
getSubVariationText</string> </value>
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
            <value> <string>z_catalog_stock_list</string> </value>
        </item>
        <item>
            <key> <string>max_cache_</string> </key>
            <value> <int>100</int> </value>
        </item>
        <item>
            <key> <string>max_rows_</string> </key>
            <value> <int>0</int> </value>
        </item>
        <item>
            <key> <string>src</string> </key>
            <value> <string encoding="cdata"><![CDATA[

DELETE FROM\n
  stock\n
WHERE\n
<dtml-in uid>\n
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>\n
</dtml-in>\n
;\n
\n
<dtml-var "\'\\0\'">\n
\n
<dtml-let row_list="[]" uid_dict="{}">\n
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">\n
    <dtml-if "not isInventoryMovement[loop_item] and isMovement[loop_item] and isAccountable[loop_item] and getResourceUid[loop_item]">\n
      <dtml-if "getBaobabDestinationUid[loop_item]">\n
        <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">\n
            <dtml-call expr="row_list.append([uid[loop_item],                 uid_dict[uid[loop_item]],                 getBaobabDestinationUid[loop_item],                 getBaobabDestinationSectionUid[loop_item],                 getBaobabDestinationPaymentUid[loop_item],                 getExplanationUid[loop_item],                 getBaobabSourceSectionUid[loop_item],                 getBaobabSourceUid[loop_item],                 getResourceUid[loop_item],                 getInventoriatedQuantity[loop_item],                 isCancellationAmount[loop_item],                 getStopDate[loop_item],                 getDestinationInventoriatedTotalAssetPrice[loop_item],                 getPortalType[loop_item],                 getSimulationState[loop_item],                 getBaobabDestinationVariationText[loop_item],                 getSubVariationText[loop_item]])">\n
      </dtml-if>\n
      <dtml-if "getBaobabSourceUid[loop_item]">\n
        <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">\n
            <dtml-call expr="row_list.append([uid[loop_item],                 uid_dict[uid[loop_item]],                 getBaobabSourceUid[loop_item],                 getBaobabSourceSectionUid[loop_item],                 getBaobabSourcePaymentUid[loop_item],                 getExplanationUid[loop_item],                 getBaobabDestinationSectionUid[loop_item],                 getBaobabDestinationUid[loop_item],                 getResourceUid[loop_item],                 -(getInventoriatedQuantity[loop_item] or 0),                 isCancellationAmount[loop_item],                 getStartDate[loop_item],                 getSourceInventoriatedTotalAssetPrice[loop_item],                 getPortalType[loop_item],                 getSimulationState[loop_item],                 getBaobabSourceVariationText[loop_item],                getSubVariationText[loop_item]])">\n
      </dtml-if>\n
    </dtml-if>\n
  </dtml-in>\n
  \n
  <dtml-if "row_list">\n
INSERT INTO\n
  stock\n
VALUES\n
    <dtml-in prefix="row" expr="row_list">\n
(\n
  <dtml-sqlvar expr="row_item[0]" type="int">,\n
  <dtml-sqlvar expr="row_item[1]" type="int">,\n
  <dtml-sqlvar expr="row_item[2]" type="int">,\n
  <dtml-sqlvar expr="row_item[3]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[4]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[5]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[6]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[7]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[8]" type="int">, \n
  <dtml-sqlvar expr="row_item[9]" type="float" optional>,\n
  <dtml-sqlvar expr="row_item[10]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[11]" type="datetime" optional>,\n
  <dtml-sqlvar expr="row_item[12]" type="float" optional>,\n
  <dtml-sqlvar expr="row_item[13]" type="string" optional>,\n
  <dtml-sqlvar expr="row_item[14]" type="string" optional>,\n
  <dtml-sqlvar expr="row_item[15]" type="string" optional>,\n
  <dtml-sqlvar expr="row_item[16]" type="string" optional>\n
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

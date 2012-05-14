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
getSourceSectionUid\r\n
getDestinationSectionUid\r\n
getResourceUid\r\n
getSourceProjectUid\r\n
getDestinationProjectUid\r\n
getSourcePaymentUid\r\n
getDestinationPaymentUid\r\n
getTitle\r\n
getReference\r\n
getSourceReference\r\n
getDestinationReference\r\n
getStartDate\r\n
getStopDate\r\n
InternalInvoiceTransaction_statInternalTransactionLineList\r\n
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
            <value> <string>z_catalog_accounting_transaction_list</string> </value>
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
  accounting_transaction\n
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
    <dtml-if "getDestinationSectionUid[loop_item]">\n
      <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">\n
      <dtml-call expr="row_list.append([\n
                  uid[loop_item], \n
                  uid_dict[uid[loop_item]],\n
                  getDestinationSectionUid[loop_item],\n
                  getSourceSectionUid[loop_item],\n
                  getResourceUid[loop_item],\n
                  getDestinationProjectUid[loop_item], \n
                  getDestinationPaymentUid[loop_item],\n
                  getTitle[loop_item], \n
                  getReference[loop_item], \n
                  getDestinationReference[loop_item], \n
                  getStopDate[loop_item], \n
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0][\'destination_asset_debit\'], \n
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0][\'destination_asset_credit\'], \n
])">\n
    </dtml-if>\n
    <dtml-if expr="True">\n
      <dtml-comment>\n
      for now, unconditionanly catalog source, to always have at\n
      least one line, but is it needed ?\n
      </dtml-comment>\n
      <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">\n
      <dtml-call expr="row_list.append([\n
                  uid[loop_item], \n
                  uid_dict[uid[loop_item]],\n
                  getSourceSectionUid[loop_item],\n
                  getDestinationSectionUid[loop_item],\n
                  getResourceUid[loop_item],\n
                  getSourceProjectUid[loop_item], \n
                  getSourcePaymentUid[loop_item],\n
                  getTitle[loop_item], \n
                  getReference[loop_item], \n
                  getSourceReference[loop_item], \n
                  getStartDate[loop_item], \n
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0][\'source_asset_debit\'], \n
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0][\'source_asset_credit\'], \n
])">\n
    </dtml-if>\n
  </dtml-in>  \n
  \n
  <dtml-if "row_list">\n
INSERT INTO\n
  accounting_transaction\n
VALUES\n
    <dtml-in prefix="row" expr="row_list">\n
(\n
  <dtml-sqlvar expr="row_item[0]" type="int">,\n
  <dtml-sqlvar expr="row_item[1]" type="int">,\n
  <dtml-sqlvar expr="row_item[2]" type="int" optional>, \n
  <dtml-sqlvar expr="row_item[3]" type="int" optional>, \n
  <dtml-sqlvar expr="row_item[4]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[5]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[6]" type="int" optional>,\n
  <dtml-sqlvar expr="row_item[7]" type="string" optional>,\n
  <dtml-sqlvar expr="row_item[8]" type="string" optional>,\n
  <dtml-sqlvar expr="row_item[9]" type="string" optional>, \n
  <dtml-sqlvar expr="row_item[10]" type="datetime" optional>,\n
  <dtml-sqlvar expr="row_item[11]" type="float" optional>,\n
  <dtml-sqlvar expr="row_item[12]" type="float" optional>\n
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

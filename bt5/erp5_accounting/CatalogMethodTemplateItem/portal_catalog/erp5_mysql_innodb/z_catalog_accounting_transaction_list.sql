DELETE FROM
  accounting_transaction
WHERE
<dtml-in uid>
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>
</dtml-in>
;

<dtml-var "'\0'">

<dtml-let row_list="[]" uid_dict="{}">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "getDestinationSectionUid[loop_item]">
      <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
      <dtml-call expr="row_list.append([
                  uid[loop_item], 
                  uid_dict[uid[loop_item]],
                  getDestinationSectionUid[loop_item],
                  getSourceSectionUid[loop_item],
                  getResourceUid[loop_item],
                  getDestinationProjectUid[loop_item], 
                  getDestinationPaymentUid[loop_item],
                  getTitle[loop_item], 
                  getReference[loop_item], 
                  getDestinationReference[loop_item], 
                  getStopDate[loop_item], 
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0]['destination_asset_debit'], 
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0]['destination_asset_credit'], 
])">
    </dtml-if>
    <dtml-if expr="True">
      <dtml-comment>
      for now, unconditionanly catalog source, to always have at
      least one line, but is it needed ?
      </dtml-comment>
      <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
      <dtml-call expr="row_list.append([
                  uid[loop_item], 
                  uid_dict[uid[loop_item]],
                  getSourceSectionUid[loop_item],
                  getDestinationSectionUid[loop_item],
                  getResourceUid[loop_item],
                  getSourceProjectUid[loop_item], 
                  getSourcePaymentUid[loop_item],
                  getTitle[loop_item], 
                  getReference[loop_item], 
                  getSourceReference[loop_item], 
                  getStartDate[loop_item], 
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0]['source_asset_debit'], 
                  InternalInvoiceTransaction_statInternalTransactionLineList[loop_item][0]['source_asset_credit'], 
])">
    </dtml-if>
  </dtml-in>  
  
  <dtml-if "row_list">
INSERT INTO
  accounting_transaction
VALUES
    <dtml-in prefix="row" expr="row_list">
(
  <dtml-sqlvar expr="row_item[0]" type="int">,
  <dtml-sqlvar expr="row_item[1]" type="int">,
  <dtml-sqlvar expr="row_item[2]" type="int" optional>, 
  <dtml-sqlvar expr="row_item[3]" type="int" optional>, 
  <dtml-sqlvar expr="row_item[4]" type="int" optional>,
  <dtml-sqlvar expr="row_item[5]" type="int" optional>,
  <dtml-sqlvar expr="row_item[6]" type="int" optional>,
  <dtml-sqlvar expr="row_item[7]" type="string" optional>,
  <dtml-sqlvar expr="row_item[8]" type="string" optional>,
  <dtml-sqlvar expr="row_item[9]" type="string" optional>, 
  <dtml-sqlvar expr="row_item[10]" type="datetime" optional>,
  <dtml-sqlvar expr="row_item[11]" type="float" optional>,
  <dtml-sqlvar expr="row_item[12]" type="float" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

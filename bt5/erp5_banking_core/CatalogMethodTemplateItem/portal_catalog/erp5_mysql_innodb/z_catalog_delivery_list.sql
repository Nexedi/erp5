<dtml-let delivery_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
      <dtml-call expr="delivery_list.append(loop_item)">
  </dtml-in>
  <dtml-if expr="_.len(delivery_list) > 0">
REPLACE INTO
  delivery
VALUES
    <dtml-in prefix="loop" expr="delivery_list">
( 
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getSourceUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getDestinationUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getSourceSectionUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getDestinationSectionUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getResourceUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getRecoupDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getSourcePaymentReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDestinationPaymentReference[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSourcePaymentInternalBankAccountNumber[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getDestinationPaymentInternalBankAccountNumber[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSourceTotalAssetPrice[loop_item]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

<dtml-let row_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "not(isInventoryMovement[loop_item]) and isMovement[loop_item] and getResourceUid[loop_item]">
      <dtml-if "getDestinationUid[loop_item]">
        <dtml-call expr="row_list.append([
                    uid[loop_item], 
                    order_id[loop_item],
                    getExplanationUid[loop_item],
                    getDestinationUid[loop_item],
                    getDestinationSectionUid[loop_item],
                    getDestinationPaymentUid[loop_item],
                    getDestinationFunctionUid[loop_item],
                    getDestinationProjectUid[loop_item], 
                    getDestinationFundingUid[loop_item], 
                    getLedgerUid[loop_item],
                    getDestinationPaymentRequestUid[loop_item], 
                    getSourceSectionUid[loop_item], 
                    getSourceUid[loop_item], 
                    getResourceUid[loop_item],
                    getInventoriatedQuantity[loop_item],
                    isCancellationAmount[loop_item],
                    isAccountable[loop_item],
                    getStopDate[loop_item], 
                    getStartDate[loop_item], 
                    getDestinationInventoriatedTotalAssetPrice[loop_item], 
                    getPortalType[loop_item], 
                    getSimulationState[loop_item], 
                    getVariationText[loop_item],
                    getSubVariationText[loop_item]])">
      </dtml-if>
      <dtml-if "getSourceUid[loop_item]">
        <dtml-call expr="row_list.append([
                    uid[loop_item], 
                    mirror_order_id[loop_item],
                    getExplanationUid[loop_item],
                    getSourceUid[loop_item],
                    getSourceSectionUid[loop_item],
                    getSourcePaymentUid[loop_item],
                    getSourceFunctionUid[loop_item],
                    getSourceProjectUid[loop_item], 
                    getSourceFundingUid[loop_item], 
                    getLedgerUid[loop_item],
                    getSourcePaymentRequestUid[loop_item], 
                    getDestinationSectionUid[loop_item], 
                    getDestinationUid[loop_item], 
                    getResourceUid[loop_item],
                    -(getInventoriatedQuantity[loop_item] or 0), 
                    isCancellationAmount[loop_item],
                    isAccountable[loop_item],
                    getStartDate[loop_item], 
                    getStopDate[loop_item],
                    getSourceInventoriatedTotalAssetPrice[loop_item], 
                    getPortalType[loop_item], 
                    getSimulationState[loop_item], 
                    getVariationText[loop_item],
                    getSubVariationText[loop_item]])">
      </dtml-if>
    </dtml-if>
  </dtml-in>  
  <dtml-if "row_list">
INSERT INTO
  stock
VALUES
    <dtml-in prefix="row" expr="row_list">
(
  <dtml-sqlvar expr="row_item[0]" type="int">,
  <dtml-sqlvar expr="row_item[1]" type="int">,
  <dtml-sqlvar expr="row_item[2]" type="int" optional>,
  <dtml-sqlvar expr="row_item[3]" type="int">,
  <dtml-sqlvar expr="row_item[4]" type="int" optional>, 
  <dtml-sqlvar expr="row_item[5]" type="int" optional>, 
  <dtml-sqlvar expr="row_item[6]" type="int" optional>,
  <dtml-sqlvar expr="row_item[7]" type="int" optional>,
  <dtml-sqlvar expr="row_item[8]" type="int" optional>,
  <dtml-sqlvar expr="row_item[9]" type="int" optional>,
  <dtml-sqlvar expr="row_item[10]" type="int" optional>,
  <dtml-sqlvar expr="row_item[11]" type="int" optional>,
  <dtml-sqlvar expr="row_item[12]" type="int" optional>,
  <dtml-sqlvar expr="row_item[13]" type="int">, 
  <dtml-sqlvar expr="row_item[14]" type="float" optional>,
  <dtml-sqlvar expr="row_item[15]" type="int">, 
  <dtml-sqlvar expr="row_item[16]" type="int">,
  <dtml-sqlvar expr="row_item[17]" type="datetime" optional>,
  <dtml-sqlvar expr="row_item[18]" type="datetime" optional>,
  <dtml-sqlvar expr="row_item[19]" type="float" optional>,
  <dtml-sqlvar expr="row_item[20]" type="string" optional>,
  <dtml-sqlvar expr="row_item[21]" type="string" optional>,
  <dtml-sqlvar expr="row_item[22]" type="string" optional>,
  <dtml-sqlvar expr="row_item[23]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

DELETE FROM
  stock
WHERE
<dtml-in uid>
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>
</dtml-in>
;

<dtml-var "'\0'">

<dtml-let row_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "isMovement[loop_item]">
      <dtml-if "isAccountable[loop_item]">
        <dtml-if "getResourceUid[loop_item]">
          <dtml-if "getDestinationUid[loop_item]">
            <dtml-call expr="row_list.append([uid[loop_item], getDestinationUid[loop_item], getDestinationSectionUid[loop_item], getDestinationPaymentUid[loop_item], getDestinationFunctionUid[loop_item], getDestinationProjectUid[loop_item], getSourceSectionUid[loop_item], getSourceUid[loop_item], getResourceUid[loop_item], getInventoriatedQuantity[loop_item], getStopDate[loop_item], getDestinationInventoriatedTotalAssetPrice[loop_item], getPortalType[loop_item], getSimulationState[loop_item], getVariationText[loop_item],getSubVariationText[loop_item]])">
          </dtml-if>
          <dtml-if "getSourceUid[loop_item]">
            <dtml-call expr="row_list.append([uid[loop_item], getSourceUid[loop_item], getSourceSectionUid[loop_item], getSourcePaymentUid[loop_item], getSourceFunctionUid[loop_item], getSourceProjectUid[loop_item], getDestinationSectionUid[loop_item], getDestinationUid[loop_item], getResourceUid[loop_item], -(getInventoriatedQuantity[loop_item] or 0), getStartDate[loop_item], getSourceInventoriatedTotalAssetPrice[loop_item], getPortalType[loop_item], getSimulationState[loop_item], getVariationText[loop_item], getSubVariationText[loop_item]])">
          </dtml-if>
        </dtml-if>
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
  <dtml-sqlvar expr="row_item[3]" type="int" optional>, 
  <dtml-sqlvar expr="row_item[4]" type="int" optional>,
  <dtml-sqlvar expr="row_item[5]" type="int" optional>,
  <dtml-sqlvar expr="row_item[6]" type="int" optional>,
  <dtml-sqlvar expr="row_item[7]" type="int" optional>,
  <dtml-sqlvar expr="row_item[8]" type="int">, 
  <dtml-sqlvar expr="row_item[9]" type="float" optional>,
  <dtml-sqlvar expr="row_item[10]" type="datetime" optional>,
  <dtml-sqlvar expr="row_item[11]" type="float" optional>,
  <dtml-sqlvar expr="row_item[12]" type="string" optional>,
  <dtml-sqlvar expr="row_item[13]" type="string" optional>,
  <dtml-sqlvar expr="row_item[14]" type="string" optional>,
  <dtml-sqlvar expr="row_item[15]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

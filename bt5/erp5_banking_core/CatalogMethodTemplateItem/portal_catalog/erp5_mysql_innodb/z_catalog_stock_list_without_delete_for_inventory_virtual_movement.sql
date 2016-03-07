DELETE FROM
  stock
WHERE
<dtml-in uid>
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>
</dtml-in>
;

<dtml-var "'\0'">

<dtml-let row_list="[]" uid_dict="{}">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "not isInventoryMovement[loop_item] and isMovement[loop_item] and isAccountable[loop_item] and getResourceUid[loop_item]">
      <dtml-if "getBaobabDestinationUid[loop_item]">
        <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
            <dtml-call expr="row_list.append([uid[loop_item],                 uid_dict[uid[loop_item]],                 getBaobabDestinationUid[loop_item],                 getBaobabDestinationSectionUid[loop_item],                 getBaobabDestinationPaymentUid[loop_item],                 getExplanationUid[loop_item],                 getBaobabSourceSectionUid[loop_item],                 getBaobabSourceUid[loop_item],                 getResourceUid[loop_item],                 getInventoriatedQuantity[loop_item],                 isCancellationAmount[loop_item],                 getStopDate[loop_item],                 getDestinationInventoriatedTotalAssetPrice[loop_item],                 getPortalType[loop_item],                 getSimulationState[loop_item],                 getBaobabDestinationVariationText[loop_item],                 getSubVariationText[loop_item]])">
      </dtml-if>
      <dtml-if "getBaobabSourceUid[loop_item]">
        <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
            <dtml-call expr="row_list.append([uid[loop_item],                 uid_dict[uid[loop_item]],                 getBaobabSourceUid[loop_item],                 getBaobabSourceSectionUid[loop_item],                 getBaobabSourcePaymentUid[loop_item],                 getExplanationUid[loop_item],                 getBaobabDestinationSectionUid[loop_item],                 getBaobabDestinationUid[loop_item],                 getResourceUid[loop_item],                 -(getInventoriatedQuantity[loop_item] or 0),                 isCancellationAmount[loop_item],                 getStartDate[loop_item],                 getSourceInventoriatedTotalAssetPrice[loop_item],                 getPortalType[loop_item],                 getSimulationState[loop_item],                 getBaobabSourceVariationText[loop_item],                getSubVariationText[loop_item]])">
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
  <dtml-sqlvar expr="row_item[2]" type="int">,
  <dtml-sqlvar expr="row_item[3]" type="int" optional>,
  <dtml-sqlvar expr="row_item[4]" type="int" optional>,
  <dtml-sqlvar expr="row_item[5]" type="int" optional>,
  <dtml-sqlvar expr="row_item[6]" type="int" optional>,
  <dtml-sqlvar expr="row_item[7]" type="int" optional>,
  <dtml-sqlvar expr="row_item[8]" type="int">, 
  <dtml-sqlvar expr="row_item[9]" type="float" optional>,
  <dtml-sqlvar expr="row_item[10]" type="int" optional>,
  <dtml-sqlvar expr="row_item[11]" type="datetime" optional>,
  <dtml-sqlvar expr="row_item[12]" type="float" optional>,
  <dtml-sqlvar expr="row_item[13]" type="string" optional>,
  <dtml-sqlvar expr="row_item[14]" type="string" optional>,
  <dtml-sqlvar expr="row_item[15]" type="string" optional>,
  <dtml-sqlvar expr="row_item[16]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

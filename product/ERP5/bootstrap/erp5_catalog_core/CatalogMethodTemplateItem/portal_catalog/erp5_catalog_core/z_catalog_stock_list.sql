DELETE FROM
  stock
WHERE
<dtml-sqltest uid type="int" multiple>

<dtml-var sql_delimiter>

<dtml-let row_list="[]" uid_dict="{}">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "not(isInventoryMovement[loop_item]) and isMovement[loop_item] and getResourceUid[loop_item]">
      <dtml-in prefix="movement" expr="asMovementList[loop_item]" no_push_item>
        <dtml-let movement_item_quantity="movement_item.getInventoriatedQuantity() or 0">
        <dtml-if "getDestinationUid[loop_item]">
          <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
          <dtml-call expr="row_list.append([
                      uid[loop_item],
                      uid_dict[uid[loop_item]],
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
                      movement_item_quantity,
                      isCancellationAmount[loop_item],
                      isAccountable[loop_item],
                      movement_item.getStopDate(),
                      movement_item.getStartDate(),
                      getDestinationInventoriatedTotalAssetPrice[loop_item],
                      getPortalType[loop_item],
                      getSimulationState[loop_item],
                      getVariationText[loop_item],
                      getSubVariationText[loop_item],
                      0,
          ])">
        </dtml-if>
        <dtml-if "getSourceUid[loop_item]">
          <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
          <dtml-call expr="row_list.append([
                      uid[loop_item],
                      uid_dict[uid[loop_item]],
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
                      -movement_item_quantity,
                      isCancellationAmount[loop_item],
                      isAccountable[loop_item],
                      movement_item.getStartDate(),
                      movement_item.getStopDate(),
                      getSourceInventoriatedTotalAssetPrice[loop_item],
                      getPortalType[loop_item],
                      getSimulationState[loop_item],
                      getVariationText[loop_item],
                      getSubVariationText[loop_item],
                      1,
          ])">
        </dtml-if>
        </dtml-let>
      </dtml-in>
    </dtml-if>
  </dtml-in>

  <dtml-if "row_list">
INSERT INTO
  stock
(
  `uid`,
  `order_id`,
  `explanation_uid`,
  `node_uid`,
  `section_uid`,
  `payment_uid`,
  `function_uid`,
  `project_uid`,
  `funding_uid`,
  `ledger_uid`,
  `payment_request_uid`,
  `mirror_section_uid`,
  `mirror_node_uid`,
  `resource_uid`,
  `quantity`,
  `is_cancellation`,
  `is_accountable`,
  `date`,
  `mirror_date`,
  `total_price`,
  `portal_type`,
  `simulation_state`,
  `variation_text`,
  `sub_variation_text`,
  `is_source`
)
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
  <dtml-sqlvar expr="row_item[23]" type="string" optional>,
  <dtml-sqlvar expr="row_item[24]" type="int">
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

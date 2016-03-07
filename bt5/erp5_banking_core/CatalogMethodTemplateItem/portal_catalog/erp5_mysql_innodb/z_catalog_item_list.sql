DELETE FROM
  item
WHERE
<dtml-in uid>
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>
</dtml-in>
;

<dtml-var "'\0'">

<dtml-let movement_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "isMovement[loop_item] and isAccountable[loop_item] and getAggregateUidList[loop_item]">
      <dtml-call expr="movement_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(movement_list) > 0">
INSERT INTO
  item
VALUES
    <dtml-in prefix="loop" expr="movement_list">
      <dtml-in "getAggregateUidList[loop_item]">
( 
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getStopDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getBaobabDestinationUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getBaobabDestinationSectionUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getResourceUid[loop_item]" type="int" optional>,
  <dtml-sqlvar sequence-item type="int" optional>,
  <dtml-sqlvar expr="getVariationText[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSimulationState[loop_item]" type="string" optional>
)
        <dtml-if sequence-end><dtml-else>,</dtml-if>
      </dtml-in>
      <dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>


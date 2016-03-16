<dtml-let movement_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "isMovement[loop_item]">
      <dtml-call expr="movement_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(movement_list) > 0">
REPLACE INTO
  movement
VALUES
    <dtml-in prefix="loop" expr="movement_list">
( 
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getExplanationUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getSourceUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getDestinationUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getResourceUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getInventoriatedQuantity[loop_item]" type="float" optional>,
  <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStopDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getPrice[loop_item]" type="float" optional>,
  <dtml-sqlvar expr="isAccountable[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="isOrderable[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="isDeliverable[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="isDivergent[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getVariationText[loop_item]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

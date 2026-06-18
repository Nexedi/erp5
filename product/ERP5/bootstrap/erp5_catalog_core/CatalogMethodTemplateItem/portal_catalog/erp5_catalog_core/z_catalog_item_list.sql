DELETE FROM
  item
WHERE
<dtml-sqltest uid type="int" multiple>

<dtml-var sql_delimiter>

<dtml-let movement_list="[]" uid_dict="{}">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "isMovement[loop_item] and isAccountable[loop_item] and getMovedItemUidList[loop_item]">
      <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
      <dtml-call expr="movement_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(movement_list) > 0">
INSERT INTO
  item
VALUES
    <dtml-in prefix="loop" expr="movement_list">
      <dtml-in expr="getMovedItemUidList[loop_item]">

(  
  <dtml-call expr="uid_dict.update({uid[loop_item]: uid_dict.get(uid[loop_item], -1) + 1})">
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="uid_dict[uid[loop_item]]" type="int">,
  <dtml-sqlvar expr="getStopDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getDestinationUid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getDestinationSectionUid[loop_item]" type="int" optional>,
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
<dtml-let delivery_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "isDelivery[loop_item]">
      <dtml-call expr="delivery_list.append(loop_item)">
    </dtml-if>
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
  <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStartDateRangeMin[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStartDateRangeMax[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStopDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStopDateRangeMin[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getStopDateRangeMax[loop_item]" type="datetime" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

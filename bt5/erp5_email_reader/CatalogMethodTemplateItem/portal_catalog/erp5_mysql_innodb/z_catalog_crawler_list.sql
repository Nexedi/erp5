REPLACE INTO
  crawler
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="getFrequencyIndex[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getCreationDateIndex[loop_item]" type="int" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>

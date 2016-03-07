<dtml-if expr="_.len(_.range(_.len(uid))) > 0">
REPLACE INTO
  birth_detail
VALUES
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
( 
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getBirthplaceAddressCity[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getStartDate[loop_item]" type="datetime" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
  </dtml-in>
</dtml-if>

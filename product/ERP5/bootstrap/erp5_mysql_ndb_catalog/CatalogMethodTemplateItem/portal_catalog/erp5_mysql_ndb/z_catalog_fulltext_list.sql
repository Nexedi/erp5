REPLACE INTO
  full_text
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="SearchableText[loop_item]" type="string" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>

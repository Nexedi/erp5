REPLACE INTO
  reporting_outcome
  (`uid`, `outcome_description`)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="getOutcomeDescription[loop_item]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>

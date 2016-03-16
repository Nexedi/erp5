REPLACE INTO
  compatibility
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,  
  <dtml-sqlvar expr="Creator[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="Date[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="PrincipiaSearchSource[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="SearchableText[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="CreationDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="EffectiveDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="ExpiresDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="ModificationDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="Type[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="bobobase_modification_time[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="created[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="effective[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="expires[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getIcon[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="in_reply_to[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="modified[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="review_state[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="summary[loop_item]" type="string" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>

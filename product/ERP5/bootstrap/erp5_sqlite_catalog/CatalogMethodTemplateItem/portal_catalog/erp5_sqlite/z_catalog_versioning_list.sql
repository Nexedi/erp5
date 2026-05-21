REPLACE INTO
  versioning
  (`uid`, `version`, `size`, `language`, `revision`, `subject_set_uid`, `effective_date`,
   `expiration_date`, `creation_date_index`, `frequency_index`)
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getVersion[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getSize[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getLanguage[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="getRevision[loop_item]" type="string" optional>,
  <dtml-sqlvar expr="subject_set_uid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getEffectiveDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getExpirationDate[loop_item]" type="datetime" optional>,
  <dtml-sqlvar expr="getCreationDateIndex[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="getFrequencyIndex[loop_item]" type="int" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>

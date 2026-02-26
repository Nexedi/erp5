<dtml-let document_list="[]" delete_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "SearchableText[loop_item]">
      <dtml-call expr="document_list.append(loop_item)">
    <dtml-else>
      <dtml-call expr="delete_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(document_list) > 0">
REPLACE INTO
  full_text
VALUES
    <dtml-in prefix="loop" expr="document_list">
( 
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="SearchableText[loop_item]" type="string" optional>
)<dtml-unless sequence-end>,</dtml-unless>
    </dtml-in>
  </dtml-if>
  <dtml-if expr="_.len(delete_list) > 0">
<dtml-var sql_delimiter>
DELETE FROM
  full_text
WHERE uid IN
( 
    <dtml-in prefix="loop" expr="delete_list">
  <dtml-sqlvar expr="uid[loop_item]" type="int"><dtml-unless sequence-end>,</dtml-unless>
    </dtml-in>
)
  </dtml-if>
</dtml-let>

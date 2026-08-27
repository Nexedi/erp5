<dtml-let document_list="[]" delete_list="[]" column_list="['SearchableText']">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "SearchableText[loop_item]">
      <dtml-call expr="document_list.append(loop_item)">
    <dtml-else>
      <dtml-call expr="delete_list.append(loop_item)">
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(document_list) > 0">
INSERT INTO
  full_text (`uid`, <dtml-in column_list>`<dtml-var sequence-item>`<dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
VALUES
    <dtml-in prefix="loop" expr="document_list">
( 
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="SearchableText[loop_item]" type="string" optional>
)<dtml-unless sequence-end>,</dtml-unless>
    </dtml-in>
ON DUPLICATE KEY UPDATE
    <dtml-in column_list>
  `<dtml-var sequence-item>` = VALUES(`<dtml-var sequence-item>`)<dtml-if sequence-end><dtml-else>,</dtml-if>
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

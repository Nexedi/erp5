INSERT IGNORE INTO search_rank VALUES
    <dtml-in prefix="loop" expr="uid">
      <dtml-if sequence-start><dtml-else>,</dtml-if>
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">
)
    </dtml-in>

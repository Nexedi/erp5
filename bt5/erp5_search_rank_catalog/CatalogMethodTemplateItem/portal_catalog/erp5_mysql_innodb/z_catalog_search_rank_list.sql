REPLACE INTO search_rank (`uid`) VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
  (
    <dtml-sqlvar expr="uid[loop_item]" type="int">
  )
  <dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>

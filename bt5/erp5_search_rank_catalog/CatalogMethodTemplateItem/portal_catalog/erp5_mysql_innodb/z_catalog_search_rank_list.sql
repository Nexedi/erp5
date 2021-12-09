INSERT INTO search_rank (uid) VALUES
    <dtml-in prefix="loop" expr="_.range(_.len(uid))">
      <dtml-if sequence-start><dtml-else>,</dtml-if>
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">
)
    </dtml-in>
  ON DUPLICATE KEY UPDATE uid=VALUES(uid);
REPLACE INTO `user` (`uid`, `user_id`) VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
<dtml-sqlvar expr="uid[loop_item]" type="int">,
<dtml-sqlvar expr="getUserId[loop_item]" type="string" optional>
)
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>

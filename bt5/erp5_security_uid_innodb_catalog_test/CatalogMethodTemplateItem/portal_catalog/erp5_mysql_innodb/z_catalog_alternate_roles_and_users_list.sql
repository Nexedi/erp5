REPLACE INTO alternate_roles_and_users
(`uid`, `alternate_security_uid`, `other_security_uid` )
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
( <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="alternate_security_uid[loop_item]" type="int" optional>,
  <dtml-sqlvar expr="other_security_uid[loop_item]" type="int" optional>
)<dtml-unless sequence-end>,</dtml-unless>
</dtml-in>
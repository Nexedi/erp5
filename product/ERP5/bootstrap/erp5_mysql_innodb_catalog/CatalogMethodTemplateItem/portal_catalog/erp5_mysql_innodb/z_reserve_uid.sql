REPLACE INTO
  catalog (uid, id, path)
VALUES
<dtml-in uid>
  (<dtml-sqlvar sequence-item type="int">, 'used', 'reserved')
<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
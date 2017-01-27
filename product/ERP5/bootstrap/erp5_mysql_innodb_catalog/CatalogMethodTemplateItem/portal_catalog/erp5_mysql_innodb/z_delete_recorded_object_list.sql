<dtml-comment>Do not delete rows really, but just mark them as "played" to avoid dead locks</dtml-comment>
UPDATE
  record
SET
  played = 1
WHERE
<dtml-in uid_list>
  uid = <dtml-sqlvar sequence-item type="string"><dtml-if sequence-end><dtml-else> OR </dtml-if>
</dtml-in>

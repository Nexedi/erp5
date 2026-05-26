select cast(id_group as CHAR) id_group, last_id from portal_ids
  <dtml-if id_group>where id_group > <dtml-sqlvar id_group type="string"></dtml-if>
  order by id_group
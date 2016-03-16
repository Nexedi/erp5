select id_group, last_id from portal_ids 
  <dtml-if id_group>where id_group > "<dtml-var id_group>"</dtml-if>
  order by id_group
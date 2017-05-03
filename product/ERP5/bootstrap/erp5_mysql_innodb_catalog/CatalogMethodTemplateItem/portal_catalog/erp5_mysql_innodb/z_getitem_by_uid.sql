SELECT <dtml-if path_only>path<dtml-else>uid,path</dtml-if> from catalog 
WHERE 
<dtml-if uid_list>
  uid IN (<dtml-in uid_list><dtml-sqlvar sequence-item type="int">
          <dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
  LIMIT <dtml-sqlvar expr="len(uid_list)" type="int">
<dtml-else>
  <dtml-sqltest uid op=eq type="int">
  LIMIT 1
</dtml-if>

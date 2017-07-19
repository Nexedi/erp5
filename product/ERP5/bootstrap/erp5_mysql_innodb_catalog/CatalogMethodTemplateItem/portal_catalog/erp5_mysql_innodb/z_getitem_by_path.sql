SELECT <dtml-if uid_only>uid<dtml-else>uid,path</dtml-if> from catalog 
WHERE 
<dtml-if path_list>
  path IN (<dtml-in path_list><dtml-sqlvar sequence-item type="string">
           <dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
  LIMIT <dtml-sqlvar expr="len(path_list)" type="int">
<dtml-else>
  <dtml-sqltest path op=eq type="string">
  LIMIT 1
</dtml-if>

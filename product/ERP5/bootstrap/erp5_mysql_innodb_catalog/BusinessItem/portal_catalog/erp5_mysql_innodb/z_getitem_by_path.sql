SELECT <dtml-if uid_only>uid<dtml-else>uid,path</dtml-if> from catalog 
WHERE 
  1 = 1
<dtml-if path>
  AND <dtml-sqltest path op=eq type="string">
</dtml-if>
<dtml-if path_list>
  AND path IN (<dtml-in path_list><dtml-sqlvar sequence-item type="string">
               <dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
</dtml-if>

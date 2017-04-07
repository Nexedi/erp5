SELECT <dtml-if path_only>path<dtml-else>uid,path</dtml-if> from catalog 
WHERE 
  1 = 1
<dtml-if expr="uid is not None">
  AND <dtml-sqltest uid op=eq type="int">
</dtml-if>
<dtml-if uid_list>
  AND uid IN (<dtml-in uid_list><dtml-sqlvar sequence-item type="int">
               <dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
</dtml-if>

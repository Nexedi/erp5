SELECT <dtml-if path_only>path<dtml-else>uid,path</dtml-if> from catalog 
WHERE 
<<<<<<< HEAD
<dtml-if uid_list>
  uid IN (<dtml-in uid_list><dtml-sqlvar sequence-item type="int">
          <dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
  LIMIT <dtml-sqlvar expr="len(uid_list)" type="int">
<dtml-else>
  <dtml-sqltest uid op=eq type="int">
  LIMIT 1
=======
  1 = 1
<dtml-if expr="uid is not None">
  AND <dtml-sqltest uid op=eq type="int">
</dtml-if>
<dtml-if uid_list>
  AND uid IN (<dtml-in uid_list><dtml-sqlvar sequence-item type="int">
               <dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
>>>>>>> 3ce2fc0... bt5_prototype: Move erp5_mysql_innodb_catalog back to BT5 type
</dtml-if>

DELETE FROM
  category
WHERE
<<<<<<< HEAD
<dtml-sqltest uid type="int" multiple>

<dtml-var sql_delimiter>

=======
<dtml-in uid>
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>
</dtml-in>
;
<dtml-var "'\0'">
>>>>>>> 3ce2fc0... bt5_prototype: Move erp5_mysql_innodb_catalog back to BT5 type
<dtml-let category_list="[]" getCategoryParentUidList="portal_categories.getCategoryParentUidList">
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
<dtml-if expr="getAcquiredCategoryList[loop_item]">
<dtml-let uid_list="getCategoryParentUidList(getAcquiredCategoryList[loop_item])">
<dtml-if uid_list>
<dtml-in prefix="uid" expr="uid_list">
<dtml-call expr="category_list.append((uid[loop_item], uid_item[0], uid_item[1], uid_item[2]))">
</dtml-in></dtml-if></dtml-let></dtml-if></dtml-in>  
<dtml-if expr="category_list">
<<<<<<< HEAD
INSERT INTO category VALUES
=======
REPLACE INTO category VALUES
>>>>>>> 3ce2fc0... bt5_prototype: Move erp5_mysql_innodb_catalog back to BT5 type
<dtml-in prefix="loop" expr="category_list">
(<dtml-sqlvar expr="loop_item[0]" type="int">, <dtml-sqlvar expr="loop_item[1]" type="int">, <dtml-sqlvar expr="loop_item[2]" type="int">, <dtml-sqlvar expr="loop_item[3]" type="int">)<dtml-if sequence-end><dtml-else>,</dtml-if>
</dtml-in>
</dtml-if>
</dtml-let>
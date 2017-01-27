DELETE FROM
  predicate_category
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

<dtml-let predicate_list="[]">
  <dtml-in prefix="loop" expr="_.range(_.len(uid))">
    <dtml-if "isPredicate[loop_item]">
      <dtml-if expr="_.len(predicate_property_dict[loop_item]) > 0">
        <dtml-call expr="predicate_list.append(loop_item)">
      </dtml-if>
    </dtml-if>
  </dtml-in>
  <dtml-if expr="_.len(predicate_list) > 0">
<<<<<<< HEAD
INSERT INTO predicate_category VALUES
=======
REPLACE INTO predicate_category VALUES 
>>>>>>> 3ce2fc0... bt5_prototype: Move erp5_mysql_innodb_catalog back to BT5 type
    <dtml-in prefix="loop" expr="predicate_list">
      <dtml-if sequence-start><dtml-else>,</dtml-if>
      <dtml-if "predicate_property_dict[loop_item].has_key('membership_criterion_category_list')">
        <dtml-let uid_list="portal_categories.CategoryTool_getPreferredPredicateCategoryParentUidItemList(predicate_property_dict[loop_item]['membership_criterion_category_list'], getObject[loop_item])">
          <dtml-if uid_list>
            <dtml-in "uid_list">
(<dtml-sqlvar expr="uid[loop_item]" type="int">, <dtml-var "_['sequence-item'][0]" >, <dtml-var "_['sequence-item'][1]" >, <dtml-var "_['sequence-item'][2]" >)
              <dtml-if sequence-end><dtml-else>,</dtml-if>
            </dtml-in> 
          <dtml-else>
(<dtml-sqlvar expr="uid[loop_item]" type="int">, 0, 0,1)
          </dtml-if>
        </dtml-let>
      <dtml-else>
(<dtml-sqlvar expr="uid[loop_item]" type="int">, 0, 0,1)
      </dtml-if>
    </dtml-in>
  </dtml-if>
</dtml-let>

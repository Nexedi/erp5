DELETE FROM
  category
WHERE
<dtml-in uid>
  uid=<dtml-sqlvar sequence-item type="int"><dtml-if sequence-end><dtml-else> OR </dtml-if>
</dtml-in>
;

<dtml-var "'\0'">

INSERT INTO category VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
<dtml-if sequence-start><dtml-else>,</dtml-if>
    <dtml-if expr="getAcquiredCategoryList[loop_item]">
      <dtml-let uid_list="portal_categories.getCategoryParentUidList(getAcquiredCategoryList[loop_item])">
        <dtml-if uid_list>
          <dtml-in prefix="uid" expr="uid_list">
<dtml-if sequence-start><dtml-else>,</dtml-if>
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="uid_item[0]" type="int">,
  <dtml-sqlvar expr="uid_item[1]" type="int">,
  <dtml-sqlvar expr="uid_item[2]" type="int">
)
          </dtml-in> 
        <dtml-else>
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  NULL,
  NULL,
  1
)
        </dtml-if>
      </dtml-let>
    <dtml-else>
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  NULL,
  NULL,
  1
)
    </dtml-if>
</dtml-in>  

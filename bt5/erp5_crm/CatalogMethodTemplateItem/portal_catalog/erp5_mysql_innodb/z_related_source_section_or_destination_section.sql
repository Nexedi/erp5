<dtml-comment>
table_0 : category as source_section or destination_section
table_1 : catalog as category
table_2 : catalog as object_uid
</dtml-comment>

( 
  <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.source_section.getUid()">
  OR 
  <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.destination_section.getUid()">
)
AND
<dtml-var table_0>.category_uid = <dtml-var table_2>.uid AND
<dtml-var table_0>.uid = <dtml-var table_1>.uid AND
<dtml-var table_1>.uid = catalog.uid

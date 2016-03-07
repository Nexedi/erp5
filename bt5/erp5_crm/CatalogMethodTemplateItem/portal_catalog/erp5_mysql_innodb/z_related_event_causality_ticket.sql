<dtml-var table_3>.uid = <dtml-var table_2>.category_uid
AND <dtml-var table_1>.uid = <dtml-var table_2>.uid
AND <dtml-var table_1>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.causality.getUid()">
AND catalog.uid = <dtml-var table_0>.uid
AND (<dtml-in "portal_catalog.getPortalEventTypeList()">
  <dtml-if sequence-start>
    <dtml-var table_1>.portal_type = '<dtml-var sequence-item>'
  <dtml-else>
    OR <dtml-var table_1>.portal_type = '<dtml-var sequence-item>'
  </dtml-if>
</dtml-in>)
AND
  (SELECT count(*) from category as sub_category
    WHERE sub_category.uid = catalog.uid
    AND sub_category.base_category_uid = <dtml-var "portal_categories.follow_up.getUid()">
    AND sub_category.category_uid = <dtml-var table_3>.uid
    LIMIT 1 ) = 0

<dtml-comment>
table_0 category as resource
table_1 category as use
</dtml-comment>
catalog.uid = <dtml-var table_0>.uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.resource.getUid()">
AND <dtml-var table_0>.category_uid = <dtml-var table_1>.uid
AND <dtml-var table_1>.base_category_uid = <dtml-var "portal_categories.use.getUid()">
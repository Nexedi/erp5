<dtml-var table_0>.uid = catalog.uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.resource.getUid()">
AND <dtml-var table_0>.category_uid=<dtml-var table_2>.uid
AND <dtml-var table_1>.uid = <dtml-var table_2>.uid
AND <dtml-var table_1>.base_category_uid = <dtml-var "portal_categories.use.getUid()">
AND <dtml-var table_1>.category_uid = <dtml-var table_3>.uid
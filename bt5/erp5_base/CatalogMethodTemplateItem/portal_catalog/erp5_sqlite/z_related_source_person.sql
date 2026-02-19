<dtml-var table_1>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.source.getUid()">
AND <dtml-var table_0>.uid = catalog.uid
AND <dtml-var table_1>.portal_type = 'Person'


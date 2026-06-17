<dtml-var table_2>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.skill.getUid()">
AND <dtml-var table_0>.uid = <dtml-var table_1>.uid
AND <dtml-var table_1>.parent_uid = catalog.uid
AND <dtml-var table_1>.portal_type = 'Career'


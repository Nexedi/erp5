<dtml-var table_0>.uid = catalog.uid
 AND <dtml-var table_0>.explanation_uid = <dtml-var table_1>.uid
 AND <dtml-var table_1>.base_category_uid = <dtml-var "portal_categories.destination_section.getUid()">
 AND <dtml-var table_1>.category_uid = <dtml-var table_2>.uid

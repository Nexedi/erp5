<dtml-var table_1>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.payment_mode.getUid()">
AND <dtml-var table_0>.uid in (<dtml-var query_table>.uid, <dtml-var query_table>.parent_uid)


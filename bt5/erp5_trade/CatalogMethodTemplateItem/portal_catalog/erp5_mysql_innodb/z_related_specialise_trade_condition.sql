<dtml-var table_1>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.specialise.getUid()">
AND <dtml-var table_1>.portal_type = 'Sale Trade Condition'
<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_0>.uid = <dtml-var query_table>.uid
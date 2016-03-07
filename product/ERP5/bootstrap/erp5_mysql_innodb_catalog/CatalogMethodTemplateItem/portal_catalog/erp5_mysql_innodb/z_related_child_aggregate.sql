<dtml-var table_0>.uid = <dtml-var table_1>.uid
<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_2>.uid = <dtml-var table_1>.category_uid
<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_1>.base_category_uid = <dtml-var "portal_categories.aggregate.getUid()">
AND <dtml-var table_0>.uid = <dtml-var table_1>.uid
AND <dtml-var table_0>.parent_uid = <dtml-var query_table>.uid
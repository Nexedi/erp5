<dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.specialise.getUid()">
<dtml-var RELATED_QUERY_SEPARATOR>

<dtml-var table_0>.uid = <dtml-var table_2>.parent_uid
<dtml-var RELATED_QUERY_SEPARATOR>

<dtml-var table_2>.uid = <dtml-var table_1>.parent_uid
<dtml-var RELATED_QUERY_SEPARATOR>

<dtml-var table_3>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_1>.uid = <dtml-var query_table>.parent_uid
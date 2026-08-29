<dtml-var table_0>.uid = <dtml-var table_1>.uid
<dtml-var RELATED_QUERY_SEPARATOR>
 <dtml-var table_0>.parent_uid = <dtml-var query_table>.uid
AND <dtml-var table_0>.portal_type = 'Email'
AND <dtml-var table_0>.id = 'default_email'

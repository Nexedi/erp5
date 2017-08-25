<dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.destination.getUid()">
AND <dtml-var table_1>.uid = <dtml-var table_0>.uid
AND <dtml-var table_1>.portal_type = 'Free Subscription'
AND <dtml-var table_1>.validation_state = 'validated'

<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_0>.uid = <dtml-var table_2>.uid
AND <dtml-var table_2>.base_category_uid = <dtml-var "portal_categories.resource.getUid()">

<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_3>.uid = <dtml-var table_1>.uid
<dtml-let now="DateTime()">
  AND ( <dtml-var table_3>.effective_date is NULL OR <dtml-var table_3>.effective_date <= <dtml-sqlvar now type="datetime"> ) 
  AND ( <dtml-var table_3>.expiration_date is NULL OR <dtml-var table_3>.expiration_date >= <dtml-sqlvar now type="datetime"> )
</dtml-let>

<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_2>.category_uid = <dtml-var table_4>.uid
AND <dtml-var table_4>.portal_type = 'Service'

<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_0>.category_uid = <dtml-var query_table>.uid

<dtml-var table_1>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_1>.portal_type = "Bank Reconciliation"
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.aggregate.getUid()">
<dtml-if table_2><dtml-comment>This related key can also be used with a criterion on delivery.date, in this case we join with a 3rd table</dtml-comment>
  <dtml-var RELATED_QUERY_SEPARATOR>
  <dtml-var table_2>.uid = <dtml-var table_1>.uid
</dtml-if>
<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_0>.uid = <dtml-var query_table>.uid
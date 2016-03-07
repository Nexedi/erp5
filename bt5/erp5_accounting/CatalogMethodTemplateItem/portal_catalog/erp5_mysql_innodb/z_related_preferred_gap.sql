<dtml-var table_1>.uid = <dtml-var table_0>.category_uid
<dtml-if expr="portal_preferences.getPreferredAccountingTransactionGap()">
  AND <dtml-var table_1>.relative_url LIKE <dtml-sqlvar expr="portal_preferences.getPreferredAccountingTransactionGap()+'%'" type="string">
</dtml-if>
<dtml-var RELATED_QUERY_SEPARATOR>
 <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.gap.getUid()">
AND <dtml-var table_0>.uid = <dtml-var query_table>.uid
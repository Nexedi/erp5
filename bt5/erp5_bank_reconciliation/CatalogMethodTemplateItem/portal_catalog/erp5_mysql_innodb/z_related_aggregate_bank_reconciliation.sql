<dtml-var table_1>.uid = <dtml-var table_0>.category_uid
AND <dtml-var table_1>.portal_type = "Bank Reconciliation"
AND <dtml-var table_0>.base_category_uid = <dtml-var "portal_categories.aggregate.getUid()">
<dtml-if table_2><dtml-comment>This related key can also be used with a criterion on delivery.date, in this case we join with a 3rd table</dtml-comment>
  <dtml-var RELATED_QUERY_SEPARATOR>
  <dtml-var table_2>.uid = <dtml-var table_1>.uid
</dtml-if>
<dtml-var RELATED_QUERY_SEPARATOR>
<dtml-var table_0>.uid = <dtml-var query_table>.uid

-- A line can be reconcilied for source_payment or destination_payment
-- so we also add a condition that the related bank reconciliation is
-- for "this side". Another approach, more efficient, is to customize `stock`
-- table to add `aggregate_bank_reconciliation_date` and `aggregate_bank_reconciliation_uid`
-- columns. See https://lab.nexedi.com/nexedi/erp5/merge_requests/495
AND stock.payment_uid in (
  select category.category_uid
  from category
  where <dtml-var table_1>.uid = category.uid
  and category.base_category_uid = <dtml-var "portal_categories.source_payment.getUid()"> )

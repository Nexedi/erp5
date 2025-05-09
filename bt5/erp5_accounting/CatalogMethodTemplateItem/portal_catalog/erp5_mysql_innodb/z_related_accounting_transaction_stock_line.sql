accounting_transaction.uid = <dtml-var table_0>.explanation_uid
and <dtml-var table_0>.portal_type in ( <dtml-in getPortalAccountingMovementTypeList><dtml-sqlvar sequence-item type="string"><dtml-unless sequence-end>, </dtml-unless></dtml-in> )

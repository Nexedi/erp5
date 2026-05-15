((<dtml-var table_0>.is_accountable = 0
AND <dtml-var table_0>.uid = catalog.parent_uid
AND <dtml-var table_0>.uid = <dtml-var table_1>.uid)

OR

(<dtml-var table_0>.is_accountable = 1
AND <dtml-var table_0>.uid = catalog.uid
AND <dtml-var table_0>.uid = <dtml-var table_1>.uid))

"""Total balance of all accounting transactions related to the project.
"""
kw['project_uid'] = context.getUid()
return context.Node_statAccountingBalance(**kw)

"""Total debit of all accounting transactions related to the project.
"""
kw['project_uid'] = context.getUid()
kw['omit_asset_decrease'] = 1
return context.Node_statAccountingBalance(**kw)

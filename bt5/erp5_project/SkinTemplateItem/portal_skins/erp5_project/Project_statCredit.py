"""Total credit of all accounting transactions related to the project.
"""
kw['project_uid'] = context.getUid()
kw['omit_asset_increase'] = 1
# here, or 0 is to prevent displaying "- 0"
return - context.Node_statAccountingBalance(**kw) or 0

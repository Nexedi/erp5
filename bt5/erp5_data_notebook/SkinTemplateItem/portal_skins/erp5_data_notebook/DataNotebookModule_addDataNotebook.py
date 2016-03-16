"""
Python script to add a new notebook to Data Notebook module.
This script also concerns for assigning an Active Process for each data notebook
created.
"""
from Products.CMFActivity.ActiveResult import ActiveResult

# Comment out person in case addition of person required to Data Notebook object
#person = context.ERP5Site_getAuthenticatedMemberPersonValue()

# Create new ActiveProcess object and getting its id
active_process = context.portal_activities.newActiveProcess()
active_process_id = active_process.getId()

# Creating new dictionary via external method to save results in ZODB
new_dict = context.Base_addLocalVariableDict()
# Add new ActiveResult object and add it to the activeprocess concerned with ...
# Data Notebook in concern
result = ActiveResult(summary=new_dict)
active_process.activateResult(result)

# Create new notebook
notebook = context.newContent(
    title=title,
    reference=reference,
    process=active_process_id,
    portal_type='Data Notebook'
  )

# Return notebook for batch_mode, used in tests
if batch_mode:
  return notebook

# Add status message to be displayed after new notebook creation
translateString = context.Base_translateString
portal_status_message = translateString(
  "New Notebook created"
)

# Redirect the notebook view with the status message being displayed
return notebook.Base_redirect('view',
  keep_items=dict(portal_status_message=portal_status_message), **kw)

"""
Python script to add a new notebook to Data Notebook module.
This script also concerns for assigning an empty notebook context for each data
notebook created.
"""
# Creating new context via external method to save results in ZODB
notebook_context = context.Base_createNotebookContext()

# Create new notebook
notebook = context.newContent(
    title=title,
    reference=reference,
    notebook_context=notebook_context,
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

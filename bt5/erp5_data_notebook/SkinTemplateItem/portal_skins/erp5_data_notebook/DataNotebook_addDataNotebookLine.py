"""
This python script concerns with creation of new notebook line which would
have notebook_code from jupyter frontend as well as its executed result
"""
# Create new Data Notebook Line object
notebook_line = context.newContent(
    notebook_code=notebook_code,
    notebook_code_result=notebook_code_result,
    mime_type=mime_type,
    portal_type="Data Notebook Line"
  )

# Return notebook_line object for batch mode, used in tests
if batch_mode:
  return notebook_line

# Add status message to be displayed after new notebook line creation
translateString = context.Base_translateString
portal_status_message = translateString(
  "New Notebook line created"
)

# Redirect the notebook_line view with the status message being displayed
return notebook_line.Base_redirect('view',
  keep_items=dict(portal_status_message=portal_status_message), **kw)

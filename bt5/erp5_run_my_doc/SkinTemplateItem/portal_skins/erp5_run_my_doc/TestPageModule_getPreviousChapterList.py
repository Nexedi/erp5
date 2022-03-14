"""
  Fetches the listbox from session variables
"""

session = context.ERP5Site_acquireRunMyDocsSession()
if 'listbox' in session:
  listbox = session['listbox']
else:
  listbox = []

return listbox

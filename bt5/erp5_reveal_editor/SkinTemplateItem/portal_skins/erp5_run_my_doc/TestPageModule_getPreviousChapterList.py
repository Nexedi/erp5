"""
  Fetches the listbox from session variables
"""

session = context.ERP5RunMyDocs_acquireSession()
if session.has_key('listbox'):
  listbox = session['listbox']
else:
  listbox = []

return listbox

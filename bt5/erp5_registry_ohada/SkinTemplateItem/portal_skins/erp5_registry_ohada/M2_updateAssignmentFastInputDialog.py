"""
  This script just returns what the user entered in
  the fast input form.
"""
portal = context.getPortalObject()
context.Base_updateDialogForm(listbox=listbox)
return context.M2_viewAssignmentFastInputDialog(**kw)

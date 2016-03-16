selection_id = 'python_shell_selection'
portal = context.getPortalObject()
portal_selections = portal.portal_selections

if python_expression is None:
  python_expression = context.REQUEST.get('python_expression')
if python_expression is None:
  # take from hard coded selection as when browsing listboxes
  # sql_expression is simply not available
  selection_object = portal_selections.getSelectionParamsFor(selection_id)
  if selection_object:
    python_expression = selection_object.get('python_expression')

# update selection
portal_selections.setSelectionParamsFor(selection_id, \
         dict(python_expression=python_expression))

# pass all to code runner
return context.Base_runPythonCode(python_expression)

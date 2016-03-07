selection_id = 'sql_shell_selection'
portal = context.getPortalObject()
portal_selections = portal.portal_selections

if sql_expression is None:
  sql_expression = context.REQUEST.get('sql_expression')
if sql_expression is None:
  # take from hard coded selection as when browsing listboxes
  # sql_expression is simply not available
  selection_object = portal_selections.getSelectionParamsFor(selection_id)
  if selection_object:
    sql_expression = selection_object.get('sql_expression')

# If not expression return empty list
if not sql_expression: return ()

# using semicolumn can kill zope
sql_expression = sql_expression.replace(';', ' ')

# update selection
portal_selections.setSelectionParamsFor(selection_id, \
         dict(sql_expression=sql_expression))

# pass all to code runner
return context.Base_zExecuteSQL(sql_expression=sql_expression)

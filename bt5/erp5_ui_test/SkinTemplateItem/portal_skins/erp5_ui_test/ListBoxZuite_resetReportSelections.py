"""Reset report sleections"""

manage_deleteSelection = context.getPortalObject().portal_selections.manage_deleteSelection
for index in xrange(3):
  try:
    manage_deleteSelection('x%s_foo_dummy_listbox_selection' % (index, ))
  except KeyError:
    pass
return "Done."

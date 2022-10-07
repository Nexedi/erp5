"""Reset report selections"""
from six.moves import range

manage_deleteSelection = context.getPortalObject().portal_selections.manage_deleteSelection
for index in range(3):
  try:
    manage_deleteSelection('x%s_foo_dummy_listbox_selection' % (index, ))
  except KeyError:
    pass
try:
  manage_deleteSelection('foo_dummy_returning_only_what_is_shown_listbox_selection')
except KeyError:
  pass
return "Done."

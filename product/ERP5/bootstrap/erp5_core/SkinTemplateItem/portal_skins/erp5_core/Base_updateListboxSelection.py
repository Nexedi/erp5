from past.builtins import basestring
portal = context.getPortalObject()
get = portal.REQUEST.get
selection_name = get('list_selection_name')

if isinstance(selection_name, basestring):
  portal.portal_selections.updateSelectionCheckedUidList(
    selection_name, get('listbox_uid'), get('uids'))

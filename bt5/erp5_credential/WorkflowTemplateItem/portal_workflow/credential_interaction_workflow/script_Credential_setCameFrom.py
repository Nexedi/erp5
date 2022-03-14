document = state_change['object']
if document.REQUEST.get('came_from', None) is not None:
  document.setUrlString(document.REQUEST.get('came_from', None))
else:
  document.setUrlString(document.getPortalObject().absolute_url())

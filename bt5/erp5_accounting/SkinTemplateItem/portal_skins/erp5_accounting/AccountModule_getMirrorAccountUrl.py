index = context.portal_selections.getSelectionIndexFor(selection_name)
object = brain.getObject()
object = object.getDestinationValue()
if object is None:
  url = None
else:
  url = object.absolute_url() + '/view?selection_index=%s&amp;selection_name=%s&amp;reset=1' % (index, selection_name)

return url

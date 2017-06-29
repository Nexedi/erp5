index = context.portal_selections.getSelectionIndexFor(selection_name)
account = brain.getObject()
account = account.getDestinationValue()
if account is not None:
  return '%s/view?selection_index=%s&amp;selection_name=%s&amp;reset=1' % (
    account.absolute_url(), index, selection_name)

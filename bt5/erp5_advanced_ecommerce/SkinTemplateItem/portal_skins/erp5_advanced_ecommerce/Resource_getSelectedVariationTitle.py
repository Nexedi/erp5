variation = context.REQUEST.get('variation', None)
if variation:
  return context.restrictedTraverse(variation).getTranslatedTitle()

return ""

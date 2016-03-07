request = container.REQUEST
if request.get('landscape'):
  return context.Base_getODTLandscapeStyleSheet
return context.Base_getODTPortraitStyleSheet

from Products.ERP5Type.Message import Message

# XXX for now, we always use the default Base_getODSStyleSheet
# we use to have Base_getODSListStyleSheet with a line at the bottom of
# the page, for better print display. Now we rather agreed that
# ods_style is a style for export, not report and the rendering appearance
# was not so important.
return context.Base_getODSStyleSheet

translate = lambda msg: Message('ui', msg)
request = context.REQUEST
landscape = int(request.get('landscape', 0))
if context.pt != 'form_list':
  if landscape == 1:
    #normal style sheet with preview of landscape
    return context.Base_getODSStyleSheetLandscape
  else:
    #preview portrait(Default) 
    return context.Base_getODSStyleSheet
else:
  if landscape == 1:
    #style sheet for list, there is under line in preview
    return context.Base_getODSListStyleSheetLandscape
  else:
    #preview portrait(Default)
    return context.Base_getODSListStyleSheet

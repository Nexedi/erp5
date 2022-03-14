from builtins import str
request = context.REQUEST
total_line = int(kw.get('total_line','0')) or int(request.get('total_line','0'))
title = kw.get('rss_title', None) or request.get('rss_title','No title')
portal_selection = getattr(context,'portal_selections')
selection = portal_selection.getSelectionFor(kw.get('selection_name',None) or request.get('selection_name',''))
params = selection.getParams()
readItemList = params.get('rss_read_item:list', {})
readItemCount = len(readItemList)
unreadItemCount = total_line - readItemCount
if unreadItemCount > 0:
  return title +' ('+str(unreadItemCount)+')'
return title

##parameters=form_id

REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
  context.manage_copyObjects(ids=REQUEST['ids'], REQUEST=REQUEST, RESPONSE=REQUEST.RESPONSE)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Item(s)+Copied.')
elif REQUEST.has_key('uids'):
  context.manage_copyObjects(uids=REQUEST['uids'], REQUEST=REQUEST, RESPONSE=REQUEST.RESPONSE)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Item(s)+Copied.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Please+select+one+or+more+items+to+copy+first.')

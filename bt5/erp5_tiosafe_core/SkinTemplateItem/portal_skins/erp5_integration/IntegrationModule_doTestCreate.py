selection_name = kw['list_selection_name']
from Products.PythonScripts.standard import url_quote

uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)

if len(uids) == 0:
  return context.REQUEST.RESPONSE.redirect(
           '%s/%s?'
           'portal_status_message=%s' % ( context.absolute_url(), kw['dialog_id'],
                               url_quote('No Object Selected.')))


conduit_id = context.getDestinationSectionValue().getConduitModuleId()

for uid in uids:
  context.callAddNodeOnConduit(context, conduit_id, uid)


return context.REQUEST.RESPONSE.redirect(
           '%s/%s?'
           'portal_status_message=%s' % ( context.absolute_url(), kw['dialog_id'],
                               url_quote('Request sent.')))

# This script will update the url of pub/sub on which it is called to
# the current site URL
url = context.getPortalObject().absolute_url()
if context.getPortalType() == "SyncML Subscription":
  context.edit(url_string=url,subscription_url_string=url)
else:
  context.edit(url_string=url)

message = context.Base_translateString('URL updated')
return context.Base_redirect(form_id, keep_items={'portal_status_message' : message},  **kw)

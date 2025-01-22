from Products.ERP5Type.Document import newTempBase
from DateTime import DateTime
from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

portal = context.getPortalObject()

# Intentionally use first, rather them later
# This prevents change the entry too often whenever
# multiple activities are failing over and over
search_kw = {
  'processing_node': -2,
  #'order_by': (('date', 'ASC'),),
  'count': 1
}

message_list = portal.portal_activities.getMessageTempObjectList(**search_kw)
if len(message_list):
  activity_entry = message_list[0]
  message = context.Base_translateString('You have one or more activity failures.')
  # Be nice with renderjs_runner
  web_site = context.getWebSiteValue()
  if web_site is None:
    web_site_url = portal.absolute_url()
  else:
    web_site_url = web_site.absolute_url() + "/#"
  return [
    newTempBase(portal, "_",
      uid=activity_entry.uid,
      date=DateTime().earliestTime(),
      link="%s/portal_activities" % web_site_url,
      title=message
    )]

return []

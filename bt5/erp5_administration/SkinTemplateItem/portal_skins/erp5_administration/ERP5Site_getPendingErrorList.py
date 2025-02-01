from Products.ERP5Type.Document import newTempBase
from DateTime import DateTime
from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

portal = context.getPortalObject()

# Use only the first entry. This prevents change the rss content
# too often whenever multiple activities are failing over time.
message_list = portal.portal_activities.getMessageTempObjectList(processing_node=-2,
                                                                 count=1)
if not len(message_list):
  return []

message = portal.Base_translateString('You have one or more activity failures.')

# Make compatible with renderjs_runner
web_site = context.getWebSiteValue()
if web_site is None:
  web_site_url = portal.absolute_url()
else:
  web_site_url = web_site.absolute_url() + "/#"
return [
  newTempBase(portal, "rss_entry",
    uid=message_list[0].uid,
    date=DateTime().earliestTime(),
    link="%s/portal_activities" % web_site_url,
    title=message)]

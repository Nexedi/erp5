from Products.ERP5Type.Document import newTempBase
from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery
from DateTime import DateTime
from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

portal = context.getPortalObject()
# Make compatible with renderjs_runner
web_site = context.getWebSiteValue()
if web_site is None:
  web_site_url = portal.absolute_url()
else:
  web_site_url = web_site.absolute_url() + "/#"

pending_error_message_list = []

# Use only the first entry. This prevents change the rss content
# too often whenever multiple activities are failing over time.
message_list = portal.portal_activities.getMessageTempObjectList(
  processing_node=-2, count=1)
if len(message_list):
  message = portal.Base_translateString('You have one or more activity failures.')
  pending_error_message_list.append(
    newTempBase(portal, "rss_entry",
      uid=message_list[0].uid,
      date=DateTime().earliestTime(),
      link="%s/portal_activities" % web_site_url,
      title=message))

alarm_list = portal.portal_catalog(
  portal_type=portal.getPortalAlarmTypeList(),
  alarm_date=NegatedQuery(Query(alarm_date=None)),
  sort_on=(('uid', 'ASC'),)
)

for alarm in alarm_list:
  if not alarm.isEnabled():
    continue
  if alarm.sense():
    message = portal.Base_translateString('You have one or more alarms with error.')
    pending_error_message_list.append(
      newTempBase(portal, "rss_entry",
        uid=alarm.getUid(), # XXX Probably not a good idea
        date=DateTime().earliestTime(),
        link="%s/portal_alarms" % web_site_url,
        title=message))
    break

return pending_error_message_list

"""Returns all support requests events for RSS
"""
from Products.PythonScripts.standard import Object
portal = context.getPortalObject()
document_type_list = portal.getPortalDocumentTypeList()

# XXX jerome: check this apparently this is 1000 for my user jerome
limit = min(limit, 30)

def makeLine(kw):
  return Object(**kw)

getSupportRequest_memo = {}
def getSupportRequestInfo(event):
  follow_up = event.getFollowUp()
  __traceback_info__ = (event, follow_up)
  # XXX jerome: what if user cannot access the ticket ?
  # is it really supposed to happen ?
  try:
    return getSupportRequest_memo[follow_up]
  except KeyError:
    support_request = portal.restrictedTraverse(follow_up, None)
    if support_request is None:
      return '', '', '' # XXX
    getSupportRequest_memo[follow_up] = (
      support_request.getTitle(),
      support_request.getResourceTranslatedTitle() or '',
      support_request.SupportRequest_getSupportRequestLink(),
    )
    return getSupportRequest_memo[follow_up]


data_list = []
for brain in portal.portal_simulation.getMovementHistoryList(
    security_query=portal.portal_catalog.getSecurityQuery(),
    portal_type=portal.getPortalEventTypeList(),
    only_accountable=False,
    follow_up_portal_type='Support Request',
    omit_input=True,
    # XXX we still don't have getCurrentMovementHistoryList
    simulation_state=('started', 'stopped', 'delivered'),
    limit=limit,
    sort_on=(('stock.date', 'desc'),
             ('uid', 'desc')),):
  event = brain.getObject()
  (support_request_title,
   support_request_category,
   support_request_link) = getSupportRequestInfo(event)
  data_list.append(
      makeLine({
        # XXX or {author} commented on {support_request} / {author} opened new Ticket: {support_request} ?
        'title': support_request_title,
        'category': support_request_category,
        'author': brain.node_title,
        'link': support_request_link,
        'description': event.asStrippedHTML(),
        'pubDate': brain.date,
        'guid': event.getSourceReference() or event.absolute_url(),
        'thumbnail': ( # XXX this is not really a thumbnail, but it's what RSS style uses for <enclosure/>
                       # Also, with this `thumbnail` it will look good for image, and most of the time
                       # users attach a screenshot of their problem.
            event.getDefaultAggregate(portal_type=document_type_list, checked_permission="View")
            and event.getDefaultAggregateValue(portal_type=document_type_list).File_getDownloadUrl()
            or None)
        }
      )
    )

return data_list

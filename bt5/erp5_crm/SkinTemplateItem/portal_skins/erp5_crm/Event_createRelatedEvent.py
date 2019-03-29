# this script allows to create a new related event by causality for
# the current event
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
N_ = context.Base_translateString
date = DateTime()
portal = context.getPortalObject()

if portal_type not in portal.event_module.getVisibleAllowedContentTypeList():
  raise WorkflowException("You Don't Have Permission to Add New Event")

# Create the draft Event
related_event = portal.event_module.newContent(
                       portal_type=portal_type,
                       title=title,
                       description=description,
                       start_date=date,
                       source=context.getDefaultDestination(),
                       destination=context.getDefaultSource(),
                       causality=context.getRelativeUrl(),
                       follow_up=context.getFollowUp(),
                       )

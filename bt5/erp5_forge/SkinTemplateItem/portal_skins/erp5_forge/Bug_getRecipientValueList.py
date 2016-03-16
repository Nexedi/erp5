# Define Recipents
project = context.getDestinationProjectValue()
portal = context.getPortalObject()
if project is not None:
  recipient_list = [ i.getParentValue() for i in project.getDestinationProjectRelatedValueList(portal_type="Assignment")]
else:
  recipient_list = context.getDestinationValueList() + context.getSourceValueList()

#If highest level of severity is reach, send Notifications also to source_decision
if context.getBugSeverityUid():
  bug_severity_list = portal.portal_categories.bug_severity.getCategoryChildValueList(sort_on='int_index')
  if bug_severity_list and\
     bug_severity_list[-1].getUid() ==\
     context.getBugSeverityUid():
    recipient_list.extend(context.getSourceDecisionValueList())
return recipient_list

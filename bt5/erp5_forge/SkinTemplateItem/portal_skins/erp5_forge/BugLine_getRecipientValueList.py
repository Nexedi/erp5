bug_line = context
bug = bug_line.getParentValue()
project = bug.getSourceProjectValue()
portal = bug.getPortalObject()
if project is not None:
  recipient_list = [ i.getParentValue() for i in project.getDestinationProjectRelatedValueList(portal_type="Assignment")]
else:
  recipient_list = bug_line.getDestinationValueList() or bug.getDestinationValueList()
  recipient_list.extend(bug_line.getSourceValueList() or bug.getSourceValueList())

#If highest level of severity is reach, send Notifications also to source_decision
if bug.getBugSeverityUid() is not None:
  bug_severity_list = portal.portal_categories.bug_severity.getCategoryChildValueList(sort_on='int_index')
  if bug_severity_list and\
     bug_severity_list[-1].getUid() ==\
     bug.getBugSeverityUid():
    recipient_list.extend(bug.getSourceDecisionValueList())

unique_recipient_list = []
for recipient in recipient_list:
  if recipient.getRelativeUrl() not in [ur.getRelativeUrl() for ur in unique_recipient_list]:
    unique_recipient_list.append(recipient)
return unique_recipient_list

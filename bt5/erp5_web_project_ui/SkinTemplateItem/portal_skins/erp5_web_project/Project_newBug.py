"""
  Creates a new bug on the current project, opens it once its reporter is its Supervisor, and jumps to it.
"""
from DateTime import DateTime
Base_translateString = context.Base_translateString
portal_type = 'Bug'
module = context.getDefaultModule(portal_type)

if portal_type not in module.getVisibleAllowedContentTypeList():
  return context.Base_redirect(form_id,
                               keep_items=dict(
    portal_status_message=Base_translateString("You do not have permission to add new bug.")))

bug_kw = {}
if bug_severity:
  bug_kw['bug_severity'] = bug_severity
person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is not None:
  bug_kw['source_decision_value'] = person

bug = module.newContent(portal_type=portal_type,
                        title=title,
                        description=description,
                        source_project=context.getRelativeUrl(),
                        # required by nexedi-erp5 BugConstraint
                        start_date=DateTime(),
                        **bug_kw)
if bug.getSourceDecision() is not None:
  # Supervisor keeps edit rights once the bug is opened
  bug.confirm()

portal_status_message = Base_translateString(
  "Created and associated a new ${portal_type} to the project.",
  mapping = dict(portal_type=Base_translateString(portal_type)))
kw['keep_items'] = dict(portal_status_message=portal_status_message)
return bug.Base_redirect('view', **kw)

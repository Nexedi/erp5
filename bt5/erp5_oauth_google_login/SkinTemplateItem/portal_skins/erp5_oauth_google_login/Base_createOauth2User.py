from DateTime import DateTime

if context.REQUEST.get('Base_createOauth2User') is not None:
  return

context.REQUEST.set('Base_createOauth2User', 1)
portal = context.getPortalObject()

if portal.portal_activities.countMessageWithTag(tag) > 0:
  return

person = portal.ERP5Site_getAuthenticatedMemberPersonValue(reference)
if person is not None:
  return

activate_kw = {'tag': tag}
# In future we can move this script to another, because this script is generic enough
# to support Facebook login
if reference.startswith("go_"):
  portal_type = "Google Login"
else:
  raise RuntimeError("Impossible to select a portal type")

if erp5_username in ("Anonymous User", None):
  person = portal.person_module.newContent(portal_type='Person',
                                           reference=reference,
                                           first_name=first_name,
                                           last_name=last_name,
                                           default_email_coordinate_text=email,
                                           activate_kw=activate_kw)
  # Support erp5_credential
  getDuration = getattr(portal.portal_preferences,
                        "getPreferredCredentialAssignmentDuration",
                        None)
  assignment_duration = getDuration and getDuration() or 365
  today = DateTime()
  delay = today + assignment_duration

  # Support erp5_credential
  getAssignmentCategoryList = getattr(portal.portal_preferences,
                                      "getPreferredSubscriptionAssignmentCategoryList",
                                      None)

  category_list = getAssignmentCategoryList and getAssignmentCategoryList() or []
  assignment = person.newContent(
    portal_type='Assignment',
    category_list=category_list,
    start_date=today,
    stop_date=delay,
    activate_kw=activate_kw)
  assignment.open(activate_kw=activate_kw)
  person.setRoleList(assignment.getRoleList())
else:
  person = portal.ERP5Site_getAuthenticatedMemberPersonValue(erp5_username)

login = person.newContent(portal_type=portal_type,
                          reference=reference)
login.validate(activate_kw=activate_kw)

if person.getValidationState() != "validated":
  person.validate(activate_kw=activate_kw)

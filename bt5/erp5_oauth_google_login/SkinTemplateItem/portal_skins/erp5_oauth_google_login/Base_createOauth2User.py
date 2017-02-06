from DateTime import DateTime

if context.REQUEST.get('Base_createOauth2User') is not None:
  return

context.REQUEST.set('Base_createOauth2User', 1)
portal = context.getPortalObject()

if portal.portal_activities.countMessageWithTag(tag) > 0:
  # If activity already exists, it means that the user reloaded the page and
  # searchUsers() from ERP5ExternalOauth2ExtractionPlugin:186 did not find the user yet
  return

person = portal.Base_getUserValueByUserId(reference)
current_user = portal.portal_membership.getAuthenticatedMember()

if person is not None or (current_user and current_user is None):
  # Script should here stop if person exists or the user logged in is a Zope user
  return

activate_kw = {'tag': tag}

# In future we can move this script to another, because this script is generic enough
# to support Facebook login, for example.
assert login_portal_type in ("Google Login",), "Impossible to select a portal type"

if user_id in ("Anonymous User", None):
  person = portal.person_module.newContent(portal_type='Person',
                                           user_id=reference,
                                           first_name=first_name,
                                           last_name=last_name,
                                           default_email_coordinate_text=email,
                                           activate_kw=activate_kw)
  duration = getattr(portal.portal_preferences,
                     "getPreferredCredentialAssignmentDuration",
                     lambda: 0)() or 365
  today = DateTime()
  delay = today + duration

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
  person.setDefaultCareerRoleList(assignment.getRoleList())
else:
  person = context.Base_getUserValueByUserId(user_id)

login = person.newContent(portal_type=login_portal_type,
                          reference=reference)
login.validate(activate_kw=activate_kw)

if person.getValidationState() != "validated":
  person.validate(activate_kw=activate_kw)

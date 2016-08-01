# Gets the Head Office Organisation of a Business Group
# The Head Office is the Organisation whose one of its roles matches the role
# category defined as "Head Office Role" in the "Organisation" system preferences
portal = context.getPortalObject()
group_base_category = portal.portal_categories.group

organisation_group = context.getGroupValue()
if organisation_group is None:
  return None

head_office_category = portal.portal_preferences.getPreferredHeadOfficeOrganisationRole()

head_office_list = []

while len(head_office_list) == 0 and organisation_group != group_base_category:
  organisation_list = portal.portal_catalog(portal_type="Organisation", group_uid=organisation_group.getUid())

  head_office_list = [organisation.getObject() for organisation in organisation_list
                      if head_office_category in organisation.getRoleList()]

  organisation_group = organisation_group.getParentValue()

if len(head_office_list) == 0:
  return None
if len(head_office_list) == 1:
  return head_office_list.pop()
else:
  return head_office_list

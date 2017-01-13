portal = context.getPortalObject()

user_name = context.portal_membership.getAuthenticatedMember().getIdOrUserName()

person_or_organisation_list = portal.portal_catalog(\
                                portal_type=['Organisation', 'Person'], 
                                reference=user_name)

if len(person_or_organisation_list) > 0:
  return True
return False

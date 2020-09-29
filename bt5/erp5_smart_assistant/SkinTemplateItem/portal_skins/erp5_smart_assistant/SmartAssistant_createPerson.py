portal = context.getPortalObject()
person_module = portal.getDefaultModule('Person')
organisation_module = portal.getDefaultModule('Organisation')

organisations = portal.portal_catalog.getResultValue(
  portal_type='Organisation', title=organisation)

if not organisations:
  organisation = organisation_module.newContent(
    title=organisation,
    portal_type='Organisation')
else:
  organisation = organisations.getObject()

person_module.newContent(
  first_name=first_name, last_name=last_name,
  default_telephone_text=telephone,
  default_email_text=email,
  career_subordination_value=organisation,
  description=description,
  portal_type='Person')

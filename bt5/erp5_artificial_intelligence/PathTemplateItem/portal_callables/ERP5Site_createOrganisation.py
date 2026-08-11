import json
portal = context.getPortalObject()

if reference:
  organisation = portal.portal_catalog.getResultValue(
    portal_type='Organisation', reference=reference)
else:
  organisation = portal.portal_catalog.getResultValue(
    portal_type='Organisation', title=title)

if organisation is not None:
  return json.dumps({
    'created': False,
    'relative_url': organisation.getRelativeUrl(),
    'title': organisation.getTitle(),
    'reference': organisation.getReference(),
  })

organisation = portal.organisation_module.newContent(
  portal_type='Organisation',
  title=title,
  reference=reference,
)
organisation.validate()

return json.dumps({
  'created': True,
  'relative_url': organisation.getRelativeUrl(),
  'title': organisation.getTitle(),
  'reference': organisation.getReference(),
})

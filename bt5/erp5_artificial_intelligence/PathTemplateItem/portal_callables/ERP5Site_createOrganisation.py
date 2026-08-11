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
    'dry_run': dry_run,
    'created': False,
    'relative_url': organisation.getRelativeUrl(),
    'title': organisation.getTitle(),
    'reference': organisation.getReference(),
  })

if dry_run:
  return json.dumps({
    'dry_run': True,
    'created': False,
    'title': title,
    'reference': reference,
    'message': 'Preview only, nothing was created. Call again with dry_run=false to actually create the organisation.',
  })

organisation = portal.organisation_module.newContent(
  portal_type='Organisation',
  title=title,
  reference=reference,
)
organisation.validate()

return json.dumps({
  'dry_run': False,
  'created': True,
  'relative_url': organisation.getRelativeUrl(),
  'title': organisation.getTitle(),
  'reference': organisation.getReference(),
})

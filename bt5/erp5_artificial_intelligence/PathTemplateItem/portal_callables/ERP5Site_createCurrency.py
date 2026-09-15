import json
portal = context.getPortalObject()

currency = portal.portal_catalog.getResultValue(
  portal_type='Currency', reference=reference)

if currency is not None:
  return json.dumps({
    'dry_run': dry_run,
    'created': False,
    'relative_url': currency.getRelativeUrl(),
    'title': currency.getTitle(),
    'reference': currency.getReference(),
  })

if dry_run:
  return json.dumps({
    'dry_run': True,
    'created': False,
    'title': title or reference,
    'reference': reference,
    'message': 'Preview only, nothing was created. Call again with dry_run=false to actually create the currency.',
  })

currency = portal.currency_module.newContent(
  portal_type='Currency',
  title=title or reference,
  reference=reference,
)
currency.validate()

return json.dumps({
  'dry_run': False,
  'created': True,
  'relative_url': currency.getRelativeUrl(),
  'title': currency.getTitle(),
  'reference': currency.getReference(),
})

import json
portal = context.getPortalObject()

currency = portal.portal_catalog.getResultValue(
  portal_type='Currency', reference=reference)

if currency is not None:
  return json.dumps({
    'created': False,
    'relative_url': currency.getRelativeUrl(),
    'title': currency.getTitle(),
    'reference': currency.getReference(),
  })

currency = portal.currency_module.newContent(
  portal_type='Currency',
  title=title or reference,
  reference=reference,
)
currency.validate()

return json.dumps({
  'created': True,
  'relative_url': currency.getRelativeUrl(),
  'title': currency.getTitle(),
  'reference': currency.getReference(),
})

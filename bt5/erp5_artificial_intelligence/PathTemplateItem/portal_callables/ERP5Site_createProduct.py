import json
portal = context.getPortalObject()

if reference:
  product = portal.portal_catalog.getResultValue(
    portal_type='Product', reference=reference)
else:
  product = portal.portal_catalog.getResultValue(
    portal_type='Product', title=title)

if product is not None:
  return json.dumps({
    'created': False,
    'relative_url': product.getRelativeUrl(),
    'title': product.getTitle(),
    'reference': product.getReference(),
  })

product = portal.product_module.newContent(
  portal_type='Product',
  title=title,
  reference=reference,
)
product.validate()

return json.dumps({
  'created': True,
  'relative_url': product.getRelativeUrl(),
  'title': product.getTitle(),
  'reference': product.getReference(),
})

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
    'dry_run': dry_run,
    'created': False,
    'relative_url': product.getRelativeUrl(),
    'title': product.getTitle(),
    'reference': product.getReference(),
  })

if dry_run:
  return json.dumps({
    'dry_run': True,
    'created': False,
    'title': title,
    'reference': reference,
    'message': 'Preview only, nothing was created. Call again with dry_run=false to actually create the product.',
  })

product = portal.product_module.newContent(
  portal_type='Product',
  title=title,
  reference=reference,
)
product.validate()

return json.dumps({
  'dry_run': False,
  'created': True,
  'relative_url': product.getRelativeUrl(),
  'title': product.getTitle(),
  'reference': product.getReference(),
})

import json
portal = context.getPortalObject()

try:
  supplier = portal.restrictedTraverse(supplier_id)
except (KeyError, AttributeError):
  supplier = None

currency_value = portal.portal_catalog.getResultValue(
  portal_type='Currency', reference=currency)

if supplier is None or currency_value is None:
  return json.dumps({
    'dry_run': dry_run,
    'created': False,
    'error': (
      'Could not resolve supplier_id=%r or currency=%r: they do not exist '
      'yet. This is expected if this is still a preview; do not call any '
      'tool with dry_run=false because of this error.' % (supplier_id, currency)
    ),
  })

if dry_run:
  return json.dumps({
    'dry_run': True,
    'created': False,
    'supplier': supplier.getTitle(),
    'currency': currency,
    'lines': lines,
    'message': 'Preview only, nothing was created. Call again with dry_run=false to actually create the purchase order.',
  })

order = portal.purchase_order_module.newContent(
  portal_type='Purchase Order',
  title='Purchase Order - %s' % supplier.getTitle(),
  source_value=supplier,
  source_section_value=supplier,
  price_currency_value=currency_value,
)

for line in lines:
  order.newContent(
    portal_type='Purchase Order Line',
    title=line['description'],
    quantity=line['quantity'],
    price=line.get('price'),
  )

return json.dumps({
  'dry_run': False,
  'created': True,
  'relative_url': order.getRelativeUrl(),
  'title': order.getTitle(),
  'supplier': supplier.getTitle(),
  'currency': currency,
  'line_count': len(lines),
})

import json
portal = context.getPortalObject()

supplier = portal.restrictedTraverse(supplier_id)
currency_value = portal.portal_catalog.getResultValue(
  portal_type='Currency', reference=currency)

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

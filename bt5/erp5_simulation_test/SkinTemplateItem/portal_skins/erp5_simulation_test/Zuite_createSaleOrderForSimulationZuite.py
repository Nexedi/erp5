if REQUEST is not None:
  kw = REQUEST.form.copy()
  for name in ["batch_mode", "create_order_line", "order_line_kw"]:  # all named parameters
    if name in kw:
      del kw[name]

order_line_kw = {}
for key, value in kw.items():
  if key.startswith("line_"):
    order_line_kw[key[5:]] = kw.pop(key)

portal = context.getPortalObject()

def setDefault(d1, d2):
  for key, value in d2.items():
    if key not in d1:
      d1[key] = value

today = DateTime(*DateTime().parts()[:3])
start_date = today + 10
stop_date = start_date + 10

# Create Sale Order

default_dict = {
  "start_date": start_date,
  "stop_date": stop_date,
  "price_currency": "currency_module/EUR",
  "source": "organisation_module/1",
  "source_section": "organisation_module/1",
  "source_payment": "organisation_module/1/bank",
  "destination_section": "organisation_module/2",
  "destination": "organisation_module/2",
  "destination_payment": "organisation_module/2/bank",
  "specialise": "sale_trade_condition_module/1",
}
setDefault(kw, default_dict)
# check defaults paths exists
for value in kw.values():
  if isinstance(value, basestring) and "_module/" in value:
    portal.restrictedTraverse(value)

sale_order = portal.sale_order_module.newContent(portal_type="Sale Order", **kw)

if "title" not in kw:
  if sale_order.getTitle():
    sale_order.setTitle("erp5_simulation_test " + sale_order.getTitle())
  else:
    sale_order.setTitle("Yet Another erp5_simulation_test Sale Order")

if create_order_line:
  # Create Sale Order Line

  default_dict = {
    "title": "Order Line",
    "quantity": 88.0,
    "price": 444.0,
    "resource": "product_module/1",
  }
  if order_line_kw:
    setDefault(order_line_kw, default_dict)
  else:
    order_line_kw = default_dict
  # check defaults paths exists
  for value in order_line_kw.values():
    if isinstance(value, basestring) and "_module/" in value:
      portal.restrictedTraverse(value)
  sale_order.newContent(
    portal_type="Sale Order Line",
    **order_line_kw
  )

sale_order.confirm()

if batch_mode:
  return sale_order
return sale_order.Base_redirect("view", keep_items={"portal_status_message": "Created successfully"})

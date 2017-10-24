if REQUEST is not None:
  kw = REQUEST.form.copy()
  for name in ["batch_mode", "create_order_line", "order_line_kw"]:  # all named parameters
    if name in kw:
      del kw[name]

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
  "source": "organisation_module/erp5_simulation_test_organisation_001",
  "source_section": "organisation_module/erp5_simulation_test_organisation_001",
  "source_payment": "organisation_module/erp5_simulation_test_organisation_001/bank",
  "destination_section": "organisation_module/erp5_simulation_test_organisation_002",
  "destination": "organisation_module/erp5_simulation_test_organisation_002",
  "destination_payment": "organisation_module/erp5_simulation_test_organisation_002/bank",
  "specialise": "sale_trade_condition_module/erp5_simulation_test_sale_trade_condition_001",
}
setDefault(kw, default_dict)
# check defaults paths exists
for value in default_dict.values():
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
    "resource": "apparel_model_module/erp5_simulation_test_apparel_model_001",
  }
  if order_line_kw:
    setDefault(order_line_kw, default_dict)
  else:
    order_line_kw = default_dict
  # check defaults paths exists
  for value in default_dict.values():
    if isinstance(value, basestring) and "_module/" in value:
      portal.restrictedTraverse(value)
  sale_order.newContent(
    portal_type="Sale Order Line",
    **order_line_kw
  )

sale_order.confirm()

if batch_mode:
  return sale_order
return sale_order.Base_redirect()

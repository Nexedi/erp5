import json

portal = context.getPortalObject()

electronic_invoice_value = portal.restrictedTraverse(electronic_invoice)
invoice_dict = json.loads(electronic_invoice_value.getTextContent())["en_invoice"]

# XXX-Titouan: this dict would be useful outside of this skin folder
unit_dict = {
  "C62": ("Product", "unit/piece"),
  "KGM": ("Product", "mass/kilogram"),
  "HUR": ("Service", "time/hour"),
}

def searchOrCreate(portal_type, search_dict, extra_dict=None):
  result_list = portal.portal_catalog(
    portal_type=portal_type,
    validation_state="validated",
    select_list=("relative_url",),
    limit=2,
    **search_dict,
  )

  if len(result_list) == 0:
    module = portal.getDefaultModule(portal_type)
    kw = {}
    kw.update(search_dict)
    if extra_dict:
      kw.update(extra_dict)
    obj = module.newContent(
      portal_type=portal_type,
      **kw,
    )
    obj.validate()
    return obj.getRelativeUrl()
  else:
    return result_list[0].relative_url

price_currency = searchOrCreate("Currency", { "reference": invoice_dict["currency_code"] })
description = "\n\n".join(x["note"] for x in invoice_dict["notes"])

invoice_value = portal.accounting_module.newContent(
  portal_type="Purchase Invoice Transaction",
  #specialise=
  price_currency=price_currency,
  start_date=invoice_dict["issue_date"],
  stop_date=invoice_dict["issue_date"],
  description=description,
  **kw
)

for line_dict in invoice_dict["lines"]:
  if "description" not in line_dict["item_information"]:
    line_dict["item_information"]["description"] = None
  quantity_unit = line_dict["invoiced_quantity_code"]
  (portal_type, quantity_unit) = unit_dict[quantity_unit]
  resource = searchOrCreate(portal_type, {
    "title": line_dict["item_information"]["name"],
  }, {
    "quantity_unit": quantity_unit,
    "description": line_dict["item_information"]["description"],
    #"base_contribution":
  })
  invoice_value.newContent(
    portal_type="Invoice Line",
    reference=line_dict["identifier"],
    resource=resource,
    quantity=line_dict["invoiced_quantity"],
    quantity_unit=quantity_unit,
    #price=
  )

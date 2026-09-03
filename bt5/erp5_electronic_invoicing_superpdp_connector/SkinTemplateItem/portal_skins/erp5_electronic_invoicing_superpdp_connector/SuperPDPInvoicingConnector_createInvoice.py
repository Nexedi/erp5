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

excluded_note_list = [
  "ACB",
  "BAR",
]

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
    return obj.getRelativeUrl()
  else:
    return result_list[0].relative_url

price_currency = searchOrCreate("Currency", { "reference": invoice_dict["currency_code"] })
description = "\n\n".join(x["note"] for x in invoice_dict["notes"] if x["subject_code"] not in excluded_note_list)
title = kw["reference"]
if not "source_section" in kw or not kw["source_section"]:
  title = "[%s] %s" % (invoice_dict["seller"]["name"], title)

invoice_value = portal.accounting_module.newContent(
  portal_type="Purchase Invoice Transaction",
  title=title,
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
  quantity = float(line_dict["invoiced_quantity"])
  price = None
  if "price_details" in line_dict and "item_net_price" in line_dict["price_details"]:
    price = float(line_dict["price_details"]["item_net_price"])
  else:
    # We are in the dark. Sometimes unit price is not included...
    price = float(line_dict["net_amount"]) / quantity
  invoice_value.newContent(
    portal_type="Invoice Line",
    reference=line_dict["identifier"],
    resource=resource,
    quantity=quantity,
    quantity_unit=quantity_unit,
    price=price,
  )
# XXX-Titouan: this is stupid rounding. How to do properly?
if "totals" in invoice_dict and \
    round(invoice_value.getTotalPrice(), 2) != float(invoice_dict["totals"]["total_without_vat"]):
  raise ValueError("Total computed price (%s) differs from expected value (%s)" % (invoice_value.getTotalPrice(), invoice_dict["totals"]["total_without_vat"]))

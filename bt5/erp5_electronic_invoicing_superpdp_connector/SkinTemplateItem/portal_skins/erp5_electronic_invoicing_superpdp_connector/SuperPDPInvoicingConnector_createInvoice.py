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

registration_identifier = invoice_dict["seller"]["legal_registration_identifier"]
if registration_identifier["scheme"] == "0002":
  corporate_registration_code = registration_identifier["value"]

  # Search for Organisations so that we do not need to match manually every time
  matching_source_section_list = portal.portal_catalog(
    portal_type="Organisation",
    corporate_registration_code=corporate_registration_code,
    select_list=("relative_url",),
    validation_state="validated",
  )

  if len(matching_source_section_list) == 1:
    kw["source_section"] = matching_source_section_list[0]["relative_url"]

seller_name = invoice_dict["seller"]["name"]
if "trading_name" in invoice_dict["seller"]:
  seller_name = invoice_dict["seller"]["trading_name"]
price_currency = searchOrCreate("Currency", { "reference": invoice_dict["currency_code"] })
description = "\n\n".join(x["note"].strip() for x in invoice_dict["notes"] if "subject_code" in x and x["subject_code"] not in excluded_note_list)

title = kw["reference"]
if len(invoice_dict["lines"]) == 1:
  title = invoice_dict["lines"][0]["item_information"]["name"]
if seller_name and "source_section" not in kw:
  title = context.Base_translateString("[${seller_name}] ${title}", mapping={
    "seller_name": seller_name,
    "title": title,
  })
if "invoicing_period" in invoice_dict:
  title = context.Base_translateString("${title} (from ${start_date} to ${end_date})", mapping={
    "start_date": invoice_dict["invoicing_period"]["start_date"],
    "end_date": invoice_dict["invoicing_period"]["end_date"],
    "title": title,
  })

invoice_value = portal.accounting_module.newContent(
  portal_type="Purchase Invoice Transaction",
  title=title,
  specialise="purchase_trade_condition_module/nexedi_france",
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

return invoice_value

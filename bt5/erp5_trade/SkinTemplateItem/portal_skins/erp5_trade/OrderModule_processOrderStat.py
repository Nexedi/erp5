from json import dumps
from Products.CMFActivity.ActiveResult import ActiveResult

# we build two dict, one that store amount per period per lient
# and another that either store amount per period per product and per client
# or only amount per period per product dependings on choosen group by
client_dict = {}
product_dict = {}
portal = context.getPortalObject()
translate = portal.Base_translateString
# Retrieve all lines related to documents
line_list = portal.portal_catalog(explanation_uid=[x['uid'] for x in document_list],
    select_list=['total_price', 'quantity', 'resource_title', 'strict_quantity_unit_title', 'explanation_uid'],
    **line_params)

doc_line_dict = {}
for line in line_list:
  doc_lines = doc_line_dict.setdefault(line.explanation_uid, [])
  doc_lines.append(line)

for result in document_list:
  try:
    line_list = doc_line_dict[result['uid']]
  except KeyError:
    line_list = []

  period = result['start_date']
  if period is not None:
    period = period.strftime(date_format)
  if report_group_by in ("client", "both"):
    total_price = sum([(x.total_price or 0) for x in line_list])
    # client_title -> period -> amount
    if report_type == "sale":
      client_title = result['destination_section_title']
    else:
      client_title = result['source_section_title']
    # FIXME: if two clients have the same title, do we want to group ?
    if client_title not in client_dict:
      client_dict[client_title] = {}
    if period in client_dict[client_title]:
      client_dict[client_title][period]['amount'] = client_dict[client_title][period]['amount'] + (total_price or 0)
    else:
      client_dict[client_title][period] = {'amount' : total_price or 0}
    if client_title not in product_dict:
      line_dict = product_dict[client_title] = {}
    else:
      line_dict = product_dict[client_title]
  else:
    line_dict = product_dict

  if report_group_by != "client":
    # client_title -> product_title -> period -> amount/quantity...
    # or product_title -> period -> amount/quantity...
    for line in line_list:
      # FIXME: if two resources have the same title, do we want to group ?
      product_title = line.resource_title
      if product_title not in line_dict:
        line_dict[product_title] = {period :{"amount" : line.total_price or 0,
                                             "quantity" : line.quantity or 0,
                                             "quantity_unit" : translate(line.strict_quantity_unit_title)}}
      else:
        if period not in line_dict[product_title]:
          line_dict[product_title][period] = {"amount" : line.total_price or 0,
                                               "quantity" : line.quantity or 0,
                                               "quantity_unit" : translate(line.strict_quantity_unit_title)}
        else:
          line_dict[product_title][period]['amount'] = line_dict[product_title][period]['amount'] + (line.total_price or 0)
          line_dict[product_title][period]['quantity'] = line_dict[product_title][period]['quantity'] + (line.quantity or 0)

active_process_value = portal.restrictedTraverse(active_process)
active_process_value.postResult(ActiveResult(
  sevrity=1,
  detail=dumps({
      'type' : "result",
      'client_dict' : client_dict,
      'product_dict' : product_dict,
      })
      ))

from Products.PythonScripts.standard import Object
from Products.ZSQLCatalog.SQLCatalog import Query

portal = context.getPortalObject()
category_tool = portal.portal_categories

request = container.REQUEST
from_date = request.get('from_date', None)
to_date = request.get('at_date', None)
aggregation_level = request.get('aggregation_level', None)
report_group_by = request.get('group_by', None)
quantity_unit = request.get('quantity_unit', None)
# get all category
incoterm = request.get('incoterm', None)
section_category = request.get('section_category', None)
order = request.get('order', None)
delivery_mode = request.get('delivery_mode', None)
product_line = request.get('product_line', None)
price_type = request.get('price_type', 'sale_price')

catalog_params = {}

resource_title_dict = {}

# get all organisations for the selected section category
if section_category:
  group_uid = category_tool.getCategoryValue(section_category).getUid()
  organisation_uid_list = [x.uid for x in portal.portal_catalog(
                                            portal_type="Organisation",
                                            default_group_uid=group_uid)]
  if report_type == "sale":
    catalog_params['default_source_section_uid'] = organisation_uid_list or -1
  elif report_type:
    catalog_params['default_destination_section_uid'] = organisation_uid_list or -1

# add category params if defined
if incoterm not in ('', None):
  incoterm_uid = category_tool.incoterm.restrictedTraverse(incoterm).getUid()
  catalog_params['default_incoterm_uid'] = incoterm_uid
if order not in ('', None):
  order_uid = category_tool.order.restrictedTraverse(order).getUid()
  catalog_params['default_order_uid'] = order_uid
if delivery_mode not in ('', None):
  delivery_mode_uid = category_tool.delivery_mode.restrictedTraverse(delivery_mode).getUid()
  catalog_params['default_delivery_mode_uid'] = delivery_mode_uid

# compute sql params, we group and order by date and portal type
if aggregation_level == "year":
  date_format = "%Y"
elif aggregation_level == "month":
  date_format = "%Y-%m"
elif aggregation_level == "week":
  date_format = "%Y-%U"
elif aggregation_level == "day":
  date_format = "%Y-%m-%d"

params = {"delivery.start_date":(from_date, to_date)}
query=None
if from_date is not None and to_date is not None:
  params = {"delivery.start_date":(from_date, to_date)}
  query = Query(range="minngt", **params)
elif from_date is not None:
  params = {"delivery.start_date":from_date}
  query = Query(range="min", **params)
elif to_date is not None:
  params = {"delivery.start_date":to_date}
  query = Query(range="ngt", **params)

sort_on_list = [ ('delivery.destination_section_uid', 'ASC'), ('delivery.start_date','ASC')]

if request.get('use_selection'):
  selection_name = request['selection_name']
  result_list = \
        context.portal_selections.callSelectionFor(request['selection_name'])
else:
  result_list = context.portal_catalog.searchResults(limit=None,query=query,
                                                   portal_type=doc_portal_type,
                                                   simulation_state=simulation_state,
                                                   sort_on=sort_on_list,
                                                   **catalog_params)
def Sale_getTotalPrice(sale):
  total_price = 0
  for line in sale.contentValues(filter = {'portal_type':line_portal_type}):
    if product_line and line.getResourceValue().getProductLine() == product_line:
      if price_type == 'sale_price':
        total_price = total_price + line.getTotalPrice()
      else:
        purchase_price = resource_value.getPurchaseSupplyLineBasePrice() or 0
        total_price = total_price + line.getTotalQuantity() * purchase_price
  return total_price

# we build two dict, one that store amount per period per client
# and another that either store amount per period per product and per client
# or only amount per period per product dependings on choosen group by
client_dict = {}
product_dict = {}
for result in result_list:
  result = result.getObject()
  period = result.getStartDate()
  if period is not None:
    period = period.strftime(date_format)
  if report_group_by in ("client", "both"):
    # client_title -> period -> amount
    if report_type == "sale":
      client_title = result.getDestinationSectionTitle()
    else:
      client_title = result.getSourceSectionTitle()
    # FIXME: if two clients have the same title, do we want to group ?
    if not client_dict.has_key(client_title):
      client_dict[client_title] = {}
    if client_dict[client_title].has_key(period):
      client_dict[client_title][period]['amount'] = client_dict[client_title][period]['amount'] + Sale_getTotalPrice(result)
    else:
      client_dict[client_title][period] = {'amount' : Sale_getTotalPrice(result)}
    if not product_dict.has_key(client_title):
      line_dict = product_dict[client_title] = {}
    else:
      line_dict = product_dict[client_title]
  else:
    line_dict = product_dict

  if report_group_by != "client":
    # client_title -> product_title -> period -> amount/quantity...
    # or product_title -> period -> amount/quantity...
    for line in result.contentValues(filter = {'portal_type':line_portal_type}):
      if product_line:
        if line.getResourceValue().getProductLine() != product_line:
          continue
      # Filter by quantity_unit
      if quantity_unit:
        if line.getQuantityUnit() != quantity_unit:
          continue
      # FIXME: if two resources have the same title, do we want to group ?
      if report_group_by == "function":
        if report_type == "sale":
          product_title = line.getSourceFunctionTitle()
        else:
          product_title = line.getDestinationFunctionTitle()
      else:
        product_title = line.getResourceTitle()
      resource_value = line.getResourceValue()
      resource_title_dict[product_title] = {
        'reference': resource_value.getReference(),
        'ean13_code': resource_value.getEan13Code()
      }

      if price_type == 'sale_price':
        total_price = line.getTotalPrice()
      else:
        purchase_price = resource_value.getPurchaseSupplyLineBasePrice() or 0
        total_price = line.getTotalQuantity() * purchase_price

      if not line_dict.has_key(product_title):
        line_dict[product_title] = {period :{"amount" : total_price,
                                             "quantity" : line.getTotalQuantity(),
                                             "quantity_unit" : line.getQuantityUnitTranslatedTitle()}}
      else:
        if not line_dict[product_title].has_key(period):
          line_dict[product_title][period] = {"amount" : total_price,
                                               "quantity" : line.getTotalQuantity(),
                                               "quantity_unit" : line.getQuantityUnitTranslatedTitle()}
        else:
          line_dict[product_title][period]['amount'] = line_dict[product_title][period]['amount'] + total_price
          line_dict[product_title][period]['quantity'] = line_dict[product_title][period]['quantity'] + line.getTotalQuantity()



def sortProduct(a, b):
  return cmp(a['product'], b['product'])

period_counter_dict = {}
line_list = []
append = line_list.append
extend = line_list.extend
# we build lines for listbox
if len(client_dict):
  # third party or third party + products
  for client_title in client_dict.keys():
    # lines for third party
    obj = Object(uid="new_")
    obj['client'] = client_title
    line_total_amount = 0
    for period in period_list:
      # client -> period
      if client_dict[client_title].has_key(period):
        obj['Amount %s' %(period)] = round(client_dict[client_title][period]['amount'], 2)
        line_total_amount += client_dict[client_title][period]['amount']
        if report_group_by == "client":
          if period_counter_dict.has_key('Amount %s' %(period)):
            period_counter_dict['Amount %s' %(period)] = period_counter_dict['Amount %s' %(period)] + client_dict[client_title][period]['amount']
          else:
            period_counter_dict['Amount %s' %(period)] = client_dict[client_title][period]['amount']
      else:
        obj['Amount %s' %(period)] = 0
    obj['total amount'] = round(line_total_amount, 2)
    if report_group_by == "client":
      if period_counter_dict.has_key('total amount'):
        period_counter_dict['total amount'] = period_counter_dict['total amount'] + line_total_amount
      else:
        period_counter_dict['total amount'] = line_total_amount

    append(obj)
    if report_group_by == "both":
      product_lines_list = []
      # one line per product
      if product_dict.has_key(client_title):
        line_product_dict = product_dict[client_title]
        for product_title in line_product_dict.keys():
          obj = Object(uid="new_")
          obj['product'] = product_title
          obj['product_reference'] = resource_title_dict.get(product_title)['reference']
          obj['ean13_code'] = resource_title_dict.get(product_title)['ean13_code']

          line_total_amount = 0
          line_total_quantity = 0
          for period in period_list:
            if line_product_dict[product_title].has_key(period):
              obj['Amount %s' %(period)] = round(line_product_dict[product_title][period]['amount'], 2)
              obj['Quantity %s' %(period)] = line_product_dict[product_title][period]['quantity']
              obj['Quantity Unit %s' %(period)] = line_product_dict[product_title][period]['quantity_unit']
              # total columns
              line_total_amount += line_product_dict[product_title][period]['amount']
              line_total_quantity += line_product_dict[product_title][period]['quantity']
              # counter for stat line
              if period_counter_dict.has_key('Amount %s' %(period)):
                period_counter_dict['Amount %s' %(period)] = period_counter_dict['Amount %s' %(period)] + \
                                                             line_product_dict[product_title][period]['amount']
              else:
                period_counter_dict['Amount %s' %(period)] = line_product_dict[product_title][period]['amount']
              if quantity_unit:
                if period_counter_dict.has_key('Quantity %s' %(period)):
                  period_counter_dict['Quantity %s' %(period)] = period_counter_dict['Quantity %s' %(period)] + \
                                                               line_product_dict[product_title][period]['quantity']
                else:
                  period_counter_dict['Quantity %s' %(period)] = line_product_dict[product_title][period]['quantity']
              
            else:
              obj['Amount %s' %(period)] = 0
              obj['Quantity %s' %(period)] = 0
              obj['Quantity Unit %s' %(period)] = ""
          
          obj['total quantity'] = line_total_quantity
          obj['total amount'] = round(line_total_amount, 2)
          # total for stat line
          if period_counter_dict.has_key('total amount'):
            period_counter_dict['total amount'] = period_counter_dict['total amount'] + line_total_amount
          else:
            period_counter_dict['total amount'] = line_total_amount
          if quantity_unit:
            if period_counter_dict.has_key('total quantity'):
              period_counter_dict['total quantity'] = period_counter_dict['total quantity'] + line_total_quantity
            else:
              period_counter_dict['total quantity'] = line_total_quantity

          product_lines_list.append(obj)
      # sort product list
      product_lines_list.sort(sortProduct)
      extend(product_lines_list)
else:
  # products
  if report_group_by in ("product", "function"):
    for product_title in product_dict.keys():
      obj = Object(uid="new_")
      obj['product'] = product_title
      obj['product_reference'] = resource_title_dict.get(product_title)['reference']
      obj['ean13_code'] = resource_title_dict.get(product_title)['ean13_code']

      line_total_amount = 0
      line_total_quantity = 0    
      for period in period_list:
        if product_dict[product_title].has_key(period):
          obj['Amount %s' %(period)] = round(product_dict[product_title][period]['amount'],2)
          obj['Quantity %s' %(period)] = product_dict[product_title][period]['quantity']
          obj['Quantity Unit %s' %(period)] = product_dict[product_title][period]['quantity_unit']
          # total column
          line_total_amount += product_dict[product_title][period]['amount']
          line_total_quantity += product_dict[product_title][period]['quantity']
          # counter for stat line
          if period_counter_dict.has_key('Amount %s' %(period)):
            period_counter_dict['Amount %s' %(period)] = period_counter_dict['Amount %s' %(period)] + product_dict[product_title][period]['amount']
          else:
            period_counter_dict['Amount %s' %(period)] = product_dict[product_title][period]['amount']
          if quantity_unit:
            if period_counter_dict.has_key('Quantity %s' %(period)):
              period_counter_dict['Quantity %s' %(period)] = period_counter_dict['Quantity %s' %(period)] + product_dict[product_title][period]['quantity']
            else:
              period_counter_dict['Quantity %s' %(period)] = product_dict[product_title][period]['quantity']
        else:
          obj['Amount %s' %(period)] = 0
          obj['Quantity %s' %(period)] = 0
          obj['Quantity Unit %s' %(period)] = ""

      obj['total quantity'] = line_total_quantity
      obj['total amount'] = round(line_total_amount,2)
      # total for stat line
      if period_counter_dict.has_key('total amount'):
        period_counter_dict['total amount'] = period_counter_dict['total amount'] + line_total_amount
      else:
        period_counter_dict['total amount'] = line_total_amount
      if quantity_unit:
        if period_counter_dict.has_key('total quantity'):
          period_counter_dict['total quantity'] = period_counter_dict['total quantity'] + line_total_quantity
        else:
          period_counter_dict['total quantity'] = line_total_quantity
      append(obj)

    line_list.sort(sortProduct)

obj = Object(uid="new_")
obj["client"] = 'Total'
for k,v in period_counter_dict.items():
  if "mount" in k:
    v = round(v, 2)
  obj[k] = v

request.set('stat_line', [obj,])

return line_list

from Products.PythonScripts.standard import Object
from json import loads
portal = context.getPortalObject()
request = container.REQUEST
report_group_by = request.get('group_by', None)
quantity_unit = request.get('quantity_unit', None)
active_process_path = request.get('active_process')
# We have to sum product_dict and client_dict from the results of active process
def _addDict(global_dict, local_dict, only_amount=False):
  if report_group_by == "both" and not only_amount:
    # we have client -> product -> period -> amount
    for local_title, local_product_dict in local_dict.iteritems():
      product_dict = global_dict.setdefault(local_title, {})
      for local_product, local_period_dict in local_product_dict.iteritems():
        period_dict = product_dict.setdefault(local_product, {})
        for period, local_amount_dict in local_period_dict.iteritems():
          amount_dict = period_dict.setdefault(period, {'amount' : 0, 'quantity' : 0, 'quantity_unit' : ''})
          amount_dict['amount'] = amount_dict['amount'] + local_amount_dict['amount']
          amount_dict['quantity'] = amount_dict['quantity'] + local_amount_dict['quantity']
          amount_dict['quantity_unit'] = local_amount_dict['quantity_unit']
  else:
    # We have client or product -> period -> amount
    for local_title, local_period_dict in local_dict.iteritems():
      period_dict = global_dict.setdefault(local_title, {})
      for period, local_amount_dict in local_period_dict.iteritems():
        amount_dict = period_dict.setdefault(period, {'amount' : 0, 'quantity' : 0, 'quantity_unit' : ''})
        amount_dict['amount'] = amount_dict['amount'] + local_amount_dict['amount']
        if not only_amount:
          amount_dict['quantity'] = amount_dict['quantity'] + local_amount_dict['quantity']
          amount_dict['quantity_unit'] = local_amount_dict['quantity_unit']
product_dict = {}
client_dict = {}
if active_process_path:
  active_process = portal.restrictedTraverse(active_process_path)
  for result in active_process.getResultList():
    if result.summary:
      continue
    detail = loads(result.detail)
    if detail['type'] == "result":
      result_product_dict = detail['product_dict']
      result_client_dict = detail["client_dict"]  
    else:
      continue
    if not len(client_dict) and len(result_client_dict):
      client_dict = result_client_dict.copy()
    else:
      _addDict(client_dict, result_client_dict, only_amount=True)
    
    if not len(product_dict) and len(result_product_dict):
      product_dict = result_product_dict.copy()
    else:
      _addDict(product_dict, result_product_dict)
else:
  raise ValueError("No active process found to process report")
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

traceability_list = traceability_data.split('\n')
traceability_dict = {}

def processAsEngine(data):
  #2 1 7 1 11 4 2 1 1
  return {data[11:22]: data}

def processAsTransmission(data):
  data_dict = {}
  for product in context.portal_catalog(
    portal_type='Product',
    strict_product_line_uid = context.portal_categories.product_line.part.transmission.getUid()):
    data_dict[product.getReference()] = data
  return data_dict

def processAsRadio(data):
  data_dict = {}
  for product in context.portal_catalog(
    portal_type='Product',
    strict_product_line_uid = context.portal_categories.product_line.part.radio.getUid()):
    data_dict[product.getReference()] = data
  return data_dict

def processAsComponent(data):
  return {data[0:11]: data}

def processAs18Component(data):
  # 030076518726000973
  # 518726000 is part number
  return {data[6:14].zfill(11): data}

def processAs28Component(data):
  # 030076518726000973
  # 518726000 is part number
  return {data[:11]: data}

def processAsFuelTank(data):
  data_dict = {}
  for product in context.portal_catalog(
    portal_type='Product',
    strict_product_line_uid = context.portal_categories.product_line.part.fuel_tank.getUid()):
    data_dict[product.getReference()] = data
  return data_dict

for traceability in traceability_list:
  length = len(traceability)
  if length in (30, 14, 26, 18, 10, 39, 28):
    if length == 30:
      data_dict = processAsEngine(traceability)
    elif length == 14:
      data_dict = processAsTransmission(traceability)
    elif length == 28:
      data_dict = processAs28Component(traceability)
    elif length == 26:
      data_dict = processAsComponent(traceability)
    # Handle the tires with extra data at the end.
    elif length == 39 and traceability[26:28] in ("1A", "0A"):
      data_dict = processAsComponent(traceability[:26])
    elif length == 18:
      if traceability.startswith("00000000000"):
        data_dict = processAsRadio(traceability)
      else:
        data_dict = processAs18Component(traceability)
    else:
      data_dict = processAsFuelTank(traceability)
  else:
    #unknown data
    data_dict = {traceability: traceability}
  for reference, data in data_dict.iteritems():
    if reference not in traceability_dict:
      traceability_dict[reference] = []
    if data not in traceability_dict[reference]:
      traceability_dict[reference].append(data)

return traceability_dict

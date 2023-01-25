from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

def getResourceInternalPriceSortKeyMethod(high_priority_supply_line_list):
  def resourceInternalPriceSortKeyMethod(a):
    high_priority_supply_line_list_len = len(high_priority_supply_line_list)
    if a in high_priority_supply_line_list:
      return high_priority_supply_line_list.index(a)
    elif "Internal" in a.getPortalType():
      if a.getDestinationSection():
        return high_priority_supply_line_list_len
      else:
        return high_priority_supply_line_list_len + 1
    else:
      if a.getSourceSection():
        return high_priority_supply_line_list_len + 2
      else:
        return high_priority_supply_line_list_len + 3
  return resourceInternalPriceSortKeyMethod


def getResourcePurchasePriceSortKeyMethod(high_priority_supply_line_list):
  def resourcePurchasePriceSortKeyMethod(a):
    high_priority_supply_line_list_len = len(high_priority_supply_line_list)
    if a in high_priority_supply_line_list:
      return high_priority_supply_line_list.index(a)
    elif "Purchase" in a.getPortalType():
      if a.getSourceSection():
        return high_priority_supply_line_list_len
      else:
        return high_priority_supply_line_list_len + 1
    else:
      if a.getDestinationSection():
        return high_priority_supply_line_list_len + 2
      else:
        return high_priority_supply_line_list_len + 3
  return resourcePurchasePriceSortKeyMethod


def getResourceSalePriceSortKeyMethod(high_priority_supply_line_list):
  def resourceSalePriceSortKeyMethod(a):
    high_priority_supply_line_list_len = len(high_priority_supply_line_list)
    if a in high_priority_supply_line_list:
      return high_priority_supply_line_list.index(a)
    elif "Sale" in a.getPortalType():
      if a.getDestinationSection():
        return high_priority_supply_line_list_len
      else:
        return high_priority_supply_line_list_len + 1
    else:
      if a.getSourceSection():
        return high_priority_supply_line_list_len + 2
      else:
        return high_priority_supply_line_list_len + 3
  return resourceSalePriceSortKeyMethod


def getOptimisedPriceCalculationOperandDict(default=None, context=None, **kw):
  """
   Price Method optimised by the preference
  """
  movement_portal_type = context.portal_type
  preferences = context.portal_preferences
  supply_portal_type_list = []
  if movement_portal_type in context.getPortalSaleTypeList():
    supply_portal_type_list = preferences.getPreferredSaleMovementSupplyPathTypeList()
  elif movement_portal_type in context.getPortalPurchaseTypeList():
    supply_portal_type_list = preferences.getPreferredPurchaseMovementSupplyPathTypeList()
  elif movement_portal_type in context.getPortalInternalTypeList():
    supply_portal_type_list = preferences.getPreferredInternalMovementSupplyPathTypeList()
  if supply_portal_type_list:
    supply_kw = dict(portal_type=supply_portal_type_list)
    for key in preferences.getPreferredPricingSupplyPathKeyCategoryList():
      key_uid = '%s_uid' % key
      supply_kw['default_%s' % key_uid] = context.getProperty(key_uid)
    supply_uid_list = [brain.uid for brain in context.portal_catalog(**supply_kw)]
    if supply_uid_list:
      kw['query'] = SimpleQuery(uid=supply_uid_list)
    else:
      return default
  return resource.getPriceCalculationOperandDict(default=default, context=context, **kw)

def isPricingOptimise():
  """Check whether pricing optimisation is enabled or not """
  try:
    return context.portal_preferences.getPreferredPricingOptimise()
  except AttributeError:
    # When the preference is not support the property, for instance, old sites
    return False

try:
  explanation = context.getExplanationValue()
except AttributeError:
  # Sometime, movements doesn't have an explanation.
  explanation = None

specialise_set = set()

if explanation is not None:
  explanation_type = explanation.getPortalType()
  high_priority_supply_line_list = []
  if explanation_type in context.getPortalInvoiceTypeList() +\
                              context.getPortalOrderTypeList() + context.getPortalDeliveryTypeList():
    # if there are trade conditions containing supply lines related to that
    # order/invoice, we give high priority to those supply lines
    try:
      composed_document = explanation.asContext(
        start_date=context.getStartDate(),
        stop_date=context.getStopDate(),
      ).asComposedDocument()
    except KeyError:
      pass
    else:
      for supply_line in composed_document.objectValues(
          portal_type=context.getPortalSupplyPathTypeList()):
        supply_cell_list = supply_line.objectValues(
          portal_type=context.getPortalSupplyPathTypeList())
        if supply_cell_list:
          high_priority_supply_line_list.extend(list(supply_cell_list))
        else:
          high_priority_supply_line_list.append(supply_line)
        specialise_set.add(supply_line.getParentValue().getRelativeUrl())

  # XXX FIXME: Hardcoded values
  if "Internal" in explanation_type:
    kw['sort_key_method'] = getResourceInternalPriceSortKeyMethod(
                                  high_priority_supply_line_list)
  elif "Purchase" in explanation_type:
    kw['sort_key_method'] = getResourcePurchasePriceSortKeyMethod(
                                  high_priority_supply_line_list)
  elif "Sale" in explanation_type:
    kw['sort_key_method'] = getResourceSalePriceSortKeyMethod(
                                  high_priority_supply_line_list)

resource = context.getResourceValue()

if specialise_set:
  kw['categories'] = kw.get('categories', []) + ['specialise/%s' % x for x in specialise_set]

if resource is not None:
  product_line = resource.getProductLine()
  if product_line:
    kw['categories'] = kw.get('categories', []) + ['product_line/%s' % product_line]

  if isPricingOptimise():
    return getOptimisedPriceCalculationOperandDict(default=default, context=context, **kw)
  else:
    r = resource.getPriceCalculationOperandDict(
                default=default, context=context, **kw)
  return r

return default

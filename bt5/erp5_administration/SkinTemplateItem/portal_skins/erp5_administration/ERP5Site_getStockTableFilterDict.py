from DateTime import DateTime

def getSourceAndDestinationList(instance):
  return (instance.getSourceUid(), instance.getDestinationUid())

def getSourcePaymentAndDestinationPaymentList(instance):
  return (instance.getSourcePaymentUid(), instance.getDestinationPaymentUid())

def getSimulationState(instance):
  return instance.getSimulationState()

def stripDate(date):
  """
    Strip everything from the given DateTime parameter,
    leaving just year, month and day.
  """
  if not same_type(date, DateTime()):
    return date
  return DateTime(date.Date())

def getStartDateAndStopDate(instance):
  start_date = stripDate(instance.getStartDate())
  stop_date = stripDate(instance.getStopDate())
  return (start_date, stop_date)

def getSourceSectionAndDestinationSectionList(instance):
  return (instance.getSourceSectionUid(), instance.getDestinationSectionUid())

def getTotalPrice(instance):
  price = instance.getTotalPrice()
  if price is None:
    return None
  return (instance.getDestinationInventoriatedTotalAssetPrice(), instance.getSourceInventoriatedTotalAssetPrice())

def getQuantity(instance):
  quantity = instance.getInventoriatedQuantity()
  if quantity is None:
    return None
  return (quantity, -quantity)

return {
  'node_uid':         getSourceAndDestinationList(instance),
  'payment_uid':      getSourcePaymentAndDestinationPaymentList(instance),
  'section_uid':      getSourceSectionAndDestinationSectionList(instance),
  'mirror_section_uid': getSourceSectionAndDestinationSectionList(instance),
  'date':             getStartDateAndStopDate(instance),
  'mirror_date':      getStartDateAndStopDate(instance),
  'total_price':      getTotalPrice(instance),
  'quantity':         getQuantity(instance),
  'mirror_node_uid':  getSourceAndDestinationList(instance),
  'simulation_state': getSimulationState(instance),
}

# Look at all items availables for the source and then
# display them on a listbox so that the user will be able
# to select them
from DateTime import DateTime

class Dummy:
  pass

dummy = Dummy()
node = kw.get('node',dummy)
vault = kw.get('vault',dummy)

if limit is None:
  limit = (0, -1)
list_start, list_length = limit

if item_portal_type_list is None:
  item_portal_type_list = ["Checkbook","Check"]

if listbox is None:

  if vault is not dummy:
    node = vault
  if node is dummy:
    node = None
  if node is None:
    node = context.getBaobabSource()

  if at_date is None:
    at_date = DateTime()
  item_list = []
  listbox = []
  if node is not None or disable_node:
    getCurrentTrackingList = context.portal_simulation.getCurrentTrackingList
    if disable_node:
      node=None

    kw = {
      'item_catalog_portal_type': ('Check', 'Checkbook'),
    }
    if reference not in (None, ''):
      kw['aggregate_uid'] = [x.uid for x in context.getPortalObject().portal_catalog(
        destination_payment_internal_bank_account_number=reference,
        portal_type=('Check', 'Checkbook')
      )]

    if checkbook_model not in (None, ''):
      checkbook_model_uid = context.getPortalObject().restrictedTraverse(checkbook_model).getUid()
      kw['resource_uid'] = checkbook_model_uid

    if title not in (None, ''):
      kw['item_catalog_title'] = title

    current_tracking_list = getCurrentTrackingList(
      to_date=at_date,
      node=node,
      **kw)

    if count is True:
      return len(current_tracking_list)

    item_index = -1
    for item in current_tracking_list:
      item = item.getObject()
      exclude=0
      if model_filter_dict is not None:
        resource = item.getResourceValue()
        for property,value in model_filter_dict.items():
          if resource.getProperty(property)!=value:
            exclude=1
      if destination_payment is not None:
        if destination_payment!=item.getDestinationPayment():
          exclude=1
      if not exclude:
        item_portal_type = item.getPortalType()
        if item_portal_type  in item_portal_type_list:
          if item_portal_type=='Check' and item.getSimulationState() not in ('draft','confirmed'):
            continue
          if simulation_state is not None:
            if item.getSimulationState()!=simulation_state:
              continue
          item_dict = {}
          if item_portal_type=='Check':
            item_dict['reference_range_max'] = item.getReference()
            item_dict['reference_range_min'] = item.getReference()
          else:
            item_dict['reference_range_min'] = item.getReferenceRangeMin()
            item_dict['reference_range_max'] = item.getReferenceRangeMax()
          item_dict['resource_title'] = item.getResourceTitle()
          item_dict['destination_trade'] = item.getDestinationTradeTitle()
          item_dict['check_amount_title'] = item.getCheckAmountTitle()
          item_dict['internal_bank_account_number'] = ''
          destination_payment_value = item.getDestinationPaymentValue()
          if destination_payment_value is not None:
            internal_bank_account_number = destination_payment_value.getInternalBankAccountNumber()
            item_dict['internal_bank_account_number'] = internal_bank_account_number
            item_dict['account_owner'] = item.getDestinationPaymentTitle()
          item_dict['recept_date'] = item.getStartDate()
          item_dict['selection'] = 0
          item_dict['uid'] = 'new_%s' %(item.getUid(),)
          item_index += 1
          if item_index < list_start:
            continue
          listbox.append(item_dict)
          if list_length != -1 and len(listbox) >= list_length:
            break

return listbox

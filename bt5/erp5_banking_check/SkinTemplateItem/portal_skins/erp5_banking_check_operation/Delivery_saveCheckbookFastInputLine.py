counter_line = 0
result = []
resultContainer = {}
result_line = []

if listbox is None:
  listbox = []

# remove existing lines
old_line = [x.getObject() for x in context.objectValues(portal_type=['Checkbook Delivery Line'])]
if len(old_line)>0:
  for object_list in old_line:
    context.deleteContent(object_list.getId())

cash_item_item_dict = {}
# construct dict of selected item
for listbox_line in listbox:
  if listbox_line['selection']==1:
    item = context.portal_catalog(uid=listbox_line['listbox_key'])[0].getObject()
    delivery_line = context.newContent(portal_type='Checkbook Delivery Line')
    item_dict = {}
    reference_range_min = None
    reference_range_max = None
    if item.getPortalType()=='Check':
      reference_range_min = reference_range_max = item.getReference()
    elif item.getPortalType()=='Checkbook':
      reference_range_min = item.getReferenceRangeMin()
      reference_range_max = item.getReferenceRangeMax()
    item_dict['reference_range_min'] = reference_range_min
    item_dict['reference_range_max'] = reference_range_max
    item_dict['destination_trade'] = item.getDestinationTrade()
    item_dict["resource_value"] = item.getResourceValue()
    item_dict["check_amount"] = item.getCheckAmount()
    item_dict["check_type"] = item.getCheckType()
    item_dict["price_currency"] = item.getPriceCurrency()
    item_dict["aggregate_value"] = item
    item_dict["quantity"] = 1
    delivery_line.edit(**item_dict)


request  = context.REQUEST
redirect_url = '%s/view?%s' % ( context.absolute_url()
                                , 'portal_status_message=done'
                                )
request[ 'RESPONSE' ].redirect( redirect_url )

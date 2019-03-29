# check that the amount of resources at `source` is greater or equal
# than the amount of movement of type `portal_type` in this movement

# returns 2 : no resource, 1 : insufficient balance, 0 : ok
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
# XXX this should be handled by a portal method.
currency_cash_portal_type_list = ['Banknote', 'Coin']

inventory_dict = {}
requested_dict = {}

# test all movement
tmp_list = context.contentValues(filter={'portal_type': portal_type})
#context.log('tmp_list', str((tmp_list, portal_type, context)))
#context.log('source',source)
line_list = []
resource_dict = {}
node_dict = {}
variation_text_dict = {}
start_date = context.getStartDate()
for l in tmp_list :
  # The source can be different for every line (due to getBaobabSource approach)
  if source is None:
    source_counter = l.getBaobabSource()
  else:
    source_counter = source
  # test if resource is a currency_cash
  try:
    if (l.getResourceValue().getPortalType() in currency_cash_portal_type_list) \
           and (same_source or l.getBaobabSource() == source_counter) :
      line_list.append(l)
      resource_dict[l.getResource()] = None
      node_dict[source_counter] = None
      for cell in l.objectValues() :
        variation_text_dict[cell.getVariationText()] = None
  except (AttributeError, KeyError):
    pass
#context.log("line list", line_list)
if len(line_list) == 0 :
  # no resource
  return 2

# in some case, we don't want to check balance
if no_balance_check:
  return 0

serialize_dict = {}

activity_tool = context.portal_activities
def checkActivities(source_counter):
  if activity_tool.countMessageWithTag(source_counter):
    msg = Message(domain='ui', message="There are operations pending for this vault that prevent form calculating its position. Please try again later.")
    raise ValidationFailed(msg,)

inventory_list = context.portal_simulation.getCurrentInventoryList(
                   #at_date=start_date,
                   group_by_variation=1,
                   group_by_node=1,
                   group_by_resource=1,
                   node=node_dict.keys(),
                   resource=resource_dict.keys(),
                   variation_text=variation_text_dict.keys())

inventory_dict = {}
inventory_column_id_order = ['node_relative_url', 'resource_relative_url', 'variation_text']
inventory_parameter_id_order = ['node', 'resource', 'variation_text']
for inventory_line in inventory_list:
  inventory_key = tuple([inventory_line[x] for x in inventory_column_id_order])
  inventory_dict[inventory_key] = inventory_line['inventory']

def getCurrentInventory(**criterion_dict):
  inventory_key = tuple([criterion_dict[x] for x in inventory_parameter_id_order])
  return inventory_dict.get(inventory_key, 0)

for line in line_list :
  line_resource = line.getResource()
  # The source can be different for every line (due to getBaobabSource approach)
  if source is None:
    source_counter = line.getBaobabSource()
  else:
    source_counter = source
  # Make sure there is no reindex with the tag of this counter
  if not serialize_dict.has_key(source_counter):
    serialize_dict[source_counter] = 1
    if source_counter is None:
      msg = Message(domain="ui", message="No source counter define to check inventory.")
      raise ValidationFailed(msg,)
    #context.log("CashDelivery_checkCounterInventory", "source_counter = %s" %source_counter)
    source_object = context.portal_categories.getCategoryValue(source_counter)
    source_object.serialize()
    checkActivities(source_counter)
  # Reindex this line with this particular source_counter tag
  activate_kw = {'tag':source_counter}
  line.reindexObject(activate_kw=activate_kw)
  if line.hasCellContent() :
    for cell in line.objectValues() :
      variation_text = cell.getVariationText()
      #context.log('check cell : ', str((source_counter, line_resource, variation_text)))
      inventory_value = getCurrentInventory(node=source_counter, resource = line_resource,
          variation_text = variation_text)
      #context.log('cell quantity', cell.getQuantity())
      #context.log('inventory value', inventory_value)
      if inventory_value - cell.getQuantity() < 0:
        msg = Message(domain='ui',
                      message='Insufficient balance for $resource, letter $letter, status $status and variation $variation',
                      mapping={'resource':cell.getResourceTranslatedTitle(),
                               'letter': cell.getEmissionLetterTitle(),
                               'status': cell.getCashStatusTranslatedTitle(),
                               'variation':cell.getVariationTitle()})
        raise ValidationFailed(msg,)
  else :
    raise ValueError('This script must not be used on movements without cells. It is deprecated and dangerous, therefor it raises.')
#    inventory_value = context.portal_simulation.getCurrentInventory(section=source_counter, resource=line_resource)
#    if inventory_value - line.getQuantity() < 0 :
#      msg = Message(domain='ui', message='Insufficient balance for $resource, letter $letter, status $status and variation $variation', mapping={'resource':line.getResourceTranslatedTitle(),
#                                                                                                                      'letter': line.getEmissionLetterTitle(),
#                                                                                                                      'status': line.getCashStatusTranslatedTitle(),
#                                                                                                                      'variation':line.getVariationTitle()})
#      raise ValidationFailed, (msg,)
  
return 0

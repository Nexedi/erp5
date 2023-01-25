"""Returns inventory list for resource scaled for chart

Needs from_date and at_date to know time size.

Uses sampling_amount, defaults to 20.

Samples inventory by proper differency, returns
sampling_amount inventory lines, sorted by date.
"""

# XXX: Might be set in preferences
sampling_amount = kwargs.get('sampling_amount',20)

from DateTime import DateTime

resource = context
portal = context.getPortalObject()

node = portal.restrictedTraverse(kwargs.get('node'))
from_date = kwargs.get('from_date')
at_date = kwargs.get('at_date')
variation_list = kwargs.get('variation_list')
variation_text = ''

if variation_list is not None and len(variation_list) > 0:
  # imitate behaviour from VariatedMixin.getVariationText
  # to create text
  variation_list.sort()
  variation_text = '\n'.join(variation_list)

if from_date is None or at_date is None or node is None:
  return []

# Lower by one, to be include from_date and at_date
sampling_delta = ( DateTime(at_date) - DateTime(from_date) ) / (sampling_amount - 1)

common_kw = {}
common_kw.update(
  node_uid = node.getUid(),
  sort_on = (('stock.date','desc'),),
  variation_text = variation_text,
)

inventory_tuple_list = []

precise_time_format = '%Y/%m/%d %H:%M.%S'
base_time_format = precise_time_format
# XXX: Below performance issues:
#  * sampling made in dumb way - it shall use SQL
#  * inventory is invoked 3 times for each sample
for i in range(0,sampling_amount):
  this_date = DateTime(from_date + sampling_delta * i)
  formatted_date = this_date.strftime(base_time_format)
  internal_tuple = (
    formatted_date,
    resource.getCurrentInventory(
      at_date = this_date,
      **common_kw
    ),
    resource.getAvailableInventory(
      at_date = this_date,
      **common_kw
    ),
    resource.getFutureInventory(
      at_date = this_date,
      **common_kw
    ),
  )
  inventory_tuple_list.append(internal_tuple)

return_list = []
for a in range(0, len(inventory_tuple_list)):
  data = inventory_tuple_list[a]
  return_list.append(
      portal.newContent(
          portal_type='Amount',
          temp_object=True,
          id=str(a),
          title='title %s'%(a,),
          date=data[0],
          current=data[1],
          available=data[2],
          future=data[3],))
return return_list

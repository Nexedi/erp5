if context.hasCellContent():
  for movement in context.getMovementList():
    movement.DeliveryLine_createItemGenerateReference(type=type)

import random

def generateReference():
  random_min = 100000000  # 9 digits
  random_max = 1000000000  # 10 digits

  new_id = context.portal_ids.generateNewLengthId(
    id_group="item_reference",  # XXX: isn't that id_group not too vauge?!
    default=1)

  return "%s-%s" % (new_id, random.randint(random_min,random_max))

listbox = []

# Make sure number of items is same as quantity
item_list = context.getAggregateValueList(portal_type="Item")
quantity = context.getQuantity()

remaining_quantity = quantity - len(item_list)

# Generate items
listbox = []
num = 0
while remaining_quantity > 0.:
  # XXX: Shouldn't it be in Item_init script?
  reference = generateReference()
  title = "%s %s %s %s %s" % (context.getResourceTitle(), 
                          context.getResourceReference(),
                          context.getSizeTitle() or '', 
                          context.getVariationTitle() or '', 
                          reference)
  listbox.append({
    'listbox_key': str(num),
    'title': title,
    'reference': reference,
    'quantity': 1.0,  # XXX: Hardcoded resource.base_quantity_unit
  })
  remaining_quantity -= 1
return context.DeliveryLine_createItemList(form_id=form_id, dialog_id=dialog_id, type=type, listbox=listbox, *args, **kwargs)

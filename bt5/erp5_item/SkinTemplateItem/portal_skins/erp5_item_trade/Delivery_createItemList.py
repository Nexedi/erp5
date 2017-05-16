"""
  This script generates one Item per delivery line with
  a title set to the product title, reference and variation, 

  Reference is setted via Item_setReference.

  TODO:
  - make title and variation handling generic
  - consider generating description
  - handle different Item types
"""

import random

def generateReference():
  random_min = 100000000  # 9 digits
  random_max = 1000000000  # 10 digits

  new_id = context.portal_ids.generateNewLengthId(
    id_group="item_reference",  # XXX: isn't that id_group not too vauge?!
    default=1)

  return "%s-%s" % (new_id, random.randint(random_min,random_max))

# Make sure every movement has a reference and associated items
for movement in context.getMovementList():

  # Make sure number of items is same as quantity
  item_list = movement.getAggregateValueList(portal_type="Item")
  quantity = movement.getQuantity()

  remaining_quantity = quantity - len(item_list)

  # Generate items
  listbox = []
  num = 0
  while remaining_quantity > 0.:
    # XXX: Shouldn't it be in Item_init script?
    reference = generateReference()
    title = "%s %s %s %s %s" % (movement.getResourceTitle(), 
                            movement.getResourceReference(),
                            movement.getSizeTitle() or '', 
                            movement.getVariationTitle() or '', 
                            reference)
    listbox.append({
      'listbox_key': str(num),
      'title': title,
      'reference': reference,
      'quantity': 1.0  # XXX: Hardcoded resource.base_quantity_unit
    })
    remaining_quantity -= 1
  movement.DeliveryLine_createItemList(type='Item', listbox=listbox)

if not batch_mode:
  message = context.Base_translateString('Items generated.')
  return context.Base_redirect(form_id,
          keep_items=dict(portal_status_message=message))

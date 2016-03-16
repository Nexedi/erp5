""" Retrieve the movement list of the transaction. """
movement_list = []

sub = context.restrictedTraverse(context_document)
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":
  sub = sub.getParentValue()

im = sub.Base_getRelatedObjectList(portal_type='Integration Module')[0].getObject()
#prod_module = im.getParentValue().product_module
#prod_pub = prod_module.getSourceSectionValue()

# getter and corresponding property (the order is important)
getter_tuple_list = [
    ('getTitle', 'title'),
    ('getReference', 'reference'),
    ('getSourceDebit', 'debit_price'),
    ('getSourceCredit', 'price'),
]

# browse the movement list, build the element to sort and movement's data
for movement in context.getMovementList():
  movement_dict = {
      'title': None,
      'reference': None,
      'price': None,
  }
  property_list = []
  # browse the main element of the movement
  for getter, key in getter_tuple_list:
    # XXX-Aurel : maybe there is better way to know if it is a cell
    if 'Cell' in movement.getPortalType() and \
        getter in ['getTitle', 'getReference']:
      value = getattr(movement.getParentValue(), getter)()
    else:
      value = getattr(movement, getter)()
      if value is not None:
        if getter == 'getSourceDebit':
          value = '%.2f' % value
        elif getter == 'getSourceCredit':
          value = '%.2f' % value    
    if value is not None and value != 0:
      movement_dict[key] = value
      property_list.append(value)

  if "price" in movement_dict.keys() and "debit_price" in movement_dict.keys():
    movement_dict["price"] = '%.2f' % (float(movement_dict["price"]) - float(movement_dict["debit_price"]))
  movement_list.append(movement_dict)
  # to not interfer with the sort, set to the end the object
  movement_dict['object'] = movement
  context.log(movement_dict)

#movement_list.sort()
return movement_list

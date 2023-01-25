""" Retrieve the movement list of the transaction. """
movement_list = []

sub = context.restrictedTraverse(context_document)
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":
  sub = sub.getParentValue()

im = sub.Base_getRelatedObjectList(portal_type='Integration Module')[0].getObject()
prod_module = im.getParentValue().product_module
prod_pub = prod_module.getSourceSectionValue()

# getter and corresponding property (the order is important)
getter_tuple_list = [
    ('getTitle', 'title'),
    ('fake_getGid', 'resource'),
    ('getReference', 'reference'),
    ('getQuantity', 'quantity'),
    ('getPrice', 'price'),
]

# browse the movement list, build the element to sort and movement's data
for movement in context.getMovementList():
  movement_dict = {
      'title': None,
      'resource': None,
      'reference': None,
      'quantity': None,
      'price': None,
      'VAT' : None,
  }
  property_list = []

  # browse the main element of the movement
  for getter, key in getter_tuple_list:
    if getter == 'fake_getGid':
      value = prod_pub.getGidFromObject(object=movement.getResourceValue(), encoded=False)
    else:
      # XXX-Aurel : maybe there is better way to know if it is a cell
      if 'Cell' in movement.getPortalType() and \
          getter in ['getTitle', 'getReference']:
        value = getattr(movement.getParentValue(), getter)()
      else:
        value = getattr(movement, getter)()
        if value is not None:
          if getter == 'getPrice':
            value = '%.6f' % value
          elif getter == 'getQuantity':
            value = '%.2f' % value

    if value is not None:
      movement_dict[key] = value
      property_list.append(value)

  # set the variations of the movement in another list, it's using by the sort
  variation_list = []
  if movement.getBaseContributionValue() is not None:
    movement_dict['VAT'] = movement.getBaseContribution().split('/')[-1]

  variation_list = movement.getVariationCategoryList()
  variation_list.sort()
  movement_list.append(movement_dict)
  # to not interfer with the sort, set to the end the object
  movement_dict['object'] = movement
  movement_dict['variation_list'] = variation_list


def cmp_resource(a,b):
  a_str = "%s %s %s" %(a['resource'], a['title'], ' '.join(a['variation_list']))
  b_str = "%s %s %s" %(b['resource'], b['title'], ' '.join(b['variation_list']))
  return cmp(a_str, b_str)

movement_list.sort(cmp=cmp_resource)

return movement_list

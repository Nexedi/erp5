## Script (Python) "transformation_getAggregatedList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=request=None
##title=
##
from Products.ERP5.XML.Base import Base
return "toto"

# Example code:
transformation_list = [context] + context.getSpecialiseValueList()
if request is None: request = {'categories': ('taille/enfant/08 ans','coloris/modele/701C402/2')}
result = []
price = 0.0
duration = 0.0

for transformation in transformation_list:
  for t in transformation.objectValues():
    variation_category_list = []
    quantity = t.getQuantity()
    r = t.getDefaultResourceValue()
    unit_price = 0.0
    item_duration = 0.0
    if r.hasDefaultBasePrice():
      unit_price = r.getBasePrice()
    else:
      item_duration = t.quantity
    # Start filing the value holder
    line_item = Base()
    line_item.edit(
        resource_id = r.getId(),
        resource_url = r.getRelativeUrl(),
        transformation_id = transformation.getId(),
        transformation_url = transformation.getRelativeUrl(),
        transformed_resource_id =  t.getId(),
        transformed_resource_description =  t.getDescription(),
        unit = t.getQuantityUnit(),
        duration = item_duration,
        quantity = quantity,
        price = unit_price,
        total_price = 0.0
      )
    # Add variable values
    for c in t.objectValues():
      if c.test(request):
        #v = self.restrictedTraverse()
        #if c.hasDefaultBasePrice():
        #  variation_unit_price = r.getBasePrice()
        # Upgrade the request with the variation values
        for a in c.getDomainDomainPropertyList():
          kw = {}
          kw[a] = c.get(a)
          line_item.edit(**kw)
        bc_list = []
        for bc in c.getDomainBaseCategoryList():
          self.portal_categories.setCategoryMembership(line_item, bc, c.getCategoryMembershipList(bc))
          bc_list += [bc]
        # Update the price
        if len(bc_list) > 0:
          for variation in c.getValueList(bc_list, portal_type=('Variante Tissu',)):
            if variation.hasDefaultBasePrice():
              new_price = variation.getBasePrice()
              if new_price > 0.0:
                unit_price = new_price
    # Calculate total
    line_item.price = unit_price
    line_item.total_price = quantity * unit_price
    result += [line_item]
    price += total_price
    duration += item_duration


#return result

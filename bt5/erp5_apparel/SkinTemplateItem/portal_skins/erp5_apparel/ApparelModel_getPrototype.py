'''
  return the first coulour variation that have prototype property set to True
  return None if no prototype is found
'''

colour_variation_list = context.contentValues(portal_type='Apparel Model Colour Variation')
prototype_list = [x for x in colour_variation_list if x.isPrototype()]
if len(prototype_list):
  return prototype_list[0]
return None

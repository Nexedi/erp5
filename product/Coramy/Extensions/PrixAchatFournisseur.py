##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the Zope Public License (ZPL) Version 2.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

source_price_dict = {}

def getSupplierPrice(self) :
  """
    Add as extension Amount_getSupplierPrice

    self      --      an amount (movement, delivery line, etc.)
  """
  try :
    coloris = self.getColoris()
  except :
    coloris = None
  try :
    variante = self.getVariante()
  except :
    variante = None
  try :
    resource = self.getResource()
    resource_value = self.getResourceValue()
  except :
    resource = None
    resource_value = None

  if resource_value is None:
    return 0
  else :
    # source price is defined on resource or on variation
    predicate_value = []
    if resource_value is not None :
      base_category_list = resource_value.getVariationBaseCategoryList()
      if 'coloris' in base_category_list and coloris :
        predicate_value.append('coloris/'+coloris)
      if 'variante' in base_category_list and variante :
        predicate_value.append('variante/'+variante)
    predicate_value.sort()
    key = tuple([resource] + predicate_value)
    if source_price_dict.has_key(key):
      return source_price_dict[key] # This is an infinite cache

  # Build cache    
  if resource_value is not None :
    supplier_price = resource_value.getSourceBasePrice()
    variation_list = resource_value.contentValues(filter={'portal_type':['Variante Tissu','Variante Composant']})
    if supplier_price is None :
      supplier_price = 0
    root_supplier_price = supplier_price
    priced_quantity = resource_value.getPricedQuantity()
    if priced_quantity not in (None, 0, 1) :
      supplier_price = supplier_price / priced_quantity 
    new_key = tuple([resource])
    source_price_dict[new_key] = supplier_price
    # Fill the cache
    for variation in variation_list:
      if variation.getSourceBasePrice() not in (None, 0) :
        supplier_price = variation.getSourceBasePrice()
      else :
        supplier_price = root_supplier_price
      if variation.getPortalType() == 'Variante Tissu' :
        predicate_value = ['coloris/' + variation.getRelativeUrl()]
      elif variation.getPortalType() == 'Variante Composant' :
        predicate_value = ['variante/' + variation.getRelativeUrl()]
      else :
        prediacte_value = []
      if priced_quantity not in (None, 0, 1) :
        supplier_price = supplier_price / priced_quantity
      new_key = tuple([resource] + predicate_value)
      source_price_dict[new_key] = supplier_price
  else :
    return 0

  if source_price_dict.has_key(key):
    return source_price_dict[key]

  return 0

def getSupplierPriceKeyList():
  return str(source_price_dict.keys())

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

pri_dict = {}

def getPri(self) :
  """
    Add as extension Amount_getPri

    self      --      an amount (movement, delivery line, etc.)
  """
  coloris = self.getColoris()
  taille = self.getTaille()
  morphologie = self.getMorphologie()
  resource = self.getResource()
  resource_value = self.getResourceValue()

  if resource_value is None:
    return 0
  else :
    # pri is defined on each resource
    predicate_value = []
    if resource_value is not None :
      base_category_list = resource_value.getVariationBaseCategoryList()
      if 'coloris' in base_category_list and coloris :
        predicate_value.append('coloris/'+coloris)
      if 'taille' in base_category_list and taille :
        predicate_value.append('taille/'+taille)
    predicate_value.sort()
    key = tuple([resource] + predicate_value)
    if pri_dict.has_key(key):
      return pri_dict[key] # This is an infinite cache

  # Build cache    
  if resource_value is not None :
    mapped_value_list = resource_value.contentValues(filter={'portal_type':'Set Mapped Value'})
    # Fill the cache
    for cell in mapped_value_list:
      predicate_value = []
      for predicate_value_item in cell.getPredicateValueList():
        if predicate_value_item <> 'value' :
          predicate_value.append(predicate_value_item)
      predicate_value.sort()
      new_key = tuple([resource] + predicate_value)
      pri_dict[new_key] = cell.getProperty(key='pri')
  else :
    return 0

  if pri_dict.has_key(key):
    return pri_dict[key]

  return 0

def getPriKeyList():
  return str(pri_dict.keys())

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

code_modele_client = {}

def getCodeModeleClient(self) :
  """
    Add as extension Amount_getCodeModeleClient

    self      --      an amount (movement, delivery line, etc.)
  """
  coloris = self.getColoris()
  taille = self.getTaille()
  morphologie = self.getMorphologie()
  resource = self.getResource()
  resource_value = self.getResourceValue()

  if resource_value is None:
    return ''
  else :
    variated_reference_list = resource_value.contentValues(filter={'portal_type':'Variated Reference'})
    # we search a variated_reference wich define 'code_modele'
    my_variated_reference = None
    for variated_reference in variated_reference_list :
      if len(variated_reference.getMappedValuePropertyList()) <> 0 :
        if variated_reference.getMappedValuePropertyList()[0] == 'code_modele' :
          my_variated_reference = variated_reference
          break

    predicate_value = []
    if my_variated_reference is not None :
      base_category_list = my_variated_reference.getVariationBaseCategoryList()
      if 'coloris' in base_category_list and coloris :
        predicate_value.append('coloris/'+coloris)
      if 'taille' in base_category_list and taille :
        predicate_value.append('taille/'+taille)
      if 'morphologie' in base_category_list and morphologie :
        predicate_value.append('morphologie/'+morphologie)
    predicate_value.sort()
    key = tuple([resource] + predicate_value)
    if code_modele_client.has_key(key):
      return code_modele_client[key] # This is an infinite cache

  # Build cache    
  if my_variated_reference is not None :
    mapped_value_list = my_variated_reference.objectValues()
    # Fill the cache
    for cell in mapped_value_list:
      predicate_value = []
      for predicate_value_item in cell.getPredicateValueList():
        if predicate_value_item <> 'value' :
          predicate_value.append(predicate_value_item)
      predicate_value.sort()
      new_key = tuple([resource] + predicate_value)
      code_modele_client[new_key] = cell.getProperty(key='code_modele')
  else :
    return resource_value.getDestinationReference('')

  if code_modele_client.has_key(key):
    return code_modele_client[key]

  return resource_value.getDestinationReference('')

def getCodeModeleClientKeyList():
  return str(code_modele_client.keys())

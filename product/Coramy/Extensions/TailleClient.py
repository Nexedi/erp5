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

taille_client = {}

def getTailleClient(self) :
  """
    Add as extension Amount_getTailleClient

    self      --      an amount (movement, delivery line, etc.)
  """
  coloris = self.getColoris()
  taille = self.getTaille()
  morphologie = self.getMorphologie()
  resource = self.getResource()
  resource_value = self.getResourceValue()
  try :
    morpho_type = self.getMorphologieValue().getMorphoType()
  except :
    morpho_type = None

  if resource_value is None:
    return taille.split('/')[-1]
  else :
    correspondance_taille = resource_value.getSpecialiseValue(portal_type=['Correspondance Tailles'])
    predicate_value = []
    if correspondance_taille is not None:
      if len(correspondance_taille.getTailleList())>0 and taille :
        predicate_value.append(taille)
      if len(correspondance_taille.getMorphoTypeList())>0 and morphologie :
        predicate_value.append(morpho_type)
    predicate_value.sort()
    key = tuple([resource] + predicate_value)
    if taille_client.has_key(key):
      return taille_client[key] # This is an infinite cache

  # Build cache
  if correspondance_taille is not None:
    mapped_value_list = correspondance_taille.objectValues()
    # Fill the cache
    for cell in mapped_value_list:
      predicate_value = []
      for predicate_value_item in cell.getPredicateValueList():
        if predicate_value_item <> 'value' :
          predicate_value.append(predicate_value_item)
      predicate_value.sort()
      new_key = tuple([resource] + predicate_value)
      taille_client[new_key] = cell.getProperty(key='taille_client')
  else :
    return taille.split('/')[-1]

  if taille_client.has_key(key):
    return taille_client[key]

  return taille.split('/')[-1]

def getTailleClientKeyList():
  return str(taille_client.keys())

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
  taille = self.getTaille()
  morphologie = self.getMorphologie()
  resource = self.getResource()
  resource_value = self.getResourceValue()
  try :
    morpho_type = self.getMorphologieValue().getMorphoType()
  except :
    morpho_type = None

  predicate_value = []
  for predicate_item in (taille, morpho_type):
    if predicate_item:
      predicate_value.append(predicate_item)
  predicate_value.sort()
  key = tuple([resource] + predicate_value)
  if taille_client.has_key(key):
    return taille_client[key] # This is an infinite cache

  # Build cache

  if resource_value is None:
    return taille.split('/')[-1]

  correspondance_taille = resource_value.getSpecialiseValue(portal_type=['Correspondance Tailles'])
  if correspondance_taille is None:
    return taille.split('/')[-1]

  # Fill the cache
  for cell in correspondance_taille.objectValues():
    predicate_value = list(cell.getPredicateValueList())
    predicate_value.sort()
    new_key = tuple([resource] + predicate_value)
    taille_client[new_key] = cell.getProperty(key='taille_client')

  if taille_client.has_key(key):
    return taille_client[key]

  return taille.split('/')[-1]

def getTailleClientKeyList():
  return str(taille_client.keys())

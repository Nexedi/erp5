##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

"""
    Converts ERP5 Set Mapped Value to Coramy SetMappedValue.
"""

# Source
import Products.ERP5.Document.SetMappedValue

# Destination
import Products.Coramy.Document.SetMappedValue

#
import re
from zLOG import LOG

##################################################################################
# This is a set of methods in order to upgrade ERP5 Mapped Value to Coramy's one #
##################################################################################

def test_before(object):
  return 1

def test_after(object):

  message = None
  # check if aq_base content the attribute 'quantity' is a float
  if hasattr(object, 'quantity'):
    quantity = object.getQuantity()
    if type(quantity) is not type(0.0):
      message = 'object is now a %s but XXX quantity is not a float XXX' % object.__class__

  # if it's a variation, check if there's a definition of color and colory

  if message is None:
    message = 'object is now a %s' % object.__class__
  return [(object.getRelativeUrl(), 'upgradeSetMappedValue',102,message)]

def upgradeSetMappedValue(REQUEST):
    """
        Folder needs to be updated in order to take into account
        changes of classes and in particular meta_type
    """
    #portal_root = getToolByName(self, 'portal_url').getPortalObject()
    container = REQUEST.PARENTS[0]
    from_class = Products.ERP5.Document.SetMappedValue.SetMappedValue
    to_class = Products.Coramy.Document.SetMappedValue.SetMappedValue
    return container.upgradeObjectClass(test_before=test_before, from_class=from_class,\
      to_class=to_class, test_after=test_after)

##################################################################################
# This is a set of methods in order to update default_base_price to base_price   #
##################################################################################

def filter_base_price(object):
  object = object.aq_base
  #if object.id!='K4011':
  #  return None
  if getattr(object, 'default_base_price', 0.0)!=0.0 and getattr(object, 'base_price',None)==None:
    return 1
  elif getattr(object, 'default_additionnal_base_price',0.0)!=0.0 and getattr(object, 'additionnal_base_price',None)==None:
    return 1
  else:
    return None

def test_after_base_price(object):
  base_object = object.aq_base
  message = None
  result = []
  if getattr(base_object, 'base_price',0.0)!=0.0:
    message = 'object have now an base_price : %s' % str(getattr(base_object,'base_price'))
    result += [(object.getRelativeUrl(), 'upgradeDefaultBasePrice',102,message)]
  if getattr(base_object, 'additional_price',0.0)!=0.0:
    message = 'object have now an additional_price : %s' % \
               str(getattr(base_object,'additional_price'))
    result += [(object.getRelativeUrl(), 'upgradeDefaultBasePrice',102,message)]
  return result

def method_base_price(object):
  object = object.aq_base
  default_base_price = getattr(object, 'default_base_price', 0.0)
  if  default_base_price != 0.0:
    setattr(object, 'base_price', default_base_price)
  default_additional_price = getattr(object, 'default_additional_price', 0.0)
  if  default_additional_price != 0.0:
    setattr(object, 'additional_price', default_additional_price)

def upgradeDefaultBasePrice(REQUEST):
    """
        Folder needs to be updated in order to take into account
        changes of classes and in particular meta_type
    """
    container = REQUEST.PARENTS[0]
    return container.updateAll(filter=filter_base_price, method=method_base_price,
                               test_after=test_after_base_price)

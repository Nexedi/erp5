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

def filterUpdateQuantityUnit(object=None,request=None,**kw):
  if object.getPortalType() <> 'Inventory MP' :
    return 1
  else :
    return 0

def testAfterUpdateQuantityUnit(object=None,request=None,**kw):
  result = []
  return result

def methodUpdateQuantityUnit(object=None,request=None,**kw):
  result = []
  try:
    object.setQuantityUnit('Unite/Cone')
  except:
    message = 'Object could not be updated'
    if hasattr(object,'getRelativeUrl'):
      result.append((object.getRelativeUrl(), 'methodUpdateQuantityUnit',101,message))
    elif hasattr(object,'id'):
      result.append((object.id, 'methodUpdateQuantityUnit',101,message))
    else:
      result.append(('Object with no id', 'methodUpdateQuantityUnit',101,message))
  return result

def UpdateQuantityUnit(object=None,request=None,**kw):
    """
        Folder needs to be updated in order to take into account
        changes of classes and in particular meta_type
    """
    #container = REQUEST.PARENTS[0]
    result = []
    container = object
    if hasattr(container,'updateAll'):
      result += container.updateAll(filter=filterUpdateQuantityUnit, method=methodUpdateQuantityUnit,
                                test_after=testAfterUpdateQuantityUnit,request=request)
    else:
      #for folder in container.objectValues(("ERP5 Folder",)):
      for object in container.objectValues():
        if hasattr(object,'updateAll'):
          result += object.updateAll(filter=filterUpdateQuantityUnit, method=methodUpdateQuantityUnit,
                                test_after=testAfterUpdateQuantityUnit,request=request)

    return result

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

from Acquisition import aq_base

def filterReindexAll(object=None,request=None,**kw):
  return 1

def testAfterReindexAll(object=None,request=None,**kw):
  result = []
  try:
    result.append((object.getRelativeUrl(), 'portal_type',1,object.getPortalType()))
  except:
    message = 'Could not find the portal type'
    if hasattr(object,'getRelativeUrl'):
      result.append((object.getRelativeUrl(), 'testAfterReindexAll',101,message))
    elif hasattr(object,'id'):
      result.append((object.id, 'testAfterReindexAll',101,message))
    else:
      result.append(('Object with no id', 'testAfterReindexAll',101,message))
  return result

def methodReindexAll(object,REQUEST=None,**kw):
  result = []
  try:
    object.portal_catalog.catalog_object(object,None)
    #object.reindexObject()
  except:
    message = 'Object could not be catalogued'
    if hasattr(object,'getRelativeUrl'):
      result.append((object.getRelativeUrl(), 'methodReindexAll',101,message))
    elif hasattr(object,'id'):
      result.append((object.id, 'methodReindexAll',101,message))
    else:
      result.append(('Object with no id', 'methodReindexAll',101,message))
  return result

def reindexAll(object=None,REQUEST=None,**kw):
    """
        Folder needs to be updated in order to take into account
        changes of classes and in particular meta_type
    """
    result = []
    container = object
    obase = aq_base(container)
    # Call recursiveApply only if this is an ERP5 Folder
    if hasattr(obase,'recursiveApply'):
      result += container.recursiveApply(filter=filterReindexAll, method=methodReindexAll,
                                test_after=testAfterReindexAll,REQUEST=REQUEST)
    # or if this is a folder, do it on contained objects
    elif hasattr(obase,'objectValues'):
      for object in container.objectValues():
        result += reindexAll(object=object, REQUEST=REQUEST, **kw)
    # else reindex
    else:
      result += methodReindexAll(object = container, REQUEST=REQUEST, **kw)

    return result

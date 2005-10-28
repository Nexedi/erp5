##############################################################################
#
# Copyright (c) 2002 Nexedi SARL. All Rights Reserved.
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import string
import Acquisition
import sys
from ZODB.POSException import ConflictError

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityInfo import allow_class

from zLOG import LOG

class  ZSQLBrain(Acquisition.Implicit):
  security = ClassSecurityInfo()
  security.declareObjectPublic()

  o_self = None

#   def __getattr__(self, key):
#     return "toto"
#     if hasattr(self, key):
#       return self.__dict__[key]
#     elif hasattr(ZSQLBrain, key):
#       return ZSQLBrain.__dict__[key]
#     else:
#       if self.o_self is None:
#         self.o_self = self.getObject()
#       if self.o_self is not None:
#         try:
#           result = self.o_self.getProperty(key)
#           self.__dict__[key] = result
#         except:
#           result = 'Can not evaluate attribute: %s' % cname_id
#       else:
#           result = 'Object does not exist'
#       return result

  def getURL(self):
    return self.path

  def getUrl(self):
    return self.path

  def getPath(self):
    return self.path

  def getUid(self):
    return self.uid

  getRID = getUid

  def getObject(self, REQUEST=None):
    """Try to return the object for this record"""
    try:
      obj = self.aq_parent.unrestrictedTraverse(self.getPath())
      if obj is None:
        if REQUEST is None:
          REQUEST = self.REQUEST
        obj = self.aq_parent.portal_catalog.resolve_url(self.getPath(), REQUEST)
      return obj
    except ConflictError:
      raise
    except:
      LOG("ZCatalog WARNING",0,"Could not access object path %s" % self.getPath(), error=sys.exc_info() )
      return None

  def absolute_url(self):
    """
      returns the path stored in the Catalog
    """
    return self.path

  def resolve_url(self, path, REQUEST):
    """
      Taken from ZCatalog

      Attempt to resolve a url into an object in the Zope
      namespace. The url may be absolute or a catalog path
      style url. If no object is found, None is returned.
      No exceptions are raised.
    """
    script=REQUEST.script
    if string.find(path, script) != 0:
      path='%s/%s' % (script, path)
    try:
      return REQUEST.resolve_url(path)
    except ConflictError:
      raise
    except:
      pass

allow_class(ZSQLBrain)

##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.CMFCore.TypesTool import TypesTool as CMFCoreTypesTool
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type import Permissions
from Acquisition import aq_base


class TypesTool(BaseTool, CMFCoreTypesTool):
  """
      EXPERIMENTAL - DO NOT USE THIS PROPERTYSHEET BESIDES R&D
  """

  id = 'portal_types'
  meta_type = 'ERP5 Types Tool'
  portal_type = 'Types Tool'
  allowed_types = ()
  security = ClassSecurityInfo()

  def getTypeInfo(self, *args):
    if not len(args): 
       return BaseTool.getTypeInfo(self)
    else:
      # The next 10 lines are taken from CMFCore
      # which means that the entire file is ZPLed
      # for now
      contentType = args[0]
      #return CMFCoreTypesTool.getTypeInfo(self, contentType)
      if not isinstance(contentType, basestring):
          if hasattr(aq_base(contentType), 'getPortalTypeName'):
              contentType = contentType.getPortalTypeName()
              if contentType is None:
                  return None
          else:
              return None
      #ob = getattr( self, contentType, None )
      ob = self._getOb(contentType, None)
      if getattr(aq_base(ob), '_isTypeInformation', 0):
          return ob
      else:
          return None

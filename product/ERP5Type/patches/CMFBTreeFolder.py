##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

#from Products.CMFCore.PortalFolder import PortalFolder
#from Products.CMFCore.PortalFolder import PortalFolder
try:
  from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
except ImportError:
  from Products.BTreeFolder2.CMFBTreeFolder import CMFBTreeFolder
from Products.CMFCore.utils import getToolByName

"""
  This patch tries to give only portal types that are defined
  in the allowed content types field. This will make the
  speed of allowed content type in almost O(1) instead of O(n),
  where n is the number of portal types in types tool.
"""

def CMFBTreeFolder_allowedContentTypes(self):
  """
      List type info objects for types which can be added in
      this folder.
  """
  result = []
  portal_types = getToolByName(self, 'portal_types')
  myType = portal_types.getTypeInfo(self)

  if myType is not None:
    allowed_types_to_check = []
    if myType.filter_content_types:
      for portal_type in myType.allowed_content_types:
        contentType = portal_types.getTypeInfo(portal_type)
        if contentType is None:
          raise AttributeError, "Portal type '%s' does not exist " \
                                "and should not be allowed in '%s'" % \
                                (portal_type, self.getPortalType())
        result.append(contentType)
    else:
      for contentType in portal_types.listTypeInfo(self):
        if myType.allowType(contentType.getId()):
          result.append(contentType)
  else:
      result = portal_types.listTypeInfo()

  return filter(
      lambda typ, container=self: typ.isConstructionAllowed(container),
      result)

CMFBTreeFolder.allowedContentTypes = CMFBTreeFolder_allowedContentTypes

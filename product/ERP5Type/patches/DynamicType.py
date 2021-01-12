##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Products.CMFCore.DynamicType import DynamicType
from zope.component import queryUtility 
from Products.CMFCore.interfaces import ITypesTool

def getTypeInfo(self):
    """ Get the TypeInformation object specified by the portal type.
    """
    
    tool = queryUtility(ITypesTool)
    if tool is None:
        # <patch>
        assert getattr(self.getPortalObject(), "portal_types", None) is None
        return None
        # </patch>
    return tool.getTypeInfo(self)  # Can return None.

DynamicType.getTypeInfo = getTypeInfo

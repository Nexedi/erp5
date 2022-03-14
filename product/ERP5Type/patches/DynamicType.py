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

def getTypeInfo(self):
    """ Get the TypeInformation object specified by the portal type.
    """
    # <patch>
    tool = getattr(self.getPortalObject(), "portal_types", None)
    # </patch>
    if tool is None:
        return None
    return tool.getTypeInfo(self)  # Can return None.

DynamicType.getTypeInfo = getTypeInfo

##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from OFS.PropertySheets import DAVProperties
from webdav.common import isDavCollection
from Acquisition import aq_base

# This is required to make an ERP5 Document (folderish) look like a file (non folderish)
def DAVProperties_dav__resourcetype(self):
    vself = self.v_self()
    if getattr(vself, 'isDocument', None): return '' # This is the patch
    if (isDavCollection(vself) or
        getattr(aq_base(vself), 'isAnObjectManager', None)):
        return '<n:collection/>'
    return ''

DAVProperties.dav__resourcetype = DAVProperties_dav__resourcetype

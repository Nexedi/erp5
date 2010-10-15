##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# CMFCatalogAware patch for accepting arbitrary parameters.

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

def reindexObject(self, idxs=[], *args, **kw):
    """
        Reindex the object in the portal catalog.
        If idxs is present, only those indexes are reindexed.
        The metadata is always updated.

        Also update the modification date of the object,
        unless specific indexes were requested.
    """
    if idxs == []:
        # Update the modification date.
        if getattr(aq_base(self), 'notifyModified', None) is not None:
            self.notifyModified()
    catalog = getToolByName(self, 'portal_catalog', None)
    if catalog is not None:
        catalog.reindexObject(self, idxs=idxs, *args, **kw)

CMFCatalogAware.reindexObject = reindexObject

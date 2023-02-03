##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from OFS.Folder import Folder
from OFS.SimpleItem import Item
from Products.ERP5Type import Permissions

"""
  This patch modifies OFS.Folder._setOb to update portal_skins cache when
  needed.
"""

Folder_original__setOb = Folder._setOb

def Folder_setOb(self, id, object):
  """
    Update portal_skins cache with the new files.

    Checks must be done from the quickest to the slowest to avoid wasting
    time when no cache must be updated.

    Update must only be triggered if we (folder) are right below the skin
    tool, not any deeper.
  """
  Folder_original__setOb(self, id, object)
  aq_chain = getattr(self, 'aq_chain', None)
  if aq_chain is None: # Not in acquisition context
    return
  if len(aq_chain) < 2: # Acquisition context is not deep enough for context to possibly be below portal skins.
    return
  portal_skins = aq_chain[1]
  if getattr(portal_skins, 'meta_type', '') != 'CMF Skins Tool' : # It is not a skin tool we're below.
    return
  _updateCacheEntry = getattr(portal_skins.aq_base, '_updateCacheEntry', None)
  if _updateCacheEntry is None:
    return
  _updateCacheEntry(self.id, id)

Folder._setOb = Folder_setOb

def Folder_isERP5SitePresent(self):
  """ Return True if a ERP5 Site is present as subobject. This is
      usefull to identify if a erp5 is present already on a Zope
      Setup.
  """
  return len(self.objectIds("ERP5 Site")) > 0

Folder.isERP5SitePresent = Folder_isERP5SitePresent

security = ClassSecurityInfo()
security.declareProtected(Permissions.ManagePortal, 'isERP5SitePresent')
Folder.security = security
InitializeClass(Folder)

# restore __repr__ after persistent > 4.4
# https://github.com/zopefoundation/Zope/issues/379
Folder.__repr__ = Item.__repr__

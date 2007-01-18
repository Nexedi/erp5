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

from Products.CMFCore.SkinsTool import SkinsTool

"""
  This patch invalidates the skin cache when manage_skinLayers is called to
  modify the skin selection.
"""

original_manage_skinLayers = SkinsTool.manage_skinLayers

def CMFCoreSkinsTool_manage_skinLayers(self, chosen=(), add_skin=0, del_skin=0,
                                       skinname='', skinpath='', REQUEST=None):
  """
    Make sure cache is flushed when skin layers are modified.
  """
  if getattr(self, '_v_skin_location_list', None) is not None:
    self._p_changed = 1
    delattr(self, '_v_skin_location_list')
  return original_manage_skinLayers(self, chosen=chosen, add_skin=add_skin,
                                    del_skin=del_skin, skinname=skinname,
                                    skinpath=skinpath, REQUEST=REQUEST)

def CMFCoreSkinsTool__updateCacheEntry(self, container_id, object_id):
  """
    Actually, do not even try to update the cache smartly : it would only
    update the cache of the current thread. So just mark the object as
    modified (for other thread to refresh) and delete the cache (to force
    current thread to refresh too before future cache uses in the samle
    query).
  """
  if getattr(self, '_v_skin_location_list', None) is not None:
    self._p_changed = 1
    delattr(self, '_v_skin_location_list')

SkinsTool.manage_skinLayers = CMFCoreSkinsTool_manage_skinLayers
SkinsTool._updateCacheEntry = CMFCoreSkinsTool__updateCacheEntry


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

from six import string_types as basestring
from Products.CMFCore.SkinsTool import SkinsTool
import six

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
    Update skin cache.

    Goal
      We must update the cache in a CPU-efficient way.
    Problem
      We cannot synchronize caches from multiple threads.
      We must avoid generating the cache multiple times in the same
      transaction, so it must be updated whenever possible.
    Solution
      We mark the skin tool object as modified and we update the cache of
      current thread.
      This way, all threads will get a cache invalidation, but still current
      thread won't suffer from systematic complete cache recreation each time
      it must be updated.
      Also, if the transaction gets aborted the cache should be flushed, but only
      for the current thread. XXX: This is an unchecked assertion.
  """
  skin_location_list = getattr(self, '_v_skin_location_list', None)
  if skin_location_list is not None:
    self._p_changed = 1
    for selection_name in list(skin_location_list.keys()):
      if not isinstance(selection_name, basestring):
        del skin_location_list[selection_name]
    for selection_name, skin_folder_id_string in six.iteritems(self._getSelections()):
      # Add portal_callables to every selection
      skin_folder_id_list = skin_folder_id_string.split(',') + ['portal_callables']
      if container_id in skin_folder_id_list:
        skin_folder_id_list.reverse()
        this_folder_index = skin_folder_id_list.index(container_id)
        if object_id in skin_location_list[selection_name]:
          existing_folder_index = skin_folder_id_list.index(skin_location_list[selection_name][object_id])
        else:
          existing_folder_index = this_folder_index - 1
        if existing_folder_index < this_folder_index:
          skin_location_list[selection_name][object_id] = container_id

SkinsTool.manage_skinLayers = CMFCoreSkinsTool_manage_skinLayers
SkinsTool._updateCacheEntry = CMFCoreSkinsTool__updateCacheEntry


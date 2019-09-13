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

from Products.CMFCore import Skinnable
from Products.CMFCore.Skinnable import SKINDATA, SkinnableObjectManager

from thread import get_ident
from zLOG import LOG, WARNING, DEBUG
from Acquisition import aq_base

"""
  This patch modifies the way CMF Portal Skins gets a skin by its name from
  the right skin folder. This way, the access complexity is O(1), and not O(n)
  (n was the number of skin folders in skin selection list) any more.

  XXX: the resolve/ignore dicts used in
  CMFCoreSkinnableSkinnableObjectManager___getattr__
  implies that it's not possible to get skins from multiple skin selections
  during the same request.
"""

def _initializeCache(portal_callables, skin_tool, skin_folder_id_list):
    skin_list = {}
    for skin_folder_id in skin_folder_id_list[::-1]:
      try:
        skin_folder = getattr(skin_tool, skin_folder_id)
      except AttributeError:
        LOG(__name__, WARNING, 'Skin folder %s is in selection list'
                               ' but does not exist.' % skin_folder_id)
      else:
        skin_list.update(dict.fromkeys(skin_folder.objectIds(), skin_folder_id))
    # update skin_list with objects in portal_callables
    if portal_callables is not None:
      skin_list.update(dict.fromkeys(portal_callables.objectIds(), "portal_callables"))
    return skin_list

def CMFCoreSkinnableSkinnableObjectManager_initializeCache(self):
  '''
    Initialize the cache on portal skins.
  '''
  portal_skins = getattr(self, 'portal_skins', None)
  if portal_skins is None:
    return
  portal_skins = portal_skins.aq_base
  portal_callables = getattr(self, 'portal_callables', None)
  if portal_callables is not None:
    portal_callables = portal_callables.aq_base
  skin_selection_mapping = {}
  for selection_name, skin_folder_id_string in portal_skins._getSelections().iteritems():
    skin_selection_mapping[selection_name] = _initializeCache(portal_callables,
      portal_skins, skin_folder_id_string.split(','))
  portal_skins._v_skin_location_list = skin_selection_mapping
  return skin_selection_mapping

Skinnable.SkinnableObjectManager.initializeCache = CMFCoreSkinnableSkinnableObjectManager_initializeCache

def skinResolve(self, selection, name):
  try:
    portal_skins = aq_base(self.portal_skins)
  except AttributeError:
    raise AttributeError, name
  try:
    portal_callables = aq_base(self.portal_callables)
  except AttributeError:
    # backwards compatability for ERP5 sites without this tool
    portal_callables = None
  try:
    skin_selection_mapping = portal_skins._v_skin_location_list
    reset = False
  except AttributeError:
    LOG(__name__, DEBUG, 'Initial skin cache fill.'
        ' This should not happen often. Current thread id:%X' % get_ident())
    skin_selection_mapping = self.initializeCache()
    reset = True
  while True:
    try:
      skin_folder_id = skin_selection_mapping[selection][name]
    except KeyError:
      if selection in skin_selection_mapping or \
         isinstance(selection, basestring):
        return
      skin_list = portal_skins._getSelections()[selection[0]].split(',') \
                  + ['portal_callables']
      skin_selection_mapping[selection] = skin_list = _initializeCache(portal_callables,
        portal_skins, skin_list[1+skin_list.index(selection[1]):])
      try:
        skin_folder_id = skin_list[name]
      except KeyError:
        return
      reset = True
    try:
      if skin_folder_id == "portal_callables":
        return aq_base(getattr(aq_base(self.portal_callables), name))
      return aq_base(getattr(getattr(portal_skins, skin_folder_id), name))
    except AttributeError:
      if reset:
        return
      # We cannot find a document referenced in the cache, so reset it.
      skin_selection_mapping = self.initializeCache()
      reset = True

def CMFCoreSkinnableSkinnableObjectManager___getattr__(self, name):
  '''
    Looks for the name in an object with wrappers that only reach
    up to the root skins folder.
    This should be fast, flexible, and predictable.
  '''
  if name[:1] != '_' and name[:3] != 'aq_':
    skin_info = SKINDATA.get(get_ident())
    if skin_info is not None:
      _, skin_selection_name, ignore, resolve = skin_info
      try:
        return resolve[name]
      except KeyError:
        if name not in ignore:
          object = skinResolve(self, skin_selection_name, name)
          if object is not None:
            resolve[name] = object
            return object
          ignore[name] = None
  raise AttributeError(name)

def CMFCoreSkinnableSkinnableObjectManager_changeSkin(self, skinname, REQUEST=None):
  '''
    Change the current skin.

    Can be called manually, allowing the user to change
    skins in the middle of a request.

    Patched not to call getSkin.
  '''
  if skinname is None:
    sf = getattr(self, "portal_skins", None)
    if sf is not None:
      skinname = sf.getDefaultSkin()
  tid = get_ident()
  SKINDATA[tid] = (
    None,
    skinname,
    {'portal_skins': None, 'portal_callables': None},
    {})
  if REQUEST is None:
    REQUEST = getattr(self, 'REQUEST', None)
  if REQUEST is not None:
    REQUEST._hold(SkinDataCleanup(tid, SKINDATA[tid]))

def CMFCoreSkinnableSkinnableObjectManager_getSkin(self, name=None):
  """
    Replacement for original getSkin which makes obvious possible remaining
    calls.
    FIXME: Which exception should be raised here ?
  """
  raise Exception, 'This method must not be called when new caching system is applied.'

Skinnable.SkinnableObjectManager.__getattr__ = CMFCoreSkinnableSkinnableObjectManager___getattr__
Skinnable.SkinnableObjectManager.changeSkin = CMFCoreSkinnableSkinnableObjectManager_changeSkin
Skinnable.SkinnableObjectManager.getSkin = CMFCoreSkinnableSkinnableObjectManager_getSkin

# Some original attributes from SkinnableObjectManager are explicitely set as
# value on PortalObjectBase. They must be updated there too, otherwise
# patching is incompletely available at ERP5Site class level.
from Products.CMFCore.PortalObject import PortalObjectBase
PortalObjectBase.__getattr__ = CMFCoreSkinnableSkinnableObjectManager___getattr__

# Redefine SkinDataCleanup completely.
# This class is designed to remove entries from SKINDATA dictionnary, to avoid
# keeping references to persistent objects besides transaction boundaries.
# This cleanup is triggered by deletion of SkinDataCleanup instance, which
# happens after corresponding REQUEST instance is deleted (because of '_hold'
# mechanism).
# But because of the lag which exists between REQUEST deletion and
# SkinDataCleanup deletion (due to garbage collection), it sometimes deletes a
# new SKINDATA entry, unrelated to the intended one. This leaves a system with
# no SKINDATA entry for current thread, leading to errors.
# A case where it's easy to trigger such error is CMFActivity's REQUEST
# separation mechanism, where one request is created for each single activity.

class SkinDataCleanup:
  def __init__(self, tid, skindata):
    self.tid = tid
    self.skindata_id = self.hashSkinData(skindata)

  def __del__(self):
    tid = self.tid
    if SKINDATA is None:
      return
    skindata = SKINDATA.get(tid)
    if skindata is not None:
      if self.hashSkinData(skindata) == self.skindata_id:
        try:
          # Entry might have already disapeared. Ignore.
          del SKINDATA[tid]
        except KeyError:
          pass

  def hashSkinData(self, skindata):
    return id(skindata)


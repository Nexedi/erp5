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
try:
    from Products.CMFCore.Skinnable import superGetAttr
except ImportError:
    # Removed on CMFCore 2.x
    superGetAttr = None

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

def CMFCoreSkinnableSkinnableObjectManager_initializeCache(self):
  '''
    Initialize the cache on portal skins.
  '''
  portal_skins = getattr(self, 'portal_skins', None)
  if portal_skins is None:
    return
  portal_skins = portal_skins.aq_base
  skin_selection_mapping = {}
  for selection_name, skin_folder_id_string in portal_skins._getSelections().iteritems():
    skin_list = {}
    skin_folder_id_list = skin_folder_id_string.split(',')
    skin_folder_id_list.reverse()
    for skin_folder_id in skin_folder_id_list:
      skin_folder = getattr(portal_skins, skin_folder_id, None)
      if skin_folder is not None:
        for skin_id in skin_folder.objectIds():
          skin_list[skin_id] = skin_folder_id
      else:
        LOG('__getattr__', WARNING, 'Skin folder %s is in selection list '\
            'but does not exist.' % (skin_folder_id, ))
    skin_selection_mapping[selection_name] = skin_list
  portal_skins._v_skin_location_list = skin_selection_mapping
  return skin_selection_mapping

Skinnable.SkinnableObjectManager.initializeCache = CMFCoreSkinnableSkinnableObjectManager_initializeCache

def CMFCoreSkinnableSkinnableObjectManager___getattr__(self, name):
  '''
    Looks for the name in an object with wrappers that only reach
    up to the root skins folder.
    This should be fast, flexible, and predictable.
  '''
  if name[:1] != '_' and name[:3] != 'aq_':
    skin_info = SKINDATA.get(get_ident())
    if skin_info is not None:
      skin_selection_name, ignore, resolve = skin_info
      try:
        return resolve[name]
      except KeyError:
        if name not in ignore:
          try:
            portal_skins = aq_base(self.portal_skins)
          except AttributeError:
            raise AttributeError, name
          try:
            skin_selection_mapping = portal_skins._v_skin_location_list
          except AttributeError:
            LOG('Skinnable Monkeypatch __getattr__', DEBUG, 'Initial skin cache fill. This should not happen often. Current thread id:%X' % (get_ident(), ))
            skin_selection_mapping = self.initializeCache()
          try:
            skin_folder_id = skin_selection_mapping[skin_selection_name][name]
          except KeyError:
            pass
          else:
            object = getattr(getattr(portal_skins, skin_folder_id), name, None)
            if object is not None:
              resolve[name] = object.aq_base
              return resolve[name]
            else:
              # We cannot find a document referenced in the cache.
              # Try to find if there is any other candidate in another
              # skin folder of lower priority.
              selection_dict = portal_skins._getSelections()
              candidate_folder_id_list = selection_dict[skin_selection_name].split(',')
              previous_skin_folder_id = skin_selection_mapping[skin_selection_name][name]
              del skin_selection_mapping[skin_selection_name][name]
              if previous_skin_folder_id in candidate_folder_id_list:
                previous_skin_index = candidate_folder_id_list.index(previous_skin_folder_id)
                candidate_folder_id_list = candidate_folder_id_list[previous_skin_index + 1:]
              for candidate_folder_id in candidate_folder_id_list:
                candidate_folder = getattr(portal_skins, candidate_folder_id, None)
                if candidate_folder is not None:
                  object = getattr(candidate_folder, name, None)
                  if object is not None:
                    skin_selection_mapping[skin_selection_name][name] = candidate_folder_id
                    resolve[name] = object.aq_base
                    return resolve[name]
                else:
                  LOG('__getattr__', WARNING, 'Skin folder %s is in selection list '\
                      'but does not exist.' % (candidate_folder_id, ))
          ignore[name] = None
  if superGetAttr is None:
    raise AttributeError, name
  return superGetAttr(self, name)

def CMFCoreSkinnableSkinnableObjectManager_changeSkin(self, skinname):
  '''
    Change the current skin.

    Can be called manually, allowing the user to change
    skins in the middle of a request.

    Patched not to call getSkin.
  '''
  if skinname is None:
    sfn = self.getSkinsFolderName()
    if sfn is not None:
      sf = getattr(self, sfn, None)
      if sf is not None:
        skinname = sf.getDefaultSkin()
  tid = get_ident()
  SKINDATA[tid] = (skinname, {'portal_skins': None}, {})
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


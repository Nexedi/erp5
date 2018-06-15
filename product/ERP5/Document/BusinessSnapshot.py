# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import gc
import os
import posixpath
import transaction
import imghdr
import tarfile
import time
import hashlib
import fnmatch
import re
import threading
import pprint

from copy import deepcopy
from collections import defaultdict
from cStringIO import StringIO
from OFS.Image import Pdata
from lxml.etree import parse
from urllib import quote, unquote
from OFS import SimpleItem, XMLExportImport
from datetime import datetime
from itertools import chain
from operator import attrgetter
from persistent.list import PersistentList
from AccessControl import ClassSecurityInfo, Unauthorized, getSecurityManager
from Acquisition import Implicit, aq_base, aq_inner, aq_parent
from zLOG import LOG, INFO, WARNING

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Core.Folder import Folder
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.PythonScript import PythonScript
from Products.ERP5Type.dynamic.lazy_class import ERP5BaseBroken
from Products.ERP5Type.Globals import Persistent, PersistentMapping
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.patches.ppml import importXML
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter


class BusinessSnapshot(Folder):
  """
  An installed/replaced snaphot should always be reduced, i.e, there can't be
  more than one item on same path because it doesn't denote the state if there
  is multiple on same path.
  """

  meta_type = 'ERP5 Business Snashot'
  portal_type = 'Business Snapshot'
  add_permission = Permissions.AddPortalContent
  allowed_types = ('Business Item',)

  id_generator = '_generateUniversalUniqueId'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  template_format_version = 3

  # Factory Type Information
  factory_type_information = \
    {    'id'             : portal_type
       , 'meta_type'      : meta_type
       , 'icon'           : 'file_icon.gif'
       , 'product'        : 'ERP5Type'
       , 'factory'        : ''
       , 'type_class'     : 'BusinessSnapshot'
       , 'immediate_view' : 'BusinessSnapshot_view'
       , 'allow_discussion'     : 1
       , 'allowed_content_types': ('Business Item',)
       , 'filter_content_types' : 1
    }

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
                      PropertySheet.Base,
                      PropertySheet.XMLObject,
                      PropertySheet.SimpleItem,
                      PropertySheet.CategoryCore,
                      PropertySheet.Version,
                    )

  def getItemList(self):
    """
    Returns the collection of all Business Item, Business Property Item and
    Business Patch item at the given snapshot.
    """
    return self.objectValues()

  def getItemPathList(self):
    """
    Returns the path of all Business Item, Business Property Item and
    Business Patch item at the given snapshot.
    """
    return [l.getProperty('item_path') for l in self.getItemList()]

  def getBusinessItemByPath(self, path):
    """
    Returns the Item given the path of item. Returns None if it doesn't exist
    """
    item_list = self.getItemList()
    try:
      return [l for l in item_list if l.getProperty('item_path') == path][0]
    except IndexError:
      return

  def getLastSnapshot(self):
    """
    Get last snapshot installed.
    Returns None if there is no last snapshot.
    """

    portal = self.getPortalObject()
    commit_tool = portal.portal_commits

    # XXX: Is it a good idea to be dependent on portal_catalog to get Snapshot list ?
    snapshot_list = commit_tool.searchFolder(
                                          portal_type='Business Snapshot',
                                          validation_state='installed'
                                          )

    # There should never be more than 1 installed snapshot
    if len(snapshot_list) == 1:
      # Get the last installed snapshot
      return snapshot_list[0].getObject()

    return None

  #def build(self, **kwargs):
  #  """
  #  Using equivalent commit, create a snapshot of ZODB state
  #  """
  #  new_item_list = []
  #  new_item_path_list = []

  #  # Get the equivalent commit for the snapshot
  #  eqv_commit = self.getSimilarValue()

  #  # Get last created snapshot
  #  last_snapshot = self.getLastSnapshot()

  #  # Commit list of all commits between the last snapshot/first commit and the
  #  # current snapshot
  #  successor_commit_list = []

  #  # If there is last snapshot, then combine all the commit afterwards to create
  #  # new snapshot
  #  if last_snapshot:

  #    for item in last_snapshot.objectValues():
  #      if item.getFollowUpValue().getAvailabilityState() == 'installable':
  #        new_item_list.append(item)
  #        new_item_path_list.extend(item.getProperty('item_path'))

  #    # Get next predecessor commit for this snapshot using the equivalent commit
  #    # Notice that we don't use the snapshot to get the next commit as the
  #    # snapshot is mere a state which uses `predecessor` just for mentioning the
  #    # equivalent commit.
  #    # Here the first next commit should be the commit created after last snapshot
  #    # which we can get using the equivalent commit of last snapshot and then
  #    # finding the next commit for it
  #    next_commit = last_snapshot.getSimilarValue().getPredecessorRelatedValue()

  #  # If there is no last snapshot, create a new one by combining all the commits
  #  else:
  #    # Get the oldest commit and start from there to find the next commit
  #    oldest_commit = min(
  #                  self.aq_parent.objectValues(portal_type='Business Commit'),
  #                  key=(lambda x: x.getCreationDate()))

  #    for item in oldest_commit.objectValues():
  #      if item.getFollowUpValue().getAvailabilityState() == 'installable':
  #        new_item_list.append(item)
  #        new_item_path_list.extend(item.getProperty('item_path'))

  #    next_commit = oldest_commit.getPredecessorRelatedValue()

  #  # Fill sucessor commit list
  #  while (next_commit.getId() != eqv_commit.getId()):
  #    successor_commit_list.append(next_commit)
  #    next_commit = next_commit.getPredecessorRelatedValue()

  #  # Append the equivalent commit to successor commits
  #  successor_commit_list.append(eqv_commit)

  #  for commit in successor_commit_list:
  #    for item in commit.objectValues():
  #      # Check if the item has a follow_up only with installable Business Template
  #      if item.getFollowUpValue().getAvailabilityState() == 'installable':
  #        item_path = item.getProperty('item_path')
  #        if item_path in new_item_path_list:
  #          # Replace the old item with same path with new item
  #          new_item_list = [l if l.getProperty('item_path') != item_path else item for l in new_item_list]
  #        else:
  #          # Add the item to list if there is no existing item at that path
  #          new_item_list.append(item)
  #          new_item_path_list.append(item_path)

  #  # Create hardlinks for the objects
  #  for item in new_item_list:
  #    self._setObject(item.id, item, suppress_events=True)

  def preinstall(self):
    """
    Compares the last installed snapshot, to be installed snapshot and the
    state at ZODB, and then returns the modification list

    Steps:
    1. Get paths for items in old and new snapshot
    2. Create a temporary snapshot(called 'installation process') for items
      which are going to be added, removed, modified
    3. Add the list of items which has been removed from last snaphshot in the
      temporary snapshot while changing their item_sign to -1.
    4. For the items which are in both the snapshot, we have 2 process:
        - No modification: Add new item to temporary snapshot directly
        - Modification: Add old item to temporary snapshot
    5. Using installation process(items needed to be installed),
      installed_snapshot and the items at ZODB, we decide what to install.
    """
    modified_list = []
    zodb_modified_list = []

    portal = self.getPortalObject()
    portal_commits = portal.portal_commits
    installed_snapshot = portal_commits.getInstalledSnapshot()

    # Create installation process, which have the changes to be made in the
    # OFS during installation. Importantly, it should be a temp Business Snapshot
    installation_process = portal_commits.newContent(
                                                portal_type='Business Snapshot',
                                                title='Installation Process',
                                                temp_object=True,
                                                )

    if installed_snapshot not in (self, None):

      old_item_list = installed_snapshot.getItemList()
      old_state_path_list = installed_snapshot.getItemPathList()

      new_item_list = self.getItemList()
      new_state_path_list = self.getItemPathList()

      to_install_path_item_list = []

      # Get the path which has been removed in new installation_state
      removed_path_list = [path for path
                           in old_state_path_list
                           if path not in new_state_path_list]

      # Add the removed path with negative sign in the to_install_path_item_list
      for path in removed_path_list:
        old_item = installed_snapshot.getBusinessItemByPath(path)
        # XXX: We can't change anything in the objects as they are just there
        # for comparison and in reality they are hardlinks
        #old_item = old_item._getCopy(installation_process)
        installation_process._setObject(old_item.id, old_item,
                                      suppress_events=True)
        old_item.setProperty('item_sign', '-1')

      # Path Item List for installation_process should be the difference between
      # old and new installation state
      for item in self.objectValues():

        old_item = installed_snapshot.getBusinessItemByPath(item.getProperty('item_path'))
        self.updateHash(item)

        if old_item:
          to_be_installed_item = item
          # If the old_item exists, we match the hashes and if it differs, then
          # add the new item
          if old_item.getProperty('item_sha') != item.getProperty('item_sha'):
            #to_be_installed_item = to_be_installed_item._getCopy(installation_process)
            installation_process._setObject(to_be_installed_item.id,
                                          to_be_installed_item,
                                          suppress_events=True)

        else:
          installation_process._setObject(item.id, item,
                                        suppress_events=True)

    # If there is no snapshot installed, everything in new snapshot should be
    # just compared to ZODB state.
    else:
      for item in self.objectValues():
        item = item._getCopy(installation_process)
        installation_process._setObject(item.id, item, suppress_event=True)

    change_list = self.compareOldStateToOFS(installation_process, installed_snapshot)

    if change_list:
      change_list = [(l[0].item_path, l[1]) for l in change_list]

    return change_list

  def compareOldStateToOFS(self, installation_process, installed_snapshot):

    # Get the paths about which we are concerned about
    to_update_path_list = installation_process.getItemPathList()
    portal = self.getPortalObject()

    # List to store what changes will be done to which path. Here we compare
    # with all the states (old version, new version and state of object at ZODB)
    change_list = []

    to_update_path_list = self.sortPathList(to_update_path_list)

    for path in to_update_path_list:
      try:
        # Better to check for status of BusinessPatchItem separately as it
        # can contain both BusinessItem as well as BusinessPropertyItem
        new_item = installation_process.getBusinessItemByPath(path)

        if '#' in str(path):
          isProperty = True
          relative_url, property_id = path.split('#')
          obj = portal.restrictedTraverse(relative_url)
          property_value = obj.getProperty(property_id)

          # If the value at ZODB for the property is none, raise KeyError
          # This is important to have compatibility between the way we check
          # path as well as property. Otherwise, if we install a new property,
          # we are always be getting an Error that there is change made at
          # ZODB for this property
          if not property_value:
            raise KeyError
          property_type = obj.getPropertyType(property_id)
          obj = property_value
        else:
          isProperty = False
          # XXX: Hardcoding because of problem with 'resource' trying to access
          # the resource via acqusition. Should be removed completely before
          # merging (DONT PUSH THIS)
          if path == 'portal_categories/resource':
            path_list = path.split('/')
            container_path = path_list[:-1]
            object_id = path_list[-1]
            container = portal.restrictedTraverse(container_path)
            obj = container._getOb(object_id)
          else:
            obj = portal.restrictedTraverse(path)

        obj_sha = self.calculateComparableHash(obj, isProperty)

        # Get item at old state
        if not installed_snapshot:
          old_item = None
        else:
          old_item = installed_snapshot.getBusinessItemByPath(path)

        # Check if there is an object at old state at this path
        if old_item:
          # Compare hash with ZODB

          if old_item.getProperty('item_sha') == obj_sha:
            # No change at ZODB on old item, so get the new item
            new_item = installation_process.getBusinessItemByPath(path)
            # Compare new item hash with ZODB

            if new_item.getProperty('item_sha') == obj_sha:
              if int(new_item.getProperty('item_sign')) == -1:
                # If the sign is negative, remove the value from the path
                change_list.append((new_item, 'Removing'))
              else:
                # If same hash, and +1 sign, do nothing
                continue

            else:
              # Install the new_item
              change_list.append((new_item, 'Adding'))

          else:
            # Change at ZODB, so get the new item
            new_item = installation_process.getBusinessItemByPath(path)
            # Compare new item hash with ZODB

            if new_item.getProperty('item_sha') == obj_sha:
              # If same hash, do nothing
              continue

            else:
              # Trying to update change at ZODB
              change_list.append((new_item, 'Updating'))

        else:
          # Object created at ZODB by the user
          # Compare with the new_item

          new_item = installation_process.getBusinessItemByPath(path)
          if new_item.getProperty('item_sha') == obj_sha:
            # If same hash, do nothing
            continue

          else:
            # Trying to update change at ZODB
            change_list.append((new_item, 'Updating'))

      except (AttributeError, KeyError) as e:
        # Get item at old state
        if not installed_snapshot:
          old_item = None
        else:
          old_item = installed_snapshot.getBusinessItemByPath(path)

        # Check if there is an object at old state at this path
        if old_item:
          # This means that the user had removed the object at this path
          # Check what the sign is for the new_item
          new_item = installation_process.getBusinessItemByPath(path)
          # Check sign of new_item

          if int(new_item.getProperty('item_sign')) == 1:
            # Object at ZODB has been removed by the user
            change_list.append((new_item, 'Adding'))

        else:
          # If there is  no item at old state, install the new_item
          new_item = installation_process.getBusinessItemByPath(path)
          # XXX: Hack for not trying to install the sub-objects from zexp,
          # This should rather be implemented while exporting the object,
          # where we shouldn't export sub-objects in the zexp
          if not isProperty:
            try:
              value =  new_item.objectValues()[0]
            except IndexError:
              continue
          # Installing a new item
          change_list.append((new_item, 'Adding'))

    return change_list

  def updateHash(self, item):
    """
    Function to update hash of Business Item or Business Property Item
    """
    # Check for isProperty attribute
    if item.isProperty:
      value = item.getProperty('item_property_value')
    else:
      value_list = item.objectValues()
      if value_list:
        value = value_list[0]
      else:
        value = ''

    if value:
      item.setProperty('item_sha', self.calculateComparableHash(
                                                            value,
                                                            item.isProperty,
                                                            ))

  def calculateComparableHash(self, object, isProperty=False):
    """
    Remove some attributes before comparing hashses
    and return hash of the comparable object dict, in case the object is
    an erp5 object.

    Use shallow copy of the dict of the object at ZODB after removing
    attributes which changes at small updation, like workflow_history,
    uid, volatile attributes(which starts with _v)

    # XXX: Comparable hash shouldn't be used for BusinessPatchItem as whole.
    We can compare the old_value and new_value, but there shouldn't be hash
    for the Patch Item.
    """
    if isProperty:
      obj_dict = object
      # Have compatibilty between tuples and list while comparing as we face
      # this situation a lot especially for list type properties
      if isinstance(obj_dict, list):
        obj_dict = tuple(obj_dict)
    else:

      klass = object.__class__
      classname = klass.__name__
      obj_dict = object.__dict__.copy()

      # If the dict is empty, do calculate hash of None as it stays same on
      # one platform and in any case its impossiblt to move live python
      # objects from one seeion to another
      if not bool(obj_dict):
        return hash(None)

      attr_set = {'_dav_writelocks', '_filepath', '_owner', '_related_index',
                  'last_id', 'uid', '_mt_index', '_count', '_tree',
                  '__ac_local_roles__', '__ac_local_roles_group_id_dict__',
                  'workflow_history', 'subject_set_uid_dict', 'security_uid_dict',
                  'filter_dict', '_max_uid'}

      attr_set.update(('isIndexable',))

      if classname in ('File', 'Image'):
        attr_set.update(('_EtagSupport__etag', 'size'))
      elif classname == 'Types Tool' and klass.__module__ == 'erp5.portal_type':
        attr_set.add('type_provider_list')

      for attr in object.__dict__.keys():
        if attr in attr_set or attr.startswith('_cache_cookie_') or attr.startswith('_v'):
          try:
            del obj_dict[attr]
          except AttributeError:
            # XXX: Continue in cases where we want to delete some properties which
            # are not in attribute list
            # Raise an error
            continue

        # Special case for configuration instance attributes
        if attr in ['_config', '_config_metadata']:
          import collections
          # Order the dictionary so that comparison can be correct
          obj_dict[attr] = collections.OrderedDict(sorted(obj_dict[attr].items()))
          if 'valid_tags' in obj_dict[attr]:
            try:
              obj_dict[attr]['valid_tags'] = collections.OrderedDict(sorted(obj_dict[attr]['valid_tags'].items()))
            except AttributeError:
              # This can occur in case the valid_tag object is PersistentList
              pass

      if 'data' in obj_dict:
        try:
          obj_dict['data'] = obj_dict.get('data').__dict__
        except AttributeError:
          pass

    obj_sha = hash(pprint.pformat(obj_dict))
    return obj_sha

  def sortPathList(self, path_list):
    """
    Custom sort for path_list according to the priorities of paths
    """
    def comparePath(path):
      split_path_list = path.split('/')
      # Paths with property item should have the least priority as they should
      # be installed after installing the object only
      if '#' in path:
        return 11
      if len(split_path_list) == 2 and split_path_list[0] in ('portal_types', 'portal_categories'):
        return 1
      # portal_transforms objects needs portal_components installed first so
      # as to register the modules
      if len(split_path_list) == 2 and split_path_list[0] == 'portal_transforms':
        return 12
      if len(split_path_list) > 2:
        return 10
      if len(split_path_list) == 1:
        return 2
      return 5

    return sorted(path_list, key=comparePath)

  def install(self):
    """
    Install the sub-objects in the commit
    """
    site = self.getPortalObject()

    # While installing a new snapshot, last snapshot state should be
    # changed to 'replaced'
    last_snapshot = self.getLastSnapshot()
    if last_snapshot not in (None, self):
      if site.portal_workflow.isTransitionPossible(
          last_snapshot, 'replace'):
        last_snapshot.replace(self)

    # Now install the items in new snapshot, using the aq_parent of item as its
    # context. This is important because if we use the snapshot as the context,
    # it will change the parent of the items to snapshot, which is undesirable
    # as we want them to stay as hardlinks in the snapshot
    for item in self.objectValues():
      item.install(item.aq_parent)

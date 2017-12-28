# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush-Tiwari <ayush.tiwari@nexedi.com>
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

  meta_type = 'ERP5 Business Snashot'
  portal_type = 'Business Snapshot'
  add_permission = Permissions.AddPortalContent
  allowed_types = ('Business Item',
                   'Business Property Item',
                   'Business Patch item',)

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
       , 'allowed_content_types': ( 'Business Item',
                                    'Business Property Item',
                                    'Business Patch Item',
                                    )
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

  def getLastSnapshot(self):
    """
    Get last snapshot exisiting.
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

  def build(self, **kwargs):
    """
    Using equivalent commit, create a snapshot of ZODB state
    """
    new_item_list = []
    new_item_path_list = []

    # Get the equivalent commit for the snapshot
    eqv_commit = self.getSimilarValue()

    # Get last created snapshot
    last_snapshot = self.getLastSnapshot()

    # Commit list of all commits between the last snapshot/first commit and the
    # current snapshot
    successor_commit_list = []

    # If there is last snapshot, then combine all the commit afterwards to create
    # new snapshot
    if last_snapshot:

      # [1]: Extend the item_list with list of items from last snapshot
      new_item_list.extend(last_snapshot.getItemList())
      new_item_path_list.extend(last_snapshot.getItemPathList())

      # Get next predecessor commit for this snapshot using the equivalent commit
      # Notice that we don't use the snapshot to get the next commit as the
      # snapshot is mere a state which uses `predecessor` just for mentioning the
      # equivalent commit.
      # Here the first next commit should be the commit created after last snapshot
      # which we can get using the equivalent commit of last snapshot and then
      # finding the next commit for it
      next_commit = last_snapshot.getSimilarValue().getPredecessorRelatedValue()

    # If there is no last snapshot, create a new one by combining all the commits
    else:
      # Get the oldest commit and start from there to find the next commit
      oldest_commit = min(
                    self.aq_parent.objectValues(portal_type='Business Commit'),
                    key=(lambda x: x.getCreationDate()))

      new_item_list.extend(oldest_commit.objectValues())
      new_item_path_list.extend(oldest_commit.getItemPathList())

      next_commit = oldest_commit.getPredecessorRelatedValue()

    # Fill sucessor commit list
    while (next_commit.getId() != eqv_commit.getId()):
      successor_commit_list.append(next_commit)
      next_commit = next_commit.getPredecessorRelatedValue()

    # Append the equivalent commit to successor commits
    successor_commit_list.append(eqv_commit)

    for commit in successor_commit_list:
      for item in commit.objectValues():
        item_path = item.getProperty('item_path')
        if item_path in new_item_path_list:
          # Replace the old item with same path with new item
          new_item_list = [l if l.getProperty('item_path') != item_path else item for l in new_item_list]
        else:
          # Add the item to list if there is no existing item at that path
          new_item_list.append(item)
          new_item_path_list.append(item_path)

    # Create hardlinks for the objects
    for item in new_item_list:
      self._setObject(item.id, item, suppress_events=True)

  def install(self):
    """
    Install the sub-objects in the commit
    """
    site = self.getPortalObject()

    # While installing a new snapshot, last snapshot state should be
    # changed to 'replaced'
    last_snapshot = self.getLastSnapshot()
    if last_snapshot not in [None, self]:
      if site.portal_workflow.isTransitionPossible(
          last_snapshot, 'replace'):
        last_snapshot.replace(self)

    # Now install the items in new snapshot
    for item in self.objectValues():
      item.install(self)

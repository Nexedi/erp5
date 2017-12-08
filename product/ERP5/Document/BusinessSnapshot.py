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

  # Attribute to store item list which are basically hardlinks
  item_list = []

  def __init__(self, id):
    """
    While creating a new Business Snapshot, we need to create the hardlinks
    and create a snapshot from the commits.
    """
    super(BusinessSnapshot, self).__init__(id)

  def install(self):
    """
    Installing a snapshot should be similar to installing an installation_state
    we used to have for Business Manager(s)
    """
    pass

  def getLastSnapshot(self):

    portal = self.getPortalObject()
    commit_tool = portal.portal_commits

    # Get the snapshot list except the current snapshot
    snapshot_list = [l for l
                     commit_tool.objectValues(portal_type='Business Snapshot')
                     if l != self]

    if snapshot_list:
      # Get the last created/installed snapshot comparing creation_date
      return max(snapshot_list, key=(lambda x: x.getCreationDate()))

    return None

  def getItemList(self):
    """
    Returns the collection of all Business Item, Business Property Item and
    Business Patch item at the given snapshot.
    """
    return self.item_list

  def getItemPathList(self):
    """
    Returns the path of all Business Item, Business Property Item and
    Business Patch item at the given snapshot.
    """
    return [l.getProperty('item_path') for l in self.getItemList()]

  def buildSnapshot(self):
    """
    Using equivalent commit, create a snapshot of ZODB state
    """
    new_item_list = []
    new_item_path_list = []

    # Get the equivalent commit for the snapshot
    eqv_commit = self.getPredecessorValue()

    # Get last created snapshot
    last_snapshot = self.getLastSnapshot()

    # [1]: Extend the item_list with list of items from last snapshot
    new_item_list.extend(last_snapshot.getItemList())
    new_item_path_list.extend(last_snapshot.getItemPathList())

    # Get next commit list upto the commit to be installed
    portal_commits = self.aq_parent
    successor_commit_list = []

    # Get next predecessor commit for this snapshot using the equivalent commit
    # Notice that we don't use the snapshot to get the next commit as the
    # snapshot is mere a state which uses `predecessor` just for mentioning the
    # equivalent commit.
    next_commit = eqv_commit.getPredecessorRelatedValue()

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

    self.item_list = new_item_list

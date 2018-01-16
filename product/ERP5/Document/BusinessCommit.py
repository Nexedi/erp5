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
import uuid

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

class BusinessCommit(Folder):

  meta_type = 'ERP5 Business Commit'
  portal_type = 'Business Commit'
  add_permission = Permissions.AddPortalContent
  allowed_types = ('Business Item',
                   'Business Property Item',
                   'Business Patch item',)

  template_format_version = 3

  # Factory Type Information
  factory_type_information = \
    {    'id'             : portal_type
       , 'meta_type'      : meta_type
       , 'icon'           : 'file_icon.gif'
       , 'product'        : 'ERP5Type'
       , 'factory'        : ''
       , 'type_class'     : 'BusinessCommit'
       , 'immediate_view' : 'BusinessCommit_view'
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

  security.declarePublic('newContent')
  def newContent(self, id=None, **kw):
    """
    Override newContent so as to use 'id' generated like hash.
    Also, copy the objects in the Business Commit after creating new object
    """
    if id is None:
      id = uuid.uuid1()

    return super(BusinessCommit, self).newContent(id, **kw)

  def createEquivalentSnapshot(self):
    """
    This function uses the current commit to create a new snapshot
    """
    site = self.getPortalObject()
    portal_commits = self.aq_parent

    # Create empty snapshot
    snapshot = portal_commits.newContent(portal_type='Business Snapshot')
    # Add the current commit as predecessor. This way we can have the BI
    # BPI in that commit to the Business Snapshot also.
    snapshot.setSimilarValue(self)
    self.setSimilarValue(snapshot)

    # Build the snapshot
    if snapshot not in [None, self]:
      if site.portal_workflow.isTransitionPossible(
          snapshot, 'build'):
        snapshot.build()

    return snapshot

  def install(self):
    """
    Installation:
    - Check if the status is committed (Done by constraint of Business Commit
      portal_type)
    - Check if there are installed Business Template V2(s) because they will be
      required in building new Business Snapshot. Raise if there are None.
    - Create an equivalent snapshot (using items of this commit and predecessors
      belonging to installed Business Template V2s)
    - TODO: Compare the snapshot with the last snapshot
    - Install the snapshot
    """
    site = self.getPortalObject()
    portal_templates = site.portal_templates
    installed_bt_list = portal_templates.getInstalledBusinessTemplateV2List()

    # Should raise if there is no installed BM in ZODB. Should install BM via
    # portal_templates first.
    # XXX: Maybe instead of raising, we can provide an option to install BM
    # here only. So that a new user don't get confused ?
    if not installed_bt_list:
      raise ValueError('There is no installed BT to create snapshot')

    successor_list = self.getPredecessorRelatedValueList()

    # Check if the successor list has a snapshot in it
    try:
      eqv_snapshot = [l for l
                      in successor_list
                      if l.getPortalType() == 'Business Snapshot'][0]
    except IndexError:
      # Create a new equivalent snapshot
      eqv_snapshot = self.createEquivalentSnapshot()

    # When installing Business Snapshot, installation state should be changed
    if eqv_snapshot not in [None, self]:
      if site.portal_workflow.isTransitionPossible(
          eqv_snapshot, 'install'):
        eqv_snapshot.install()

  def getItemPathList(self):
    return [l.getProperty('item_path') for l in self.objectValues()]

  def getBusinessTemplateV2List(self):
    """
    Give the list of all Business Template V2(s) being touched by this Business
    Commit
    """
    template_list = []
    for item in self.objectValues():
      template_list.extend(item.getFollowUpValueList())

    return list(set(template_list))

  def getBusinessTemplateV2TitleList(self):
    title_list = [l.getTitle() for l in self.getBusinessTemplateV2List()]
    return title_list

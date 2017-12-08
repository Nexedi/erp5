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

  def install(self):
    """
    Installation:
    - create an empty snapshot that that's similar to a Commit
    - fill it with hard links to commits and snapshots
    - install it
    """
    portal_commit = self.aq_parent

    # Create empty snapshot
    snapshot = portal_commit.newContent(portal_type='Business Commit')
    # Add the current commit as predecessor. This way we can have the BI
    # BPI in that commit to the Business Snapshot also.
    snapshot.setPredecessorValue(self)

    # Build the snapshot
    snapshot.buildSnapshot()

    for item in snapshot.item_path_list:
      item.install(self)

  def getPathList(self):
    return [l.getProperty('item_path') for l in self.objectValues()]

# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from webdav.client import Resource

from App.config import getConfiguration
import os
import time
import shutil
import sys
import hashlib
import pprint
import transaction

from Acquisition import Implicit, Explicit
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFActivity.ActiveResult import ActiveResult
from Products.PythonScripts.PythonScript import PythonScript
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.DiffUtils import DiffFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5.Document.BusinessTemplate import BusinessTemplateMissingDependency
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5.genbt5list import generateInformation
from Acquisition import aq_base
from tempfile import mkstemp, mkdtemp
from Products.ERP5 import _dtmldir
from cStringIO import StringIO
from urllib import pathname2url, urlopen, splittype, urlretrieve
import urllib2
import re
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError
import struct
import cPickle
from base64 import b64encode, b64decode
from Products.ERP5Type.Message import translateString
from zLOG import LOG, INFO, WARNING
from base64 import decodestring
from difflib import unified_diff
from operator import attrgetter
import subprocess
import time

class CommitTool (BaseTool):
    """
      CommitTool manages commits of Business Templates.

      CommitTool provides some methods to deal with Business Templates:
        - download commits
        - install commits
        - push commits
        - XXX

      ERP5 Business Commit contains:
      - ERP5 Business Template Item
      - ERP5 Business Template Property Item
      - ERP5 Business Template Patch Item
      in relation to one or more ERP5 Business Template (follow_up relation from BTI to BTS)

      ERP5 Business Commit has relation to:
      - predecessor: previous Business Commit

      ERP5 Business Snapshot has relation to:
      - similar: equivalent ERP5 Business Commit
      they only serve as a way to optmize installation time by having all objects in one
      folder rather than downloading 10 years of commit to get things installed

      ERP5 Business Temaplate Specification defines:
      - title
      - description
      - dependency
      - list of paths (of different kinds) to help generate initial ERP5 Business Commit
      It is only a spec file with no object inside

      ERP5 Business Snapshot contains:
      - all BTI BTPI and BTPI for a single BT at specifc build point

      Bootstrap:
      - import zexp file to portal_commits/
      - portal_commits/business_template_index is installed (ERP5 Buiness Snapshot of the erp5_root_index business template) [BOOSTRAP]
      - this makes portal_templates/* full of all possibles Business Template that can be installed
      - portal_commits/business_template_index --> similar/portal_commits/387897938794876-276376

      Portal Templates:
      - portal_templates/erp5_base (only one)
      - portal_templates/erp5_trade (only one)
      they containing nothing inside, just their title and description and spec (like a spec file in rpm)

      Installation:
      - download all commits that
      - are predecessor of 387897938794876-276376
      - that are required to install (erp5_base, erp5_trade, etc.)
      RESULT:
        - portal_commits/387897938794876-1 (Commit)
        - portal_commits/387897938794876-2 (Commit)
        - portal_commits/387897938794876-3 (Commit)
        - portal_commits/387897938794876-4 (Commit)
        - portal_commits/387897938794876-5 (Commit)
        - portal_commits/387897938794876-6 (Commit)
        - portal_commits/387897938794876-7 (Commit)
        - portal_commits/387897938794876-8 (Commit)
        - portal_commits/387897938794876-9 (Snapshort of erp5_trade)
        - portal_commits/387897938794876-10 (Snapshot of erp5_base)

      Draft -> Commited -> Pushed (to repo)  |Commit]
      Draft -> Installed <-> Uninstalled |Snapshot]

      Developer mode: make commits and push them (nothing else)
      Developer mode: make snapshots and push them (nothing else)

      Installation:
      - create an empty snapshot that that's similar to a Commit
      - fill it with hard links to commits and snapshots
      - install it

      Only Draft can be modified

      3 types
      - Commit - partial state (pushed)
      - Save Point - complete state with copies of a single bt (only for
      optimisation) (really needed ?) (pushed)
      - Snapshort - complete state with hard link for all bt (installed)

      We should try first with Commit and Snapshot
    """
    id = 'portal_commits'
    title = 'Commit Tool'
    meta_type = 'ERP5 Commit Tool'
    portal_type = 'Commit Tool'
    allowed_types = (
      'ERP5 Business Commit',
      'ERP5 Business Snapshot',
      )

    # This stores information on repositories.
    repository_dict = {}

    # Declarative Security
    security = ClassSecurityInfo()

    security.declareProtected(Permissions.ManagePortal, 'manage_overview')
    #manage_overview = DTMLFile('explainCommitTool', _dtmldir)

    def getCommitList(self):
      return self.objectValues(portal_type='Business Commit')

    security.declarePublic('newContent')
    def newContent(self, id=None, **kw):
      """
      Override newContent so as to use 'id' generated like hash
      """
      if id is None:
        id = self.generateNewId()

      id = str(str(id) + '_' + str(time.time())).replace('.', '')
      return super(CommitTool, self).newContent(id, **kw)

InitializeClass(CommitTool)

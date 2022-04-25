# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
##############################################################################
import six

from Products.ERP5Type import WITH_LEGACY_WORKFLOW

# Load all monkey patches
from Products.ERP5Type.patches import WSGIPublisher
from Products.ERP5Type.patches import HTTPRequest
from Products.ERP5Type.patches import AccessControl_patch
from Products.ERP5Type.patches import Restricted
from Products.ERP5Type.patches import m2crypto
from Products.ERP5Type.patches import ObjectManager
from Products.ERP5Type.patches import PropertyManager
from Products.ERP5Type.patches import TM
from Products.ERP5Type.patches import DA
if WITH_LEGACY_WORKFLOW:
  from Products.ERP5Type.patches import DCWorkflow
  from Products.ERP5Type.patches import Worklists
from Products.ERP5Type.patches import BTreeFolder2
if WITH_LEGACY_WORKFLOW:
  from Products.ERP5Type.patches import WorkflowTool
from Products.ERP5Type.patches import DynamicType
from Products.ERP5Type.patches import Expression
from Products.ERP5Type.patches import sqltest
from Products.ERP5Type.patches import sqlvar
from Products.ERP5Type.patches import CMFCatalogAware
from Products.ERP5Type.patches import ProductContext
from Products.ERP5Type.patches import PropertiedUser
if WITH_LEGACY_WORKFLOW:
  from Products.ERP5Type.patches import States
from Products.ERP5Type.patches import FSZSQLMethod
from Products.ERP5Type.patches import ActionInformation
from Products.ERP5Type.patches import ActionProviderBase
from Products.ERP5Type.patches import ActionsTool
from Products.ERP5Type.patches import CookieCrumbler
if six.PY2:
  # XXX- patch for webdav
  from Products.ERP5Type.patches import PropertySheets
from Products.ERP5Type.patches import CMFCoreSkinnable
from Products.ERP5Type.patches import CMFCoreSkinsTool
from Products.ERP5Type.patches import OFSFile
from Products.ERP5Type.patches import OFSFolder
from Products.ERP5Type.patches import OFSUninstalled
from Products.ERP5Type.patches import PersistentMapping
from Products.ERP5Type.patches import DateTimePatch
from Products.ERP5Type.patches import PythonScript
from Products.ERP5Type.patches import MailHost
if six.PY2:
  # No more ZServer
  from Products.ERP5Type.patches import http_server
from Products.ERP5Type.patches import memcache_client
if WITH_LEGACY_WORKFLOW:
  from Products.ERP5Type.patches import StateChangeInfoPatch
from Products.ERP5Type.patches import transforms
from Products.ERP5Type.patches import OFSPdata
from Products.ERP5Type.patches import make_hidden_input
if six.PY2:
  # Check with other work on ZODB
  from Products.ERP5Type.patches import DemoStorage
from Products.ERP5Type.patches import unicodeconflictresolver
from Products.ERP5Type.patches import ZODBConnection
if six.PY2:
  from Products.ERP5Type.patches import ZopePageTemplateUtils
from Products.ERP5Type.patches import OFSHistory
from Products.ERP5Type.patches import OFSItem
from Products.ERP5Type.patches import ExternalMethod
from Products.ERP5Type.patches import User
from Products.ERP5Type.patches import zopecontenttype
from Products.ERP5Type.patches import OFSImage
from Products.ERP5Type.patches import _transaction
from Products.ERP5Type.patches import default_zpublisher_encoding
if six.PY2:
  # DCWorkflowGraph is dead since 2011, so no py3 version
  from Products.ERP5Type.patches import DCWorkflowGraph
from Products.ERP5Type.patches import SourceCodeEditorZMI
from Products.ERP5Type.patches import CachingPolicyManager
from Products.ERP5Type.patches import AcceleratedHTTPCacheManager
from Products.ERP5Type.patches import ExceptionFormatter
if six.PY2:
  # Not needed with Zope4 and new ZMI
  from Products.ERP5Type.patches import DTMLMethod
  from Products.ERP5Type.patches import DTMLDocument
  # No ZServer, so no webdav
  from Products.ERP5Type.patches import WebDAV
from Products.ERP5Type.patches import DTMLMethod
from Products.ERP5Type.patches import DTMLDocument
from Products.ERP5Type.patches import CMFCoreUtils
from Products.ERP5Type.patches import ZopePageTemplate
from Products.ERP5Type.patches import ZSQLMethod
from Products.ERP5Type.patches import MimetypesRegistry
from Products.ERP5Type.patches import users
if six.PY2:
  # No ZServer
  from Products.ERP5Type.patches import Publish
from Products.ERP5Type.patches import WSGITask
if six.PY2:
  # XXX-zope4py3: urllib2 removed (see future/backports/urllib/request.py)
  from Products.ERP5Type.patches import urllib_opener

# These symbols are required for backward compatibility
from Products.ERP5Type.patches.PropertyManager import ERP5PropertyManager
from Products.ERP5Type.Core.Workflow import ValidationFailed
if WITH_LEGACY_WORKFLOW:
  from Products.ERP5Type.patches.DCWorkflow import ERP5TransitionDefinition
from Products.ERP5Type.patches.BTreeFolder2 import ERP5BTreeFolder2Base

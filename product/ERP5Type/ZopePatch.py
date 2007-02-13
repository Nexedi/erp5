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

# Load all monkey patches
from Products.ERP5Type.patches import ObjectManager
from Products.ERP5Type.patches import PropertyManager
from Products.ERP5Type.patches import DA
from Products.ERP5Type.patches import DCWorkflow
from Products.ERP5Type.patches import BTreeFolder2
from Products.ERP5Type.patches import Transaction
from Products.ERP5Type.patches import WorkflowTool
from Products.ERP5Type.patches import XMLExportImport
from Products.ERP5Type.patches import ppml
from Products.ERP5Type.patches import Expression
from Products.ERP5Type.patches import sqlvar
from Products.ERP5Type.patches import CMFCatalogAware
from Products.ERP5Type.patches import ProductContext
from Products.ERP5Type.patches import PropertiedUser
from Products.ERP5Type.patches import States
from Products.ERP5Type.patches import FSZSQLMethod
from Products.ERP5Type.patches import ActionInformation
from Products.ERP5Type.patches import ActionProviderBase
from Products.ERP5Type.patches import CookieCrumbler
from Products.ERP5Type.patches import Localizer
from Products.ERP5Type.patches import CMFMailIn
from Products.ERP5Type.patches import CMFCoreUtils
from Products.ERP5Type.patches import PropertySheets
from Products.ERP5Type.patches import CMFCoreSkinnable
from Products.ERP5Type.patches import CMFCoreSkinsTool
from Products.ERP5Type.patches import OFSFolder
from Products.ERP5Type.patches import HTTPRequest

# These symbols are required for backward compatibility
from Products.ERP5Type.patches.PropertyManager import ERP5PropertyManager
from Products.ERP5Type.patches.DCWorkflow import ValidationFailed, ERP5TransitionDefinition
from Products.ERP5Type.patches.BTreeFolder2 import ERP5BTreeFolder2Base

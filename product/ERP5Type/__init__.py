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
"""
    ERP5Type is provides a RAD environment for Zope / CMF
    All ERP5 classes derive from ERP5Type
"""
from patches import python, pylint
from zLOG import LOG, INFO
DISPLAY_BOOT_PROCESS = False

# We have a name conflict with source_reference and destination_reference,
# which are at the same time property accessors for 'source_reference'
# property, and category accessors (similar to getSourceValue().getReference())
# When this is set to True, those accessors will be the property accessors.
# At the time beeing, if it's set to False for document having both category
# and property, the result seem to be undefined.
SOURCE_DESTINATION_REFERENCE_LEGACY = True

# This is used to register all Document classes used in ERP5
# items are class names, values are class paths, e.g.:
#   'Person' -> 'Products.ERP5.Document.Person.Person'
document_class_registry = {}
# similarly for mixins
mixin_class_registry = {}

# For early phases of bootstrap (and future ZODB property sheets)
# ERP5Type.PropertySheet becomes a dynamic module that always
# returns a string. ERP5Type.PropertySheet.doesnotexist for example
# is 'doesnotexist'
# Later on, if a local property sheet is imported from a product,
# importLocalPropertySheet will load it as ERP5Type.PropertySheet.*
# This is mostly a backwards compatible mechanism, to ensure that
# old class definitions will still work with properties such as
#    property_sheets = (ERP5Type.PropertySheet.YYY, ... )
# after transforming 'YYY' into a ZODB property sheet
from dynamic.dynamic_module import registerDynamicModule
PropertySheet = registerDynamicModule('Products.ERP5Type.PropertySheet',
                                      lambda name: name)

# Switch(es) for ongoing development which require single code base

# Update ERP5 Globals
import sys, Permissions, os
from App.Common import package_home
this_module = sys.modules[ __name__ ]
product_path = package_home( globals() )
this_module._dtmldir = os.path.join( product_path, 'dtml' )
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
document_classes = updateGlobals( this_module,
                                  globals(),
                                  permissions_module=Permissions,
                                  is_erp5_type=1 )

import ZopePatch
import interfaces

import Products.Localizer # So that we make sure Globals.get_request is available

# allow our workflow definitions to be registered
import Products.ERP5Type.Workflow

def initialize( context ):
  # Import Product Components
  from Tool import (CacheTool, MemcachedTool, SessionTool,
                    TypesTool, WebServiceTool, PropertySheetTool,
                    ComponentTool, ActionsTool)
  import Document
  from Base import Base
  import XMLObject
  from ERP5Type import ERP5TypeInformation
  import CodingStyle
  # Define documents, classes, constructors and tools
  object_classes = ()
  content_constructors = ()
  content_classes = ( Base,
                      XMLObject.XMLObject,
                      ERP5TypeInformation )
  portal_tools = ( CacheTool.CacheTool,
                   MemcachedTool.MemcachedTool,
                   SessionTool.SessionTool,
                   TypesTool.TypesTool,
                   WebServiceTool.WebServiceTool,
                   PropertySheetTool.PropertySheetTool,
                   ComponentTool.ComponentTool,
                   ActionsTool.ActionsTool,
                  )
  # Do initialization step
  initializeProduct(context, this_module, globals(),
                         document_module = Document,
                         document_classes = document_classes,
                         object_classes = object_classes,
                         portal_tools = portal_tools,
                         content_constructors = content_constructors,
                         content_classes = content_classes)

  # Register our Workflow factories directly (if on CMF 2)
  Products.ERP5Type.Workflow.registerAllWorkflowFactories(context)
  # We should register local constraints at some point
  from Products.ERP5Type.Utils import initializeLocalConstraintRegistry
  if DISPLAY_BOOT_PROCESS:
    LOG('ERP5Type.__init__', INFO, 'initializeLocalConstraintRegistry')
  initializeLocalConstraintRegistry()
  # We should register local property sheets at some point
  from Products.ERP5Type.Utils import initializeLocalPropertySheetRegistry
  if DISPLAY_BOOT_PROCESS:
    LOG('ERP5Type.__init__', INFO, 'initializeLocalPropertySheetRegistry')
  initializeLocalPropertySheetRegistry()
  # We should register product classes at some point
  from Products.ERP5Type.InitGenerator import initializeProductDocumentRegistry
  if DISPLAY_BOOT_PROCESS:
    LOG('ERP5Type.__init__', INFO, 'initializeProductDocumentRegistry')
  initializeProductDocumentRegistry()
  # We should register local classes at some point
  from Products.ERP5Type.Utils import initializeLocalDocumentRegistry
  if DISPLAY_BOOT_PROCESS:
    LOG('ERP5Type.__init__', INFO, 'initializeLocalDocumentRegistry')
  initializeLocalDocumentRegistry()
  # We can now setup global interactors
  from Products.ERP5Type.InitGenerator import initializeProductInteractorRegistry
  if DISPLAY_BOOT_PROCESS:
    LOG('ERP5Type.__init__', INFO, 'initializeProductInteractorRegistry')
  initializeProductInteractorRegistry()
  # And local interactors
  from Products.ERP5Type.Utils import initializeLocalInteractorRegistry
  if DISPLAY_BOOT_PROCESS:
    LOG('ERP5Type.__init__', INFO, 'initializeLocalInteractorRegistry')
  initializeLocalInteractorRegistry()
  # We can now install all interactors
  from Products.ERP5Type.InitGenerator import installInteractorClassRegistry
  if DISPLAY_BOOT_PROCESS:
    LOG('ERP5Type.__init__', INFO, 'installInteractorClassRegistry')
  installInteractorClassRegistry()


from AccessControl.SecurityInfo import allow_module
from AccessControl.SecurityInfo import ModuleSecurityInfo

allow_module('Products.ERP5Type.Cache')
ModuleSecurityInfo('Products.ERP5Type.Utils').declarePublic(
    'sortValueList', 'convertToUpperCase', 'UpperCase',
    'convertToMixedCase', 'cartesianProduct', 'sleep', 'getCommonTimeZoneList',
    'int2letter', 'getMessageIdWithContext', 'getTranslationStringWithContext',
    'Email_parseAddressHeader', 'guessEncodingFromText',
    'isValidTALESExpression')

allow_module('Products.ERP5Type.Message')
ModuleSecurityInfo('Products.ERP5Type.Message').declarePublic('translateString')

allow_module('Products.ERP5Type.Error')
allow_module('Products.ERP5Type.Errors')
allow_module('Products.ERP5Type.JSONEncoder')
allow_module('Products.ERP5Type.Log')
ModuleSecurityInfo('Products.ERP5Type.JSON').declarePublic('dumps', 'loads')
ModuleSecurityInfo('Products.ERP5Type.Constraint').declarePublic('PropertyTypeValidity')
ModuleSecurityInfo('Products.ERP5Type.DiffUtils').declarePublic('DiffFile')
ModuleSecurityInfo('pprint').declarePublic('pformat', 'pprint')
ModuleSecurityInfo('Products.ERP5Type.XMLUtils').declarePublic('parseStream')

import zExceptions
ModuleSecurityInfo('zExceptions').declarePublic(*filter(
  lambda x: Exception in getattr(getattr(zExceptions, x), '__mro__', ()),
  dir(zExceptions)))

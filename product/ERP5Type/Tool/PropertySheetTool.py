##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import transaction

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Accessor import Translation
from Products.ERP5Type.Base import PropertyHolder
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

from Products.ERP5Type.dynamic.accessor_holder import AccessorHolderType

from zLOG import LOG, ERROR, INFO

class PropertySheetTool(BaseTool):
  """
  Provides a configurable registry of property sheets
  """
  id = 'portal_property_sheets'
  meta_type = 'ERP5 Property Sheet Tool'
  portal_type = 'Property Sheet Tool'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declarePublic('getTranslationDomainNameList')
  def getTranslationDomainNameList(self):
    return (['']+
            [object_.id
             for object_ in getToolByName(self, 'Localizer').objectValues()
             if object_.meta_type=='MessageCatalog']+
            [Translation.TRANSLATION_DOMAIN_CONTENT_TRANSLATION]
            )

  @staticmethod
  def _guessFilesystemPropertyPortalType(attribute_dict):
    """
    Guess the Portal Type of a filesystem-based Property Sheet from
    the attributes of the given property
    """
    for key in attribute_dict:
      if key.startswith('acqui') or \
         key in ('alt_accessor_id',
                 # Specific to 'content' type
                 'portal_type',
                 'translation_acquired_property'):
        return 'Acquired Property'

    return 'Standard Property'

  security.declareProtected(Permissions.ModifyPortalContent,
                            'createPropertySheetFromFilesystemClass')
  def createPropertySheetFromFilesystemClass(self, klass):
    """
    Create a new Property Sheet in portal_property_sheets from a given
    filesystem-based Property Sheet definition.
    """
    new_property_sheet = self.newContent(id=klass.__name__,
                                         portal_type='Property Sheet')

    types_tool = self.getPortalObject().portal_types

    for attribute_dict in getattr(klass, '_properties', []):
      # The property could be either a Standard or an Acquired
      # Property
      portal_type_class = types_tool.getPortalTypeClass(
        self._guessFilesystemPropertyPortalType(attribute_dict))

      # Create the new property and set its attributes
      portal_type_class.importFromFilesystemDefinition(new_property_sheet,
                                                       attribute_dict)

    for category in getattr(klass, '_categories', []):
      # A category may be a TALES Expression rather than a plain
      # string
      portal_type = isinstance(category, Expression) and \
        'Dynamic Category Property' or 'Category Property'

      portal_type_class = types_tool.getPortalTypeClass(portal_type)

      # Create the new category
      portal_type_class.importFromFilesystemDefinition(new_property_sheet,
                                                       category)

    return new_property_sheet

  security.declareProtected(Permissions.ManagePortal,
                            'createAllPropertySheetsFromFilesystem')
  def createAllPropertySheetsFromFilesystem(self, REQUEST=None):
    """
    Create Property Sheets in portal_property_sheets from _all_
    filesystem Property Sheets

    XXX: only meaningful for testing?
    """
    from Products.ERP5Type import PropertySheet

    # Get all the filesystem Property Sheets
    for name, klass in PropertySheet.__dict__.iteritems():
      if name[0] == '_':
        continue

      if name in self.portal_property_sheets.objectIds():
        self.portal_property_sheets.deleteContent(name)
        transaction.commit()

      LOG("Tool.PropertySheetTool", INFO,
          "Creating %s in portal_property_sheets" % repr(name))

      self.createPropertySheetFromFilesystemClass(klass)
      transaction.commit()

    if REQUEST is not None:
      return self.REQUEST.RESPONSE.redirect(
        '%s?portal_status_message=' \
        'Property Sheets successfully imported from filesystem to ZODB.' % \
        self.absolute_url())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportPropertySheetToFilesystemDefinitionTuple')
  def exportPropertySheetToFilesystemDefinitionTuple(self, property_sheet):
    """
    Export a given ZODB Property Sheet to its filesystem definition as
    tuple (properties, categories, constraints)

    XXX: Move this code and the accessor generation code (from Utils)
         within their respective documents
    """
    properties = []
    constraints = []
    categories = []

    for property in property_sheet.contentValues():
      portal_type = property.getPortalType()
      property_definition = property.exportToFilesystemDefinition()

      if portal_type == "Category Property" or \
         portal_type == "Dynamic Category Property":
        categories.append(property_definition)

      elif portal_type.endswith('Constraint'):
        constraints.append(property_definition)

      else:
        properties.append(property_definition)

    return (properties, categories, constraints)

  security.declarePrivate('createFilesystemPropertySheetAccessorHolder')
  def createFilesystemPropertySheetAccessorHolder(self, property_sheet):
    """
    Create a new accessor holder from the given filesystem Property
    Sheet (the accessors are created through a Property Holder)

    XXX: Workflows?
    XXX: Remove as soon as the migration is finished
    """
    property_holder = PropertyHolder(property_sheet.__name__)

    property_holder._properties = getattr(property_sheet, '_properties', [])
    property_holder._categories = getattr(property_sheet, '_categories', [])
    property_holder._constraints = getattr(property_sheet, '_constraints', [])

    return AccessorHolderType.fromPropertyHolder(
      property_holder,
      self.getPortalObject(),
      'erp5.filesystem_accessor_holder')

  security.declarePrivate('createZodbPropertySheetAccessorHolder')
  def createZodbPropertySheetAccessorHolder(self, property_sheet):
    """
    Create a new accessor holder from the given ZODB Property Sheet
    (the accessors are created through a Property Holder)
    """
    property_sheet_name = property_sheet.getId()
    definition_tuple = \
      self.exportPropertySheetToFilesystemDefinitionTuple(property_sheet)

    property_holder = PropertyHolder(property_sheet_name)

    # Prepare the Property Holder
    property_holder._properties, \
      property_holder._categories, \
      property_holder._constraints = definition_tuple

    return AccessorHolderType.fromPropertyHolder(
      property_holder,
      self.getPortalObject(),
      'erp5.accessor_holder')

  security.declareProtected(Permissions.ManagePortal,
                            'getPropertyAvailablePermissionList')
  def getPropertyAvailablePermissionList(self):
    """
    Return a sorted set of all the permissions useful for read/write
    permissions for properties of ZODB Property Sheets
    """
    return sorted(set([ value for key, value in Permissions.__dict__.iteritems() \
                        if key[0].isupper() ]))

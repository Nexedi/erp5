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
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

from zLOG import LOG, INFO, WARNING

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

  _merged_portal_type_dict = {
    'CategoryAcquiredExistence': 'Category Existence Constraint',
    'CategoryAcquiredMembershipArity': 'Category Membership Arity Constraint'}

  security.declareProtected(Permissions.ModifyPortalContent,
                            'createPropertySheetFromFilesystemClass')
  def createPropertySheetFromFilesystemClass(self, klass):
    """
    Create a new Property Sheet in portal_property_sheets from a given
    filesystem-based Property Sheet definition.
    """
    new_property_sheet_name = klass.__name__

    new_property_sheet = self.newContent(id=new_property_sheet_name,
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

    # Get filesystem Constraint names to be able to map them properly
    # to ZODB Constraint Portal Types as some filesystem constraint
    # names are 'NAMEConstraint' or 'NAME'
    from Products.ERP5Type import Constraint as FilesystemConstraint
    filesystem_constraint_class_name_list = [
      class_name for class_name in FilesystemConstraint.__dict__ \
      if class_name[0] != '_' ]

    # Mapping between the filesystem 'type' field and Portal Types ID
    portal_type_dict = {}

    for portal_type_id in types_tool.objectIds():
      if not portal_type_id.endswith(' Constraint'):
        continue

      constraint_class_name = portal_type_id.replace(' ', '')

      if constraint_class_name not in filesystem_constraint_class_name_list:
        constraint_class_name = constraint_class_name.replace('Constraint', '')

        if constraint_class_name not in filesystem_constraint_class_name_list:
          LOG("Tool.PropertySheetTool", WARNING,
              "PropertySheet %s: No matching Constraint found for Portal '%s'" % \
              (new_property_sheet_name, portal_type_id))

          continue

      portal_type_dict[constraint_class_name] = portal_type_id

    portal_type_dict.update(self._merged_portal_type_dict)

    for constraint in getattr(klass, '_constraints', ()):
      try:
        portal_type = portal_type_dict[constraint['type']]
      except KeyError:
        # TODO: Constraints without Portal Type yet (e.g. Constraints
        # which have not been migrated yet (within BTs or per-project
        # Products)) are simply *ignored* for now
        LOG("Tool.PropertySheetTool", WARNING,
            "Not migrating constraint %s to portal_property_sheets" % \
            constraint['type'])

        continue

      portal_type_class = types_tool.getPortalTypeClass(portal_type)

      # Create the new constraint
      portal_type_class.importFromFilesystemDefinition(new_property_sheet,
                                                       constraint)

    return new_property_sheet

  security.declareProtected(Permissions.ManagePortal,
                            'createAllPropertySheetsFromFilesystem')
  def createAllPropertySheetsFromFilesystem(self, erase_existing=False,
      REQUEST=None):
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
        if erase_existing:
          self.portal_property_sheets.deleteContent(name)
          transaction.commit()
        else:
          continue

      LOG("Tool.PropertySheetTool", INFO,
          "Creating %s in portal_property_sheets" % repr(name))
      self.createPropertySheetFromFilesystemClass(klass)
      transaction.commit()

    if REQUEST is not None:
      portal = self.getPortalObject()
      message = portal.Base_translateString('Property Sheets successfully'\
                                          ' imported from filesystem to ZODB.')
      return self.Base_redirect('view',
                                keep_items={'portal_status_message': message})

  security.declareProtected(Permissions.ManagePortal,
                            'getPropertyAvailablePermissionList')
  def getPropertyAvailablePermissionList(self):
    """
    Return a sorted set of all the permissions useful for read/write
    permissions for properties of ZODB Property Sheets
    """
    return sorted(set([ value for key, value in Permissions.__dict__.iteritems() \
                        if key[0].isupper() ]))

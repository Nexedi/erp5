##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.Core.Folder import Folder
from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import PropertyHolder
from Products.ERP5Type.dynamic.accessor_holder import AccessorHolderType
from Acquisition import aq_base

from zLOG import LOG, INFO, WARNING

class PropertySheet(Folder):
  """
  Define a Property Sheet for ZODB Property Sheets, which contains
  properties (such as Standard Property), categories (such as Category
  Property) and/or constraints (such as Property Existence Constraint)
  """
  meta_type = 'ERP5 Property Sheet'
  portal_type = 'Property Sheet'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declarePrivate('createAccessorHolder')
  def createAccessorHolder(self, expression_context, portal):
    """
    Create a new accessor holder from the Property Sheet
    """
    my_id = self.getId()
    __traceback_info__ = my_id
    accessor_holder = AccessorHolderType(my_id)

    self.applyOnAccessorHolder(accessor_holder, expression_context, portal)

    return accessor_holder

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

  # The following filesystem definitions have been merged into another
  # Portal Type
  _merged_portal_type_dict = {
    'CategoryAcquiredExistence': 'Category Existence Constraint',
    'CategoryAcquiredMembershipArity': 'Category Membership Arity Constraint'}

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importFromFilesystemDefinition')
  @classmethod
  def importFromFilesystemDefinition(cls, context, definition_class):
    """
    Create a new Property Sheet in the given context from a given
    filesystem-based Property Sheet definition
    """
    property_sheet_name = definition_class.__name__

    property_sheet = context.newContent(id=property_sheet_name,
                                        portal_type='Property Sheet')

    types_tool = context.getPortalObject().portal_types

    for attribute_dict in getattr(definition_class, '_properties', []):
      # The property could be either a Standard or an Acquired
      # Property
      portal_type_class = types_tool.getPortalTypeClass(
        cls._guessFilesystemPropertyPortalType(attribute_dict))

      # Create the new property and set its attributes
      portal_type_class.importFromFilesystemDefinition(property_sheet,
                                                       attribute_dict)

    for category in getattr(definition_class, '_categories', []):
      # A category may be a TALES Expression rather than a plain
      # string
      portal_type = isinstance(category, Expression) and \
        'Dynamic Category Property' or 'Category Property'

      portal_type_class = types_tool.getPortalTypeClass(portal_type)

      # Create the new category
      portal_type_class.importFromFilesystemDefinition(property_sheet,
                                                       category)

    constraint_list = getattr(definition_class, '_constraints', None)
    if constraint_list:
      # Mapping between the filesystem 'type' field and Portal Types ID
      portal_type_dict = {}
      for portal_type_id in types_tool.objectIds():
        if portal_type_id.endswith(' Constraint'):
          portal_type_dict[portal_type_id.replace(' ', '')] = portal_type_id

      portal_type_dict.update(cls._merged_portal_type_dict)

      for constraint in constraint_list:
        # Some filesystem Constraints does not end with 'Constraint', whereas
        # ZODB Constraint *must* have a Portal Type ending with
        # 'Constraint'.
        #
        # Previously, it was implemented through a mapping between Portal Type
        # and filesystem Constraint class name but this does not work when two
        # projects used Constraints within a shared bt5 which has already been
        # migrated for a project (thus filesystem Constraints have been
        # deleted) but not the other...
        constraint_type = constraint['type']
        if not constraint['type'].endswith('Constraint'):
          constraint_type += 'Constraint'

        try:
          portal_type = portal_type_dict[constraint_type]
        except KeyError:
          # TODO: Constraints without Portal Type yet (e.g. Constraints
          # which have not been migrated yet (within BTs or per-project
          # Products)) are simply *ignored* for now
          LOG("Tool.PropertySheetTool", WARNING,
              "Not migrating constraint %s to portal_property_sheets as "
              "the corresponding Portal Type could not be found"
              % constraint_type)
        else:
          portal_type_class = types_tool.getPortalTypeClass(portal_type)
          # Create the new constraint
          portal_type_class.importFromFilesystemDefinition(property_sheet,
                                                           constraint)

    return property_sheet

  security.declareProtected(Permissions.AccessContentsInformation,
                            'applyOnAccessorHolder')
  def applyOnAccessorHolder(self, accessor_holder, expression_context, portal):
    # Accessor generation used to first generate accessors for
    # properties, *then* accessors for categories only if the latter
    # accessors have not been defined by the former (by using
    # 'hasattr'). As the 'hasattr'es have been removed, the reverse
    # operation is performed to maintain backward-compatibility
    property_definition_list = []
    for property_definition in self.contentValues():
      if property_definition.getPortalType().endswith('Category Property'):
        property_definition_list.insert(0, property_definition)
      else:
        property_definition_list.append(property_definition)

    for property_definition in property_definition_list:
      __traceback_info__ = property_definition
      if getattr(aq_base(property_definition), 'applyOnAccessorHolder',
          None) is None:
        # Prevent implicit acquisition of this method when subobject doesn't
        # have one with same name, triggering an infinite recursion.
        # We raise a RuntimeError, to be consistent with infinit recursion
        # (to avoid regressions).
        raise RuntimeError('Malformed property definition %r on %s' % (
          property_definition, self.getPath()))
      try:
        property_definition.applyOnAccessorHolder(accessor_holder,
                                                  expression_context,
                                                  portal)
      except ValueError as e:
        LOG("ERP5Type.Core.PropertySheet", INFO,
            "Invalid property '%s' for Property Sheet '%s': %s" % \
            (property_definition.getId(), self.getId(), str(e)))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRecursivePortalTypeValueList')
  def getRecursivePortalTypeValueList(self):
    """
    Get all the Portal Types where this Property Sheet is used
    """
    portal = self.getPortalObject()
    property_sheet_id = self.getId()
    import erp5.portal_type
    portal_type_value_list = []
    for portal_type in portal.portal_types.contentValues():
      portal_type_class = getattr(erp5.portal_type, portal_type.getId())
      portal_type_class.loadClass()

      for klass in portal_type_class.mro():
        if (klass.__module__ == 'erp5.accessor_holder.property_sheet' and
            klass.__name__ == property_sheet_id):
          portal_type_value_list.append(portal_type)

    return portal_type_value_list

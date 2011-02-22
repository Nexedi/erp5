##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Accessor.Base import Getter as BaseGetter
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin

class StandardProperty(IdAsReferenceMixin('_property'), XMLObject):
  """
  Define an Acquired Property Document for a ZODB Property Sheet
  """
  meta_type = 'ERP5 Standard Property'
  portal_type = 'Standard Property'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (PropertySheet.SimpleItem,
                     PropertySheet.StandardProperty,
                     PropertySheet.TranslatableProperty)

  # Names mapping between filesystem to ZODB property, only meaningful
  # when importing a property from its filesystem definition
  _name_mapping_filesystem_to_zodb_dict = {'id': 'reference',
                                           'type': 'elementary_type',
                                           'default': 'property_default'}

  # ZODB name of attributes whose value is a TALES Expression string
  _expression_attribute_tuple = ('property_default',)

  # Define getters for the property. This is necessary for bootstrap
  # as a Standard Property is defined by Standard Properties which
  # also depends on Property Sheets defined by Standard Properties.
  #
  # There is no need to define the setter as this static definition of
  # the getter is only meaningful for the Standard Properties defined
  # within an Standard Property.
  getDescription = BaseGetter('getDescription', 'description', 'string',
                              default='')

  def getElementaryType(self):
    """
    Define this getter manually as it is not possible to rely on
    CategoryTool during the bootstrap
    """
    for category in self.__dict__.get('categories', ()):
      if category.startswith('elementary_type/'):
        return category.split('elementary_type/')[1]

    return getattr(self, 'elementary_type', None)

  getStorageId = BaseGetter('getStorageId', 'storage_id', 'string')

  getMultivalued = BaseGetter('getMultivalued', 'multivalued', 'boolean',
                              default=False)

  # Define as a TALES expression string, use for Expression
  # instanciation when exporting the property to the filesystem
  # definition
  getPropertyDefault = BaseGetter('getPropertyDefault', 'property_default',
                                  'string')

  getRange = BaseGetter('getRange', 'range', 'boolean', default=False)

  getPreference = BaseGetter('getPreference', 'preference', 'boolean',
                             default=False)

  getReadPermission = BaseGetter(
    'getReadPermission', 'read_permission', 'string',
    default=Permissions.AccessContentsInformation)

  getWritePermission = BaseGetter('getWritePermission',
                                  'write_permission',
                                  'string',
                                  default=Permissions.ModifyPortalContent)

  getTranslatable = BaseGetter('getTranslatable', 'translatable', 'boolean',
                               default=False)

  getTranslationDomain = BaseGetter('getTranslationDomain',
                                    'translation_domain',
                                    'string')

  @staticmethod
  def _getExpressionFromString(expression_string):
    """
    Get a TALES Expression instance from a string value
    """
    if expression_string is None:
      return None

    return Expression(expression_string)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportToFilesystemDefinition')
  def exportToFilesystemDefinition(self):
    """
    Return the filesystem definition of this ZODB property
    """
    property_default_value = self._getExpressionFromString(self.getPropertyDefault())

    reference = self.getReference()
    if reference:
      return {'id': reference,
              'description': self.getDescription(),
              'type': self.getElementaryType(),
              'storage_id': self.getStorageId(),
              'multivalued': self.getMultivalued(),
              'default': property_default_value,
              'range': self.getRange(),
              'preference': self.getPreference(),
              'read_permission': self.getReadPermission(),
              'write_permission': self.getWritePermission(),
              'translatable': self.getTranslatable(),
              'translation_domain': self.getTranslationDomain()}

  @classmethod
  def _convertFromFilesystemPropertyDict(cls, filesystem_property_dict):
    """
    Convert a property dict coming from a Property Sheet on the
    filesystem to a ZODB property dict
    """
    # Prepare a dictionnary of the ZODB property
    zodb_property_dict = {}

    for fs_property_name, value in filesystem_property_dict.iteritems():
      # Convert filesystem property name to ZODB if necessary
      zodb_property_name = \
          fs_property_name in cls._name_mapping_filesystem_to_zodb_dict and \
          cls._name_mapping_filesystem_to_zodb_dict[fs_property_name] or \
          fs_property_name

      # Convert existing TALES expression class or primitive type to a
      # TALES expression string
      if zodb_property_name in cls._expression_attribute_tuple:
        value = isinstance(value, Expression) and \
            value.text or 'python: ' + repr(value)

      zodb_property_dict[zodb_property_name] = value

    return zodb_property_dict

  security.declareProtected(Permissions.AccessContentsInformation,
                            'importFromFilesystemDefinition')
  @classmethod
  def importFromFilesystemDefinition(cls, context, filesystem_property_dict):
    """
    Set attributes from the filesystem definition of a property
    """
    return context.newContent(
      portal_type=cls.portal_type,
      **cls._convertFromFilesystemPropertyDict(filesystem_property_dict))

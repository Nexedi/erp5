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
from Products.ERP5Type.Core.StandardProperty import StandardProperty

class AcquiredProperty(StandardProperty):
  """
  Define an Acquired Property Document for a ZODB Property Sheet (an
  Acquired Property only brings new attributes to a Standard Property)
  """
  meta_type = 'ERP5 Acquired Property'
  portal_type = 'Acquired Property'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = StandardProperty.property_sheets + \
      (PropertySheet.AcquiredProperty,)

  # Filesystem-based name of attributes specific to 'content' type
  _content_type_attribute_tuple = ('portal_type',
                                   'acquired_property_id',
                                   'translation_acquired_property_id')

  # Add names specific to 'content' type (see StandardProperty)
  _name_mapping_filesystem_to_zodb_dict = \
      dict([ (name, 'content_' + name,) for name in _content_type_attribute_tuple ],
           **StandardProperty._name_mapping_filesystem_to_zodb_dict)

  # ZODB name of attributes whose value is a TALES Expression string
  _expression_attribute_tuple = \
      StandardProperty._expression_attribute_tuple + \
      ('acquisition_portal_type', 'content_portal_type')

  @staticmethod
  def _convertValueToTalesExpression(value):
    """
    Convert a string value to a TALES expression for attributes listed
    in '_expression_attribute_tuple'
    """
    if value is None:
      return None

    return Expression(value)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportToFilesystemDefinition')
  def exportToFilesystemDefinition(self):
    """
    Return the filesystem definition of this ZODB property
    """
    filesystem_property_dict = \
        StandardProperty.exportToFilesystemDefinition(self)

    filesystem_property_dict.update(
      {'acquisition_base_category': self.getAcquisitionBaseCategoryList(),
       'acquisition_object_id': self.getAcquisitionObjectIdList(),
       'acquisition_portal_type': self._convertValueToTalesExpression(self.getAcquisitionPortalType()),
       'acquisition_accessor_id': self.getAcquisitionAccessorId(),
       'alt_accessor_id': self.getAltAccessorIdList(),
       'acquisition_copy_value': self.getAcquisitionCopyValue(),
       'acquisition_mask_value': self.getAcquisitionMaskValue(),
       'portal_type': self._convertValueToTalesExpression(self.getContentPortalType()),
       'acquired_property_id': self.getContentAcquiredPropertyIdList(),
       'translation_acquired_property_id': self.getContentTranslationAcquiredPropertyIdList()})

    return filesystem_property_dict

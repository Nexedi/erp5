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
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import PropertyHolder
from Products.ERP5Type.dynamic.accessor_holder import AccessorHolderType

from zLOG import LOG, INFO

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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportToFilesystemDefinition')
  def exportToFilesystemDefinition(self):
    """
    Export the ZODB Property Sheet to its filesystem definition as a
    tuple (properties, categories, constraints)
    """
    properties = []
    constraints = []
    categories = []

    for item in self.contentValues():
      definition = item.exportToFilesystemDefinition()

      # If a category doesn't have a name yet or the constraint class
      # returned is None, then just skip it
      if definition is None:
        LOG("ERP5Type.Core.PropertySheet", INFO,
            "Skipping property with ID '%s' in Property Sheet '%s'" % \
            (item.getId(), self.getId()))

        continue

      portal_type = item.getPortalType()

      if portal_type == "Category Property" or \
         portal_type == "Dynamic Category Property":
        categories.append(definition)

      elif portal_type.endswith('Constraint'):
        constraints.append(definition)

      else:
        properties.append(definition)

    return (properties, categories, constraints)

  security.declarePrivate('createAccessorHolder')
  def createAccessorHolder(self):
    """
    Create a new accessor holder from the Property Sheet (the
    accessors are created through a Property Holder)
    """
    property_holder = PropertyHolder(self.getId())

    # Prepare the Property Holder
    property_holder._properties, \
      property_holder._categories, \
      property_holder._constraints = self.exportToFilesystemDefinition()

    return AccessorHolderType.fromPropertyHolder(
      property_holder,
      self.getPortalObject(),
      'erp5.accessor_holder')

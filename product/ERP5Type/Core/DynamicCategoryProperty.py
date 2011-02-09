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

class DynamicCategoryProperty(XMLObject):
  """
  Define a Dynamic Category Property Document for a ZODB Property
  Sheets (a dynamic category is defined by a TALES expression rather
  than a string and is being used by Item and Movement for example)
  """
  meta_type = 'ERP5 Dynamic Category Property'
  portal_type = 'Dynamic Category Property'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (PropertySheet.SimpleItem,
                     PropertySheet.Reference,
                     PropertySheet.DynamicCategoryProperty)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportToFilesystemDefinition')
  def exportToFilesystemDefinition(self):
    """
    Return the filesystem definition of the property
    """
    expression_string = self.getCategoryExpression()
    if expression_string is None:
      return None

    return Expression(expression_string)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'importFromFilesystemDefinition')
  @classmethod
  def importFromFilesystemDefinition(cls, context, category_expression):
    """
    Set the Expression text from a filesystem definition of a property
    """
    return context.newContent(portal_type=cls.portal_type,
                              category_expression=category_expression.text)

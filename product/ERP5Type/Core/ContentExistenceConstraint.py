##############################################################################
#
# Copyright (c) 2006-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Romain Courteaud <romain@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from Products.CMFCore.Expression import Expression
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet

class ContentExistenceConstraint(ConstraintMixin):
  """
  This constraint checks whether the given object contains at least
  one subobject. It also allows to filter the subobjects by their
  Portal Types.

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5Type.Constraint.ContentExistence
  instead).

  Note that the portal_type is now a TALES Expression, meaningful to
  be able to call a method returning a list of Portal Types.

  For example, if we would like to check whether the object contains
  subobjects whose Portal Types could be ("Foo", "Bar"), then we would
  create a 'Content Existence Constraint' within that Property Sheet
  and set 'Portal Types' to ("Foo", "Bar"), then set the 'Predicate'
  if necessary (known as 'condition' for filesystem Property Sheets).
  """
  meta_type = 'ERP5 Content Existence Constraint'
  portal_type = 'Content Existence Constraint'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.ContentExistenceConstraint,)

  def _checkConsistency(self, obj, fixit=0):
    """
    Checks that object contains at least one subobject and, if a list
    of Portal Type has been given, check their Portal Types
    """
    portal_type = self._getExpressionValue(obj,
                                           self.getConstraintPortalType())

    # If there is at least one subobject with the given Portal Type,
    # then return now
    if len(obj.contentValues(portal_type=portal_type)) > 0:
      return []

    # Otherwise, generate an error message
    mapping = {}
    if not portal_type:
      message_id = 'message_no_subobject'
    else:
      message_id = 'message_no_subobject_portal_type'

      from Products.ERP5Type.Message import Message
      mapping['portal_type'] = str(Message('erp5_ui', ' or ')).join(
          [str(Message('erp5_ui', pt)) for pt in portal_type])

    return [self._generateError(obj,
                                self._getMessage(message_id),
                                mapping)]

  _message_id_tuple = ('message_no_subobject',
                       'message_no_subobject_portal_type')

  @staticmethod
  def _convertFromFilesystemDefinition(portal_type=()):
    """
    @see ERP5Type.mixin.constraint.ConstraintMixin._convertFromFilesystemDefinition

    Filesystem definition example:
    { 'id'            : 'line',
      'description'   : 'Object have to contain a Line',
      'type'          : 'ContentExistence',
      'portal_type'   : ('Line', ),
    }
    """
    constraint_portal_type_str = isinstance(portal_type, Expression) and \
        portal_type.text or 'python: ' + repr(portal_type)

    yield dict(constraint_portal_type=constraint_portal_type_str)

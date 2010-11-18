##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Sebastien Robin <seb@nexedi.com>
#                         Jean-Paul Smets <jp@nexedi.com>
#                         Courteaud Romain <romain@nexedi.com>
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

from Products.ERP5Type.interfaces import IConstraint
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from zope.interface import implements
from Products.ERP5Type.Core.Predicate import Predicate
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import UpperCase

class ConstraintMixin(Predicate):
  """
  Mixin Constraint implementation (only relevant for ZODB Property
  sheets, use Products.ERP5Type.Constraint instead for filesystem
  Property Sheets) relying on Predicate
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  __allow_access_to_unprotected_subobjects__ = 1
  implements( IConstraint, )

  _message_id_list = []

  def _getMessage(self, message_id):
    """
    Get the message corresponding to this message_id.
    """
    return getattr(self, 'get' + UpperCase(message_id))()

  def _generateError(self, obj, error_message, mapping={}):
    """
    Generic method used to generate error in checkConsistency.
    """
    if error_message is not None:
      msg = ConsistencyMessage(self,
                               object_relative_url=obj.getRelativeUrl(),
                               message=error_message,
                               mapping=mapping)
      return msg

  security.declareProtected(Permissions.AccessContentsInformation,
                            'checkConsistency')
  def checkConsistency(self, obj, fixit=0, **kw):
    """
    Default method is to return no error.
    """
    errors = []
    return errors

  security.declareProtected(Permissions.AccessContentsInformation,
                            'fixConsistency')
  def fixConsistency(self, obj, **kw):
    """
    Default method is to call checkConsistency with fixit set to 1
    """
    return self.checkConsistency(obj, fixit=1, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportToFilesystemDefinition')
  def exportToFilesystemDefinition(self):
    """
    Return a temporary copy of the constraint object (with acquisition
    wrapping removed) in order to maintain compatibility and be able
    to use setDefaultProperties

    XXX: remove as soon as the code is stable
    """
    return self.asContext()

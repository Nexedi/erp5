##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from six import string_types as basestring
from Products.ERP5Type.Constraint import Constraint

class ContentExistence(Constraint):
  """
    This constraint class allows to check that an object contains at least one
    subobject.

    Configuration example:
    { 'id'            : 'line',
      'description'   : 'Object have to contain a Line',
      'type'          : 'ContentExistence',
      'portal_type'   : ('Line', ),
    },
  """

  _message_id_list = [ 'message_no_subobject',
                       'message_no_subobject_portal_type' ]

  message_no_subobject = "The document does not contain any subobject"
  message_no_subobject_portal_type = "The document does not contain any"\
                   " subobject of portal portal type ${portal_type}"

  def _checkConsistency(self, obj, fixit=0):
    """Checks that object contains a subobject.
    """
    from Products.ERP5Type.Message import Message
    error_list = []
    # Retrieve configuration values from PropertySheet (_constraints)
    portal_type = self.constraint_definition.get('portal_type', ())
    if not len(obj.contentValues(portal_type=portal_type)):
      # Generate error message
      mapping = {}
      message_id = 'message_no_subobject'
      if portal_type is not ():
        message_id = 'message_no_subobject_portal_type'
        # XXX maybe this could be factored out
        if isinstance(portal_type, basestring):
          portal_type = (portal_type, )
        mapping['portal_type'] = str(Message('erp5_ui', ' or ')).join(
            [str(Message('erp5_ui', pt)) for pt in portal_type])
      # Add error
      error_list.append(self._generateError(obj,
                          self._getMessage(message_id), mapping))
    return error_list


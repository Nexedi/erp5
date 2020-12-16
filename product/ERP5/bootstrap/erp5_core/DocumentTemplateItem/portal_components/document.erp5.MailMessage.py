##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
#                         Kevin Deldycke          <kevin@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.document.Event import Event

_MARKER = object()

class MailMessage(Event):
  """
  LEGACY

  The MailMessage class is deprecated. It is superceded by
  the Event class (for CRM events) and by the EmailDocument class
  (to store raw email messages).

  TODO: compatibility layer is required so that old MailMessage
  instance can mimic Event instances based on legacy data. This
  is required for example for old CRM implementations of ERP5.
  """

  meta_type       = 'ERP5 Mail Message'
  portal_type     = 'Mail Message'
  add_permission  = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.DublinCore
                    , PropertySheet.CategoryCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Event
                    , PropertySheet.MailMessage
                    )

  security.declareProtected(Permissions.AccessContentsInformation, 'getTextContent')
  def getTextContent(self, default=_MARKER):
    """
    Overload EmailDocument method to add backward compatibility layer
    """
    if getattr(self, 'body', None) is not None:
      return self.getBody(default)
    else:
      if default is _MARKER:
        return Event.getTextContent(self)
      else:
        return Event.getTextContent(self, default)


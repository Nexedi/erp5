##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.EmailDocument import EmailDocument

class AcknowledgeableMixin:
  """
  Mixin class for all documents that we can acknowledge
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'acknowledge')
  def acknowledge(self, **kw):
    """
      Define what we want to do with acknowledgment.

      Possibilities :
        - do nothing
        - add an Acknowledge document every time someone read
          an event corresponding to this ticket
        - we could even think to move the workflow forward
          when all event have been acknowledge

      Is the name buildAcknowledgement better ???
    """
    method = self._getTypeBasedMethod('acknowledge')
    if method is not None:
      return method(**kw)
    return None

  def hasAcknowledgementActivity(self, user_name=None):
    """
    We will check if there is some current activities running or not
    """
    tag = "%s_%s" % (user_name, self.getRelativeUrl())
    result = False
    # First look at activities, we check if an acknowledgement document
    # is under reindexing
    if self.portal_activities.countMessageWithTag(tag):
      result = True
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'isAcknowledged')
  def isAcknowledged(self, user_name=None):
    """
    Say if this ticket is already acknowledged or not by this user.
    """
    result = self.hasAcknowledgementActivity(user_name=user_name)
    if not result:
      # Check in the catalog if we can find an acknowledgement
      person_value = self.ERP5Site_getAuthenticatedMemberPersonValue(
                          user_name=user_name)
      if len(self.portal_catalog(portal_type='Acknowledgement',
                causality_relative_url=self.getRelativeUrl(),
                destination_relative_url=person_value.getRelativeUrl())) > 0:
        result = True
    return result

class Event(EmailDocument, Movement, AcknowledgeableMixin):
  """
    Event is the base class for all events in ERP5.

    Event objects include emails, phone calls,

    The purpose of an Event object is to keep track
    of the interface between the ERP and third parties.

    Events have a start and stop date.

    Events may contain files and local role definitions.
  """

  meta_type = 'ERP5 Event'
  portal_type = 'Event'
  isPortalContent = 1
  isRADContent = 1
  isDelivery = 1
  isMovement = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Document
                    , PropertySheet.DublinCore
                    , PropertySheet.Snapshot
                    , PropertySheet.Task
                    , PropertySheet.Url
                    , PropertySheet.TextDocument
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Event
                    , PropertySheet.Delivery
                    , PropertySheet.ItemAggregation
                   )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self):
    """Events are accountable 
    """
    return 1

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getQuantity')
  def getQuantity(self):
    """
      Quantity is set automatically on Events.
    """
    # Provide opportunity to script this
    return 1.

  security.declareProtected(Permissions.AccessContentsInformation,
                             'getExplanationValue')
  def getExplanationValue(self):
    """
      An event is it's own explanation
    """
    return self

  security.declareProtected(Permissions.UseMailhostServices, 'send')
  def send(self, from_url=None, to_url=None, reply_url=None, subject=None,
           body=None, attachment_format=None, attachment_list=None,
           download=False, **kw):
    """
      Make the send method overridable by typed based script
      so that special kinds of events can use a different gateway
      to send messages. This is useful for example to send
      faxes through fax server or to send letters by printing
      them to the printer or to send SMS through a custom 
      gateway. In the most usual case, sending will only consist
      in changing the destination.
    """
    send_script = self._getTypeBasedMethod('send')
    if send_script is None:
      return Event.inheritedAttribute('send')(
          self, from_url, to_url, reply_url, subject, body, attachment_format,
          attachment_list, download
          )
    return send_script(
        from_url, to_url, reply_url, subject, body, attachment_format, attachment_list,
        download, **kw
        )

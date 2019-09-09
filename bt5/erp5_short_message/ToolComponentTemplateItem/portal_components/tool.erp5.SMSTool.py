# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    François-Xavier Algrain <fxalgrain@tiolive.com>
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
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Permissions import ManagePortal

#from Products.ERP5ShortMessage import _dtmldir

class SMSTool(BaseTool):
  """
    This tool manages gadgets.

    It is used as a central point to manage gadgets (ERP5 or external ones)...
  """
  id = 'portal_sms'
  meta_type = 'ERP5 SMS Tool'
  portal_type = 'SMS Tool'

  # Declarative Security
  security = ClassSecurityInfo()
  security.declareProtected(ManagePortal, 'manage_overview')
  #manage_overview = DTMLFile('explainSMSTool', _dtmldir )

  security.declareProtected(ManagePortal, 'send')
  def send(self, text, recipient, sender, gateway_reference='default',
           document_relative_url=None, activate_kw=None):
    """Send the message

    gateway_reference: send message throught the gateway with this reference.
    document_relative_url (optional) : allows to send back result to a document
    activate_kw (optional) : Call SMSTool_afterSend if founded in activity with
                            message_id and document_relative_url
    """

    gateway = self._findGateway(gateway_reference)

    message_id = gateway.send(
            text=text,
            recipient=recipient,
            sender=sender)

    if getattr(self, 'SMSTool_afterSend'):
      # We need to use activities in order to avoid any conflict
      send_activate_kw = {'activity':'SQLQueue'}
      if activate_kw is not None:
        send_activate_kw.update(**activate_kw)
      self.activate(**send_activate_kw).SMSTool_afterSend(
              message_id,
              document_relative_url=document_relative_url,
              gateway_relative_url=gateway.getRelativeUrl())

  security.declareProtected(ManagePortal, 'getMessageStatus')
  def getMessageStatus(self,message_id, gateway_reference='default'):

    gateway = self._findGateway(gateway_reference)
    return gateway.getMessageStatus(message_id)

  security.declarePublic('isSendByTitleAllowed')
  def isSendByTitleAllowed(self, gateway_reference='default'):
    """Define the support or not to use the title of the telephone instead of
        the number when send a message."""
    gateway = self._findGateway(gateway_reference)
    return gateway.isTitleMode()


  def _findGateway(self, gateway_reference='default'):
    """Search the gateway by its reference"""

    result = self.getPortalObject().portal_catalog.unrestrictedSearchResults(
        parent_uid=self.getUid(),
        reference=gateway_reference)
    if result:
      result, = result # ensure only one gateway with this reference
      return result.getObject()
    raise ValueError("Impossible to find gateway with reference %s" % gateway_reference)


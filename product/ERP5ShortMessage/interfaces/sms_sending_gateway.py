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

from zope.interface import Interface

class ISmsSendingGateway(Interface):
  """SMS Gateway allow sending Short Messages to phones.
  """

  def send(text, recipient, sender):
    """Send a message.
    
    * text: the message as an utf-8 encoded string
    * recipient: relative URL of recipient person or organisation. Recipient must have a defaut mobile phone
    * sender: relative URL of sender person or organisation.

    On most implementations, returns a message-id that can be later passed to
    getMessageStatus to check the status of the message.
    """

  def getMessageStatus(message_id):
    """Retrieve the status of a message
       Should return x in ['sent', 'delivered', 'queued', 'failed']"""

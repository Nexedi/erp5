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


class ISmsGateway(Interface):

    def send(text, recipient,
             sender=None, sender_title=None,
             message_type="text", test=False, **kw):
      """Send a message.
      
      TODO: write

      TODO: is getAllowedMessageType part of this API ?
      shouldn't we rely on content_type ? ( text/plain -> SMS, text/html -> MMS ? )
      """

    def receive(REQUEST):
      """Public handler to push notification from the gateway"""

    def getAllowedMessageType():
      """List of all allowed message type when sending a message."""

    def getMessageStatus(message_id):
      """Retrieve the status of a message
         Should return x in ['sent', 'delivered', 'queued', 'failed']"""

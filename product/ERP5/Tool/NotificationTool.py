##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

import time
import threading

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir

from zLOG import LOG, INFO

class NotificationTool(BaseTool):
  """
    This tool manages notifications.

    It is used as a central point to send messages from one
    user to one or many users. The purpose of the tool
    is to provide an API for sending messages which is
    independent on how messages are actually going to be
    sent and when.

    It is also useful to send messages without having to
    write always the same piece of code (eg. lookup the user,
    lookup its mail, etc.).

    This early implementation only provides asynchronous
    email sending.

    Future implementations may be able to lookup user preferences
    to decide how and when to send a message to each user.
  """
  id = 'portal_notifications'
  meta_type = 'ERP5 Notification Tool'
  portal_type = 'Notification Tool'

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainNotificationTool', _dtmldir )

  security.declareProtected(Permissions.UseMailhostServices, 'sendMessage')
  def sendMessage(self, sender=None, recipient=None, subject=None, message=None, attachment_list=None):
    """
      This method provides a common API to send messages to users
      from object actions of worflow scripts.

      sender -- a string or a Person object

      recipient -- a string or a Person object
                   a list of thereof

      subject -- the subject of the message

      message -- the text of the message (already translated)

      attachment_list -- attached documents (optional)
    """
    catalog_tool = getToolByName(self, 'portal_catalog')

    # Change all strings to object values
    if isinstance(sender, basestring):
      sender = catalog_tool(portal_type='Person', reference=sender)[0]

    email_from_address = None
    if sender is not None:
      email_value = sender.getDefaultEmailValue()
      if email_value is not None:
        email_from_address = email_value.asText()
    if not email_from_address:
      # If we can not find a from address then
      # we fallback to portal values
      portal = self.getPortalObject()
      email_from_address = portal.email_from_address

    # To is a list - let us find all members
    if isinstance(recipient, basestring):
      recipient = [recipient]
    to_list = []
    for user in recipient:
      user_value = catalog_tool(portal_type='Person', reference=user)[0]
      if user_value is not None:
        to_list.append(user_value)

    # Default implementation is to send an active message to everyone
    for person in to_list:
      email_value = person.getDefaultEmailValue()
      if email_value is not None:
        email_value.activate(activity='SQLQueue').send(
                                    from_url=email_from_address,
                                    to_url=email_value.asText(),
                                    subject=subject,
                                    msg=message,
                                    attachment_list=attachment_list)
    
    # Future implemetation could consist in implementing
    # policies such as grouped notification (per hour, per day,
    # per week, etc.) depending on user preferences. It
    # also add some urgency and selection of notification
    # tool (ex SMS vs. email)

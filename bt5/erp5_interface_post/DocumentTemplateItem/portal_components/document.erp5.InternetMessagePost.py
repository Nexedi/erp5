##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions
from erp5.component.document.Item import Item
from erp5.component.mixin.MailMessageMixin import MailMessageMixin

import email

class InternetMessagePost(Item, MailMessageMixin):

  meta_type = 'ERP5 Internet Message Post'
  portal_type = 'Internet Message Post'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)


  def _getMessage(self):
    return email.message_from_string(self.getData().decode())

  security.declareProtected(Permissions.AccessContentsInformation, 'stripMessageId')
  def stripMessageId(self, message_id):
    """
    In rfc5322 headers, message-ids may follow the syntax "<msg-id>" in
    order to permit the dot-atom-text form. Thus those "<" and ">" should
    be stripped when working with message-ids
    """
    if message_id:
      if message_id[0] == '<':
        message_id = message_id[1:]
      if message_id[-1] == '>':
        message_id = message_id[:-1]
    return message_id

  security.declareProtected(Permissions.AccessContentsInformation, 'getReference')
  def getReference(self):
    return self.stripMessageId(self.getSourceReference())

  def _setReference(self, value):
    """
    Raise if given value is different from current value,
    as reference of an Internet Message Post is read-only
    (if _setReference is called, it means some form field
    hasn't been set read-only)
    """
    if value != self.getReference():
      raise ValueError("Reference is read-only and can't be changed")
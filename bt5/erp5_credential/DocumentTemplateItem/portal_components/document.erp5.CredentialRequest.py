##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien MORIN <fabien@nexedi.com>
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
from Products.ERP5.Document.Ticket import Ticket
from erp5.component.mixin.EncryptedPasswordMixin import EncryptedPasswordMixin

class CredentialRequest(Ticket, EncryptedPasswordMixin):
    """
    """

    meta_type = 'ERP5 Credential Request'
    portal_type = 'Credential Request'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.CredentialQuestion
                      , PropertySheet.DefaultCredentialQuestion
                      , PropertySheet.Login
                      , PropertySheet.Codification
                      , PropertySheet.Person
                      , PropertySheet.Reference
                      , PropertySheet.Url
                      )

    def checkUserCanChangePassword(self):
      # every body can change a password of a credential request as annonymous
      # should be able to do it
      pass

    def checkPasswordValueAcceptable(self, value):
      # all passwords are acceptable on Credential Request
      pass

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTitle')
    def getTitle(self, **kw):
      """
        Returns the title if it exists or a combination of
        first name and last name
      """
      if self.title == '':
        name_list = []
        if self.getFirstName() not in (None, ''):
          name_list.append(self.getFirstName())
        if self.getLastName() not in (None, ''):
          name_list.append(self.getLastName())
        if name_list:
          return ' '.join(name_list)
        return self.getReference() or self.getId()
      else:
        return self.title

    security.declareProtected(Permissions.AccessContentsInformation,
                              'hasTitle')
    def hasTitle(self):
      return self.title or self.hasFirstName() or self.hasLastName()


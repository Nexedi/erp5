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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5.mixin.encrypted_password import EncryptedPasswordMixin
from Products.ERP5.mixin.login_account_provider import LoginAccountProviderMixin
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.XMLObject import XMLObject

class Login(XMLObject, LoginAccountProviderMixin, EncryptedPasswordMixin):
  meta_type = 'ERP5 Login'
  portal_type = 'Login'
  add_permission = Permissions.AddPortalContent

  zope.interface.implements(interfaces.INode)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Reference
                    , PropertySheet.Login
                    , PropertySheet.LoginConstraint
                    )

  def _setReference(self, value):
    """
      Set the user id. This method is defined explicitly, because:

      - we want to apply a different permission

      - we want to prevent duplicated user ids, but only when
        PAS _AND_ ERP5UserManager are used
    """
    activate_kw = {}
    portal = self.getPortalObject()
    if value:
      # Encode reference to hex to prevent uppercase/lowercase conflict in
      # activity table (when calling countMessageWithTag)
      activate_kw['tag'] = tag = \
        self.getPortalType() + '_setReference_' + value.encode('hex')
      # Check that there no existing user
      erp5_users = portal.acl_users.erp5_users
      login = erp5_users.getLoginObject(value, self.getPortalType())
      if login is not None and login != self and \
          login != self.getParentValue():
        raise RuntimeError, 'user id %s already exist' % (value,)
      # Check that there is no reindexation related to reference indexation
      if portal.portal_activities.countMessageWithTag(tag):
        raise RuntimeError, 'user id %s already exist' % (value,)

      # Prevent concurrent transaction to set the same reference on 2
      # different persons
      self.getParentValue().getParentValue().serialize()
      # Prevent to set the same reference on 2 different persons during the
      # same transaction
      transactional_variable = getTransactionalVariable()
      if tag in transactional_variable:
        raise RuntimeError, 'user id %s already exist' % (value,)
      else:
        transactional_variable[tag] = None

    self._baseSetReference(value)
    self.reindexObject(activate_kw=activate_kw)
    # invalid the cache for ERP5Security
    portal_caches = portal.portal_caches
    portal_caches.clearCache(cache_factory_list=('erp5_content_short', ))

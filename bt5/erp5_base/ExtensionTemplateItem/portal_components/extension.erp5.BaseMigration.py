##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#          Ivan Tyagov <ivan@nexedi.com>
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

import erp5
import re
from Products.ERP5.Extensions.CheckPortalTypes import changeObjectClass

def migrateToEmbeddedFile(self, force=0):
  """Migrate all embedded "File" and "Image"
     objects to an unified "Embedded File
  """
  portal_type = self.getPortalType()
  if portal_type in ('File', 'Image') and self.getValidationState()=='embedded':
    embedded_type = 'Embedded File'
    container = self.getParentValue()
    if force == 1:
      changeObjectClass(container, self.id, getattr(erp5.portal_type, embedded_type))
    return '%s: %s -> %s' % (self.getRelativeUrl(), portal_type, embedded_type),

def migrateToLogin(self):
  assert self.getPortalType() == 'Person'
  if len(self.objectValues(portal_type=self.getPortalObject().getPortalLoginTypeList())):
    # already migrated
    return
  reference = self.getReference()
  if not reference:
    # no login is required
    return
  login_list = []
  if re.match(r'^fb_\d+$', reference):
    login = self.newContent(
      portal_type='Facebook Login',
      reference=reference,
    )
    login_list.append(login)
  elif re.match(r'^go_\d+$', reference):
    login = self.newContent(
      portal_type='Google Login',
      reference=reference,
    )
    login_list.append(login)
  elif re.match('^bid_[^@]+@[^@]+$', reference):
    login = self.newContent(
      portal_type='Persona Login',
      reference=reference,
    )
    login_list.append(login)
  if self.hasPassword():
    login = self.newContent(
      portal_type='ERP5 Login',
      reference=reference,
    )
    login._setEncodedPassword(self.getPassword())
    login_list.append(login)
  if not login_list:
    login = self.newContent(
      portal_type='ERP5 Login',
      reference=reference,
    )
    login_list.append(login)
  for login in login_list:
    login.validate()

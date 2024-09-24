##############################################################################
#
# Copyright (c) 2002-2024 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase

class TestAntivirus(SecurityTestCase):

  def test_document_owner_cant_declare_safe(self):
    uf = self.getPortal().acl_users
    user = "someuser"
    uf._doAddUser(user, "", ["Author"], [])

    # Create a file as user
    self.loginByUserName(user)
    file_value = self.portal.document_module.newContent(
      portal_type="File"
    )

    file_value.setSuspect()

    # Assert user has Owner and can edit the document, otherwise the test is pointless
    self.failUnlessUserHaveRoleOnDocument(user, "Owner", file_value)
    self.failUnlessUserHavePermissionOnDocument("Modify portal content", user, file_value)

    # Test that the user can't declare safe a suspect document
    self.failIfUserCanPassWorkflowTransition(user, "set_safe", file_value)

    # Test that the user can't declare safe an infected document
    self.login()
    file_value.setInfected()

    self.failUnlessUserHaveRoleOnDocument(user, "Owner", file_value)
    self.failUnlessUserHavePermissionOnDocument("Modify portal content", user, file_value)
    self.failIfUserCanPassWorkflowTransition(user, "set_safe", file_value)

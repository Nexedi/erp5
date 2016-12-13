# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho <lucas@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################


from AccessControl.SecurityManagement import newSecurityManager


class ShaSecurityMixin(object):
  """
    ShaSecurity - Mixin Class
  """

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.lucas_user = self.createUser('lucas', 'lucas').Person_getUserId()

    self.toto_user = self.createUser('toto', 'toto').Person_getUserId()

  def createUser(self, reference, password):
    """
      Create a user with basic information
    """
    person = self.portal.portal_catalog.getResultValue(portal_type='Person', reference=reference)
    if person is None:
      person = self.portal.person_module.newContent(portal_type='Person')
      person.edit(first_name=reference,
                  reference=reference)
      login = person.newContent(
        portal_type='ERP5 Login',
        reference=reference,
        password=password,
      )
      login.validate()
      self.tic()

    create = True
    group=self.group
    for assignment in person.contentValues(portal_type="Assignment"):
      if assignment.getGroup() == self.group:
        create = False

    if create:
      assignment = person.newContent(portal_type='Assignment')
      assignment.edit(group=self.group)
      assignment.open()
      self.tic()

    return person

  def changeUser(self, user_id):
    """
      Change the current user to user_id
    """
    user_folder = self.getPortal().acl_users
    user = user_folder.getUserById(user_id).__of__(user_folder)
    newSecurityManager(None, user)



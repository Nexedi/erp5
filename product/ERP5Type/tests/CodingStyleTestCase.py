# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Jean-Paul Smets <jp@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Testing import ZopeTestCase
from Acquisition import aq_base

class CodingStyleTestCase(ERP5TypeTestCase):
  """Test case to test coding style in business templates.

  Subclasses must override:
    * getBusinessTemplateList to list business template to install.
    * getTestedBusinessTemplateList to list business templates to test.
  """
  manager_username = 'zope'
  manager_password = 'zope'
  website_id = 'test'

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    Override this method in implementation class.
    """
    raise NotImplementedError

  def getTestedBusinessTemplateList(self):
    """
    Return the list of business templates to be
    checked for consistency. By default, return
    the last business template of the
    list of installed business templates.
    """
    return self.getBusinessTemplateList()[-1:]

  def afterSetUp(self):
    portal = self.portal

    uf = portal.acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    self.loginByUserName(self.manager_username)


  def test_SkinCodingStyle(self):
    """
    Find all skin items of business templates to be checked
    and gather all consistency messages.
    """
    # Find the list if skins to test - we only test the last business template
    portal_templates = self.portal.portal_templates
    skin_id_list = []
    for business_template in portal_templates.contentValues():
      if business_template.getTitle() in self.getTestedBusinessTemplateList():
        skin_id_list.extend(business_template.getTemplateSkinIdList())

    # Init message list
    message_list = []

    # Test skins
    portal_skins = self.portal.portal_skins
    for skin_id in skin_id_list:
      skin = portal_skins[skin_id]
      for document in skin.objectValues():
        if getattr(aq_base(document), 'checkConsistency', None) is not None:
          message_list.extend(document.checkConsistency())

    # Return results
    if len(message_list):
      raise self.failureException('\n'.join(map(lambda x: repr(x), message_list)))

  def test_PythonSourceCode(self):
    """test python script from the tested business templates.

    reuses BusinessTemplate_getPythonSourceCodeMessageList from erp5_administration
    """
    if 'erp5_administration' not in self.getBusinessTemplateList():
      self.skipTest('erp5_administration needs be installed to check python source code')

    self.maxDiff = None
    for business_template in self.portal.portal_templates.contentValues():
      if business_template.getTitle() in self.getTestedBusinessTemplateList():
        self.assertEqual([], business_template.BusinessTemplate_getPythonSourceCodeMessageList())


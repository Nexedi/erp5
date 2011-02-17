##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                     Ivan Tyagov <ivan@nexedi.com>
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

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
import transaction

class TestKM(ERP5TypeTestCase):
  """Test Knowledge Management  """

  website_id = 'km_test'

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_jquery',
            'erp5_jquery_ui',
            'erp5_knowledge_pad',
            'erp5_web',
            'erp5_trade',
            'erp5_pdm',
            'erp5_project',
            'erp5_ingestion',
            'erp5_dms',
            'erp5_km', )

  def getTitle(self):
    return "Knowledge Management"

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    self.website = self.setupWebSite(skin_selection_name='KM',
                                     container_layout='erp5_km_minimal_layout',
                                     content_layout='erp5_km_minimal_content_layout',
                                     custom_render_method_id='WebSite_viewKnowledgePad',
                                     layout_configuration_form_id='WebSection_viewKMMinimalThemeConfiguration')
    self.websection = self.website.newContent(portal_type='Web Section')

  def setupWebSite(self, **kw):
    """
      Setup Web Site
    """
    portal = self.getPortal()

    # create website
    if hasattr(portal.web_site_module, self.website_id):
      portal.web_site_module.manage_delObjects(self.website_id)
    website = portal.web_site_module.newContent(portal_type = 'Web Site',
                                                          id = self.website_id,
                                                          **kw)
    transaction.commit()
    self.tic()
    return website

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('ivan', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('ivan').__of__(uf)
    newSecurityManager(None, user)

  def changeSkin(self, skin_name):
    """
      Change current Skin
    """
    request = self.app.REQUEST
    self.getPortal().portal_skins.changeSkin(skin_name)
    request.set('portal_skin', skin_name)

  def test_01_AssignedMembersToProject(self):
    """ Test assigned members to a project. Project is defined in a Web Section  """
    portal = self.getPortal()
    websection = self.websection

    # change to KM skins which is defined in erp5_km
    self.changeSkin('KM')

    assigned_member_list = websection.WebSection_searchAssignmentList(portal_type='Assignment')
    self.assertEquals(0, len(websection.WebSection_searchAssignmentList(portal_type='Assignment')))
    project = portal.project_module.newContent(portal_type='Project', \
                                               id='test_project')
    another_project = portal.project_module.newContent(portal_type='Project', \
                                                       id='another_project')
    # set websection to this project
    websection.edit(membership_criterion_base_category = ['destination_project'],
                    membership_criterion_category=['destination_project/%s' \
                      %project.getRelativeUrl()])
    # create person and assigned it to this project
    person = portal.person_module.newContent(portal_type='Person')
    assignment = person.newContent(portal_type= 'Assignment',
                                   destination_project = project.getRelativeUrl())
    another_assignment = person.newContent(portal_type= 'Assignment',
                                   destination_project = another_project.getRelativeUrl())
    assignment.open()
    self.stepTic()

    self.changeSkin('KM')

    self.assertEquals(1,\
      len( websection.WebSection_searchAssignmentList(portal_type='Assignment')))
    self.assertEquals(1,\
      len( websection.WebSection_countAssignmentList(portal_type='Assignment')))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestKM))
  return suite

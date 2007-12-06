##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
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

import unittest
import os

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from glob import glob

try:
  from transaction import get as get_transaction
except ImportError:
  pass

#
# Test Setting
#
INSTANCE_HOME = os.environ['INSTANCE_HOME']
bt5_base_path = os.environ.get('erp5_tests_bt5_path',
                               os.path.join(INSTANCE_HOME, 'bt5'))

# dependency order
target_business_templates = (
  'erp5_base',
  'erp5_trade',

  'erp5_pdf_editor',
  'erp5_pdf_style',
  'erp5_pdm',
  'erp5_accounting',
  'erp5_invoicing',

  'erp5_apparel',

##   'erp5_banking_core',
##   'erp5_banking_cash',
##   'erp5_banking_check',
##   'erp5_banking_inventory',

  'erp5_budget',

  'erp5_commerce',

  'erp5_consulting',

  'erp5_crm',

  'erp5_web',
  'erp5_dms',

  'erp5_forge',

  'erp5_immobilisation',

  'erp5_item',

  'erp5_mrp',

  'erp5_payroll',

  'erp5_project',

  'erp5_calendar',
)


class TestXHTML(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "XHTML Test"

  def getBusinessTemplateList(self):
    """  """
    return target_business_templates

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.login()
    self.enableDefaultSitePreference()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def enableDefaultSitePreference(self):
    portal_preferences = getToolByName(self.portal, 'portal_preferences')
    portal_workflow = getToolByName(self.portal, 'portal_workflow')
    default_site_preference = portal_preferences.default_site_preference
    portal_workflow.doActionFor(default_site_preference, 'enable_action')

  def test_deadProxyFields(self):
    # check that all proxy fields defined in business templates have a valid
    # target
    skins_tool = self.portal.portal_skins
    for field_path, field in skins_tool.ZopeFind(
              skins_tool, obj_metatypes=['ProxyField'], search_sub=1):
      self.assertNotEqual(None, field.getTemplateField(),
          '%s\nform_id:%s\nfield_id:%s\n' % (field_path,
                                             field.get_value('form_id'),
                                             field.get_value('field_id')))



def validate_xhtml(source):
  import popen2
  stdout, stdin, stderr = popen2.popen3('/usr/bin/tidy -e -q -utf8')
  stdin.write(source)
  stdin.close()
  for i in stderr:
    data = i.split(' - ')
    if len(data) >= 2:
      if data[1].startswith('Error: '):
        return False
  return True


def makeTestMethod(module_id, portal_type, view_name):
  def testMethod(self):
    module = getattr(self.portal, module_id)
    content = module.newContent(portal_type=portal_type)
    view = getattr(content, view_name)
    self.assert_(validate_xhtml(view()))
  return testMethod


def addTestMethodDynamically():
  from Products.ERP5.tests.utils import BusinessTemplateInfoTar
  from Products.ERP5.tests.utils import BusinessTemplateInfoDir
  for i in target_business_templates:
    business_template = os.path.join(bt5_base_path, i)

    # Look for business templates, like in ERP5TypeTestCase, they can be:
    #  .bt5 files in $INSTANCE_HOME/bt5/
    #  directories in $INSTANCE_HOME/
    #  directories in $INSTANCE_HOME/bt5/*/
    if not ( os.path.exists(business_template) or
        os.path.exists('%s.bt5' % business_template)):
      # try in $INSTANCE_HOME/bt5/*/
      business_template_glob_list = glob('%s/*/%s' % (bt5_base_path, i))
      if business_template_glob_list:
        business_template = business_template_glob_list[0]

    if os.path.isdir(business_template):
      business_template_info = BusinessTemplateInfoDir(business_template)
    elif os.path.isfile(business_template+'.bt5'):
      business_template_info = BusinessTemplateInfoTar(business_template+'.bt5')
    else:
      raise KeyError, "Can't find the business template: %s" % i

    for module_id, module_portal_type in business_template_info.modules.items():
      for portal_type in business_template_info.allowed_content_types.get(
        module_portal_type, ()):
        for action_information in business_template_info.actions[portal_type]:
          if (action_information['category']=='object_view' and
              action_information['visible']==1 and
              action_information['text'].startswith('string:${object_url}/') and
              len(action_information['text'].split('/'))==2):
            view_name = action_information['text'].split('/')[-1]
            method = makeTestMethod(module_id, portal_type, view_name)
            method_name = 'test%s%s' % (portal_type, view_name)
            setattr(TestXHTML, method_name, method)

addTestMethodDynamically()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestXHTML))
  return suite

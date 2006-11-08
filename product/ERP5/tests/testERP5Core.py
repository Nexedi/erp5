##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors. 
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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

#
# Skeleton ZopeTestCase
#

from random import randint
import os
import sys
import unittest
import time

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from zExceptions import BadRequest
from Products.ERP5Type import product_path
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Tool.ClassTool import _aq_reset

class TestERP5Core(ERP5TypeTestCase):

  run_all_test = 1
  quiet = 1

  def getTitle(self):
    return "ERP5Core"

  def getBusinessTemplateList(self):
    """
    """
    return tuple()

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

#  def enableLightInstall(self):
#    """
#    You can override this. 
#    Return if we should do a light install (1) or not (0)
#    """
#    return 1
#
#  def enableActivityTool(self):
#    """
#    You can override this.
#    Return if we should create (1) or not (0) an activity tool.
#    """
#    return 1

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()
    self.portal = self.getPortal()
#    portal = self.getPortal()
#    self.category_tool = self.getCategoryTool()
#    portal_catalog = self.getCatalogTool()
    #portal_catalog.manage_catalogClear()
#    self.createCategories()

  def test_01_ERP5Site_createModule(self, quiet=quiet, run=run_all_test):
    """
      Test that a module is created when ERP5Site_createModule is given the
      strict minimum number of arguments.
      A created module is composed of :
       - the module itself, directly in the portal object
       - a skin folder, directly in the skins tool
       - a portal type for the module
       - a portal type for the objects which can be contained in the module

      TODO: check more behaviours of the creation script, like skin priority, ...
    """
    if not run: return

    module_portal_type='UnitTest Module'
    portal_skins_folder='erp5_unittest'
    object_portal_type='UnitTest'
    object_title='UnitTest'
    module_id='unittest_module'
    module_title='UnitTests'
    
    self.assertEqual(getattr(self.portal.hasObject, module_id, None), None)
    self.assertEqual(getattr(self.portal.portal_skins, portal_skins_folder, None), None)
    self.assertEqual(getattr(self.portal.portal_types, module_portal_type, None), None)
    self.assertEqual(getattr(self.portal.portal_types, object_portal_type, None), None)
    self.portal.ERP5Site_createModule(module_portal_type=module_portal_type,
                                      portal_skins_folder=portal_skins_folder,
                                      object_portal_type=object_portal_type,
                                      object_title=object_title,
                                      module_id=module_id,
                                      module_title=module_title)
    self.assertNotEqual(getattr(self.portal, module_id, None), None)
    self.assertNotEqual(getattr(self.portal.portal_skins, portal_skins_folder, None), None)
    self.assertNotEqual(getattr(self.portal.portal_types, module_portal_type, None), None)
    #self.assertEqual(self.portal.portal_types[module_portal_type].title, module_title)
    self.assertNotEqual(getattr(self.portal.portal_types, object_portal_type, None), None)
    #self.assertEqual(self.portal.portal_types[object_portal_type].title, object_title)
  
  def test_01_Bug_446(self, quiet=quiet, run=run_all_test):
    """
      Test that Manage members is not an entry in the My Favourites menu.
    """
    if not run: return
    portal_action = getattr(self.getPortal(), 'portal_actions', None)
    global_action_list = portal_action.listFilteredActionsFor()['global']
    action_name_list = []
    for action in global_action_list:
      action_name_list.append(action['title'])

    self.assertTrue('Create Module' in action_name_list)

    for action_name in action_name_list:
      self.assertNotEqual(action_name, "Manage Members")
      self.assertNotEqual(action_name, "Manage members")

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestERP5Core))
        return suite


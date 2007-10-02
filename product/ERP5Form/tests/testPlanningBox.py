##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Rafael Monnerat <rafael@nexedi.com>
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

import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Testing import ZopeTestCase
from Products.ERP5Type.Utils import get_request
from Products.ERP5Type.tests.utils import createZODBPythonScript
from ZPublisher.HTTPRequest import FileUpload
from StringIO import StringIO
from Products.ERP5Form.Selection import Selection
from DateTime import DateTime

class DummyFieldStorage:
  """A dummy FieldStorage to be wrapped in a FileUpload object.
  """ 
  def __init__(self):
    self.file = StringIO()
    self.filename = '<dummy field storage>'
    self.headers = {}

class TestPlanningBox(ERP5TypeTestCase):
  """
    Test the API of PlanningBox. The user-visible aspect is 
    not tested here.
  """
  quiet = 1
  run_all_test = 1
 
  def getBusinessTemplateList(self):
    # Use the same framework as the functional testing for convenience.
    # This adds some specific portal types and skins.
     return ('erp5_ui_test',)

  def getTitle(self):
     return "PlanningBox"

  def afterSetUp(self):
     self.login()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def stepTic(self,**kw):
    self.tic()

  def stepCreateObjects(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    message = portal.foo_module.FooModule_createObjects()
    self.failUnless('Created Successfully' in message)

  def stepCreateObjectLines(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    portal = self.getPortal()
    message = portal.foo_module['0'].Foo_createObjects(num=1)
    self.failUnless('Created Successfully' in message)
    #portal.foo_module['0'].Foo_editObjects(num=3)

  def stepRenderStructure(self, sequence = None, sequence_list = None, **kw):
    portal = self.getPortal()
    context = portal.foo_module['0']
    planningbox = context.Foo_viewPlanningBox.planning_box
    request = get_request()
    request['here'] = context
    #planningboxline_list = planningbox.get_value('default', REQUEST = request)
    basic, planning = planningbox.widget.render_structure(field=planningbox, 
                                                          REQUEST=request, 
                                                          context=context)
    sequence.edit(planning_box = planningbox,
                    basic=basic,
                    planning=planning)

  def stepCheckPlanning(self, sequence = None, sequence_list = None, **kw):
    planning = sequence.get('planning')  
    self.assertEquals(len(planning.content), 1)
    bloc = planning.content[0]
    self.assertEquals(bloc.name , 'Group_1_Activity_1_Block_1')
    self.assertEquals(bloc.title , 'Title 0')
    for info in bloc.info.values():
      self.assertEquals(info.info,'Title 0')
      self.assertEquals(info.link , '/%s/foo_module/0/0' % self.getPortal().getId())
      
  def stepCheckBasic(self, sequence = None, sequence_list = None, **kw):
    basic = sequence.get('basic')
    self.assertEquals(len(basic.report_groups), 1)
    # Note that this test use the use_date_zoom enabled
    sec_axis_info = basic.getSecondaryAxisInfo()
    date = DateTime()
    today = DateTime('%s/%s/%s' % (date.year(),date.month(),date.day()))
    self.assertEquals(sec_axis_info['zoom_begin'], today)
    self.assertEquals(sec_axis_info['zoom_end'], today+1)
    self.assertEquals(sec_axis_info['bound_begin'], today)
    self.assertEquals(sec_axis_info['bound_start'], today)
    self.assertEquals(sec_axis_info['bound_end'], today+1)
    self.assertEquals(sec_axis_info['bound_stop'], today+1)
    self.assertEquals(sec_axis_info['zoom_start'], 0)
    self.assertEquals(sec_axis_info['zoom_level'], 1.0)
    self.assertEquals(sec_axis_info['bound_range'], 1.0)


    for tree_list, activity_list,stat in basic.report_groups:
      self.assertEquals(len(activity_list), 1)


  def test_01(self, quiet=quiet, run=run_all_test):
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
                       CreateObjects \
                       Tic \
                       CreateObjectLines \
                       Tic \
                       RenderStructure \
                       CheckPlanning \
                       CheckBasic \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPlanningBox))
    return suite


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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.Globals import get_request
from six.moves import cStringIO as StringIO
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

  def login(self, *args, **kw):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def stepCreateObjects(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    portal = self.getPortal()
    portal.ListBoxZuite_reset()
    message = portal.foo_module.FooModule_createObjects()
    self.assertIn('Created Successfully', message)

  def stepCreateObjectLines(self, sequence = None, sequence_list = None, **kw):
    # Make sure that the status is clean.
    portal = self.getPortal()
    message = portal.foo_module['0'].Foo_createObjects(num=1)
    self.assertIn('Created Successfully', message)
    portal.foo_module['0'].Foo_editObjectLineDates()

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
    self.assertEqual(planning.vertical_view, 0)
    self.assertEqual(len(planning.content), 1)
    bloc = planning.content[0]
    self.assertEqual(bloc.name , 'group_1_activity_1_block_1')
    self.assertEqual(bloc.title , 'Title 0')
    for info in bloc.info.values():
      self.assertEqual(info.info,'Title 0')
      self.assertEqual(info.link ,
                        '%s/foo_module/0/0' % self.getPortal().absolute_url())
    # Check Parent Activities
    parent = bloc.parent_activity
    for info in parent.info.values():
      self.assertEqual(info,'Title 0')
    self.assertEqual(parent.link ,
                      '/%s/foo_module/0/0' % self.getPortal().getId())
    # XXX This test for Quantity is not complete, It should be improved.
    self.assertEqual(parent.height , None)
    self.assertEqual(parent.title,'Title 0')

  def stepCheckBasic(self, sequence = None, sequence_list = None, **kw):
    basic = sequence.get('basic')
    self.assertEqual(len(basic.report_group_list), 1)
    lane_tree_list = basic.buildLaneTreeList()
    sec_axis_info = basic.getLaneAxisInfo(lane_tree_list)
    date = DateTime()
    today = DateTime('%s/%s/%s' % (date.year(),date.month(),date.day()))
    self.assertEqual(sec_axis_info['bound_start'], today)
    self.assertEqual(sec_axis_info['bound_stop'], today+1)

    for _, activity_list, _ in basic.report_group_list:
      self.assertEqual(len(activity_list), 1)


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

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPlanningBox))
  return suite


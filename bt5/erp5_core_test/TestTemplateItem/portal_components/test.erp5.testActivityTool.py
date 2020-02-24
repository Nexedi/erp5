##############################################################################
#
# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class Test(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "TestActivityTool"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    self.activity_tool = self.getPortalObject().portal_activities
    if not(hasattr(self.portal,'test_activity_tool_module')):
      self.portal.newContent(portal_type='Organisation Module',
                             id='test_activity_tool_module')
    self.test_activity_tool_module = getattr(self.getPortal(), 'test_activity_tool_module', None)
    if not(self.test_activity_tool_module.hasContent('untitled')):
      self.test_activity_tool_module.newContent(id='untitled')
    self.test_activity_tool_object = self.test_activity_tool_module._getOb('untitled')
    self.tic()

  def RestartAndDeleteActivity(self, activity):
    self.test_activity_tool_object._setTitle('title1')
    self.assertEquals('title1',self.test_activity_tool_object.getTitle())

    self.test_activity_tool_object.activate(activity=activity)._setTitle('title2')
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = self.activity_tool.getMessageTempObjectList()
    self.assertEquals(len(message_list),1)
    self.activity_tool.manageDelete([message_list[0].uid],activity)
    # Needed so that the message are removed from the queue
    self.commit()
    self.tic()
    self.assertEquals('title1',self.test_activity_tool_object.getTitle())
    message_list = self.activity_tool.getMessageTempObjectList()
    self.assertEquals(len(message_list),0)

    self.test_activity_tool_object.activate(activity=activity)._setTitle('title2')
    # Needed so that the message are commited into the queue
    self.commit()
    message_list = self.activity_tool.getMessageTempObjectList()
    self.assertEquals(len(message_list),1)
    self.activity_tool.manageRestart([message_list[0].uid],activity)
    self.commit()
    self.tic()
    self.assertEquals('title2',self.test_activity_tool_object.getTitle())
    message_list = self.activity_tool.getMessageTempObjectList()
    self.assertEquals(len(message_list),0)

  def test_manageDelete(self):
    self.RestartAndDeleteActivity('SQLQueue')
    self.RestartAndDeleteActivity('SQLDict')

##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

import os, sys
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
import time
import os
from Products.ERP5Type import product_path
from Products.CMFCore.utils import getToolByName

class TestBase(ERP5TypeTestCase):

  run_all_test = 1
  object_portal_type = "Organisation"

  def getTitle(self):
    return "Base"

  def getBusinessTemplateList(self):
    """
    """
    return ()

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('rc', '', ['Manager'], [])
    user = uf.getUserById('rc').__of__(uf)
    newSecurityManager(None, user)

  def enableLightInstall(self):
    """
    You can override this. 
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def afterSetUp(self, quiet=1, run=run_all_test):
    self.login()
    portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    portal_catalog = self.getCatalogTool()
    #portal_catalog.manage_catalogClear()
    self.createCategories()

  def createCategories(self):
    """ 
      Light install create only base categories, so we create 
      some categories for testing them
    """
    pass

  def stepTic(self,**kw):
    self.tic()

  def stepCreateObject(self, sequence=None, sequence_list=None, **kw):
    """
      Create a object which will be tested.
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.object_portal_type)
    object = module.newContent(portal_type=self.object_portal_type)
    sequence.edit(
        object=object,
        current_title=''
    )

  def stepCheckTitleValue(self, sequence=None, sequence_list=None, **kw):
    """
      Check if getTitle return a correect value
    """
    object = sequence.get('object')
    current_title = sequence.get('current_title')
    self.assertEquals(object.getTitle(), current_title)

  def stepSetDifferentTitleValue(self, sequence=None, sequence_list=None, 
                                 **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    current_title = sequence.get('current_title')
    new_title_value = '%s_a' % current_title
    ZopeTestCase._print('\nNew title value: %s\n' % new_title_value)
    object.edit(title=new_title_value)
    sequence.edit(
        current_title=new_title_value
    )

  def stepCheckIfActivitiesAreCreated(self, sequence=None, sequence_list=None,
                                      **kw):
    """
      Check if there is a activity in activity queue.
    """
    portal = self.getPortal()
    get_transaction().commit()
    message_list = portal.portal_activities.getMessageList()
    # XXX 2 messages are created.
    ZopeTestCase._print('\n%s\n' % str(message_list))
    ZopeTestCase._print('\n%s\n' % str([x.method_id for x in message_list]))
# XXX     ZopeTestCase._print('%s' % str([x.active_process for x in message_list]))
# XXX     ZopeTestCase._print('%s' % str([x.path for x in message_list]))
# XXX     self.assertEquals(len(message_list), 1)
    self.assertEquals(len(message_list), 2)


  def stepSetSameTitleValue(self, sequence=None, sequence_list=None, **kw):
    """
      Set a different title value
    """
    object = sequence.get('object')
    object.edit(title=object.getTitle())

  def stepCheckIfMessageQueueIsEmpty(self, sequence=None, 
                                     sequence_list=None, **kw):
    """
      Check if there is no activity in activity queue.
    """
    portal = self.getPortal()
    message_list = portal.portal_activities.getMessageList()
    self.assertEquals(len(message_list), 0)

  def test_01_titleSetter(self, quiet=0, run=run_all_test):
    """
      Test if setter is not called when we try to set the current value.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = \
             'CreateObject \
              CheckTitleValue \
              SetDifferentTitleValue \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              SetSameTitleValue \
              CheckIfMessageQueueIsEmpty \
              SetDifferentTitleValue \
              CheckIfActivitiesAreCreated \
              CheckTitleValue \
              Tic \
              CheckIfMessageQueueIsEmpty \
              '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestBase))
        return suite

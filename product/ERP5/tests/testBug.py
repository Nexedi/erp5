##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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


import os
from zLOG import LOG
from Testing import ZopeTestCase
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Utils import convertToUpperCase, DummyMailHost
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from AccessControl.SecurityManagement import newSecurityManager


if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'



class TestBug(ERP5TypeTestCase):
  """
    ERP5 unit tests for Bug module (part of erp5_forge business template).
  """

  # pseudo constants
  RUN_ALL_TEST = 1
  QUIET = 1


  ##################################
  ##  ZopeTestCase Skeleton
  ##################################

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "Bug"


  def getBusinessTemplateList(self):
    """
      Return the list of required business templates.
    """
    return ( 'erp5_base'
           , 'erp5_forge'
           )


  def afterSetUp(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.datetime      = DateTime()  # Save today at initialisation to "freeze" the time
    self.portal        = self.getPortal()
    self.workflow_tool = self.portal.portal_workflow
    # Use a dummy mailhost to not send mail notification to the guy how run unit test
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
      self.portal._setObject('MailHost', DummyMailHost('MailHost'))



  ##################################
  ##  Usefull methods
  ##################################

  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Create a new manager user and login.
    """
    user_name = 'kevin'
    user_folder = self.getPortal().acl_users
    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
    user = user_folder.getUserById(user_name).__of__(user_folder)
    newSecurityManager(None, user)



  ##################################
  ##  Basic steps
  ##################################

  def stepTic(self, **kw):
    """
      Flush activity queue.
    """
    self.tic()


  def stepCreateBug(self, sequence=None, sequence_list=None, **kw):
    """
      Create a dummy bug
    """
    portal_type = 'Bug'
    bug_module = self.portal.getDefaultModule(portal_type)
    bug = bug_module.newContent( portal_type       = portal_type
                               , immediate_reindex = 1
                               , title             = 'This is an important bug'
                               , description       = 'This %µ&~#^@! bug always happend on ERP5 start. The solution consist to kill the developper.'
                               , start_date        = self.datetime  # Today
                               , stop_date         = self.datetime  # Today
                               )
    sequence.edit(bug = bug)


  def stepOpenBug(self, sequence=None, sequence_list=None, **kw):
    """
      Open the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'open_action')
    self.assertEquals(bug.getValidationState(), 'open')


  def stepCloseBug(self, sequence=None, sequence_list=None, **kw):
    """
      Close the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'close_action')
    self.assertEquals(bug.getValidationState(), 'close')


  def stepCancelBug(self, sequence=None, sequence_list=None, **kw):
    """
      Cancel the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'cancel_action')
    self.assertEquals(bug.getValidationState(), 'cancel')


  def stepFollowBug(self, sequence=None, sequence_list=None, **kw):
    """
      The bug reporter don't know how to nicely report a bug. Tell him.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'follow_action', comment="Your Bug report is bad. You don't know how to report a bug. Please read http://www.chiark.greenend.org.uk/~sgtatham/bugs.html and resubmit your bug.")
    self.assertEquals(bug.getValidationState(), 'follow')


  def stepSetTestedBug(self, sequence=None, sequence_list=None, **kw):
    """
      Set the bug as unit tested.
    """
    bug = sequence.get('bug')
    bug.setTested(True)
    self.assertEquals(bug.getTested(), True)


  def stepSetOldClosedDate(self, sequence=None, sequence_list=None, **kw):
    """
      Change Closed Date to a funky old value.
    """
    bug = sequence.get('bug')
    bug.setStopDate(self.datetime - 10)
    self.assertEquals(bug.getStopDate(), self.datetime - 10) # Check that datetime is fixed


  def stepCheckClosedDate(self, sequence=None, sequence_list=None, **kw):
    """
      Check that the closed date is set as today.
    """
    bug = sequence.get('bug')
    self.assertEquals(bug.getStopDate(), self.datetime)



  ##################################
  ##  Tests
  ##################################

  def test_01_StopDateUpdatedOnClose(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test that a closed bug has its stop date property updated.
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreateBug'
                , 'stepOpenBug'
                , 'stepTic'
                , 'stepSetOldClosedDate'
                , 'stepCloseBug'
                , 'stepTic'
                , 'stepCheckClosedDate'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  def test_02_StopDateUpdatedOnCancel(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Same test as above but on cancel action (test bug #600).
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreateBug'
                , 'stepOpenBug'
                , 'stepTic'
                , 'stepSetOldClosedDate'
                , 'stepCancelBug'
                , 'stepTic'
                , 'stepCheckClosedDate'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)



if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBug))
    return suite

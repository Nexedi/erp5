# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
#                       Kevin Deldycke <kevin_AT_nexedi_DOT_com>
#                       Rafael Monnerat <rafael@nexedi.com>
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
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import DummyMailHost
from email import message_from_string
from email.header import decode_header


class TestBug(ERP5TypeTestCase):
  """
    ERP5 unit tests for Bug module (part of erp5_forge business template).
  """
  # pseudo constants
  RUN_ALL_TEST = 1
  QUIET = 1
  person_portal_type = "Person"
  assignment_portal_type = "Assignment"
  project_portal_type = "Project"
  bug_portal_type = "Bug"
  organisation_portal_type  = "Organisation"

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
           , 'erp5_crm'
           , 'erp5_forge'
           , 'erp5_pdm'
           , 'erp5_simulation'
           , 'erp5_trade'
           , 'erp5_project'
           )

  def afterSetUp(self):
    """
      Initialize the ERP5 site.
    """
    self.login()
    self.setDefaultSitePreference()
    self.datetime = DateTime()
    self.workflow_tool = self.portal.portal_workflow
    # Use a dummy mailhost to not send mail notification to the guy how run unit test
    if 'MailHost' in self.portal.objectIds():
      self.portal.manage_delObjects(['MailHost'])
      self.portal._setObject('MailHost', DummyMailHost('MailHost'))

  def setDefaultSitePreference(self):
    default_preference = self.portal.portal_preferences.default_site_preference
    default_preference.setPreferredTextFormat('text/plain')
    default_preference.getPreferredTextEditor('text_area')
    if self.portal.portal_workflow.isTransitionPossible(default_preference,
                                                                     'enable'):
      default_preference.enable()
    return default_preference

  ##################################
  ##  Usefull methods
  ##################################
#  def login(self, quiet=QUIET, run=RUN_ALL_TEST):
#    """
#      Create a new manager user and login.
#    """
#    user_name = 'kevin'
#    user_folder = self.getPortal().acl_users
#    user_folder._doAddUser(user_name, '', ['Manager', 'Owner', 'Assignor'], [])
#    user = user_folder.getUserById(user_name).__of__(user_folder)
#    newSecurityManager(None, user)
#
  ##################################
  ##  Basic steps
  ##################################
  def stepLoginUsualUser(self, **kw):
    portal = self.getPortal()
    uf = portal.acl_users
    uf._doAddUser('mame', '', ['Assignor','Assignee'], [])
    if not uf.getUser('dummy'):
      uf._doAddUser('manager', '', ['Manager'], [])
      self.loginByUserName('manager')
      person_module = portal.getDefaultModule(self.person_portal_type)
      person = person_module.newContent(id='dummy', title='dummy',
                                        reference='dummy')
      portal.portal_categories.group.newContent(id='dummy',
                                                codification='DUMMY')

      person.setEmailText('loggedperson@localhost')
      assignment = person.newContent(title='dummy', group='dummy',
                                     portal_type='Assignment',
                                     start_date='1980-01-01',
                                     stop_date='2099-12-31')
      assignment.open()
      person.newContent(portal_type='ERP5 Login', reference='dummy').validate()
      self.tic()
      portal_type_list = []
      for portal_type in (self.project_portal_type,
                          self.bug_portal_type,
                          self.person_portal_type,
                          self.assignment_portal_type,
                          self.organisation_portal_type,):
        portal_type_list.append(portal_type)
        module = portal.getDefaultModule(portal_type, None)
        if module is not None:
          portal_type_list.append(module.getPortalType())

      for portal_type in portal_type_list:
        ti = portal.portal_types[portal_type]
        ti.newContent(portal_type='Role Information',
          role_name_list=('Auditor','Author','Assignee','Assignor'),
          title='Dummy',
          role_base_category_script_id=
            'ERP5Type_getSecurityCategoryFromAssignment',
          role_category='group/dummy')
        ti.updateRoleMapping()

      self.tic()
      portal.portal_caches.clearAllCache()

    self.loginByUserName('dummy')


  def stepCreateProject(self,sequence=None, sequence_list=None, \
                        **kw):
    """
    Create a project
    """
    project_portal_type = "Project"
    portal = self.getPortal()
    module = portal.getDefaultModule(project_portal_type)
    project = module.newContent(
        portal_type=project_portal_type,
        title = 'Project')
    sequence.edit(project=project)

  def createPerson(self):
    """
      Create a person.
    """
    portal_type = 'Person'
    person_module = self.portal.getDefaultModule(portal_type)
    person = person_module.newContent(portal_type = portal_type )
    return person

  def stepCreatePerson1(self, sequence=None, sequence_list=None, **kw):
    """
      Create one Person
    """
    person = self.createPerson()
    project = sequence.get("project")
    self.createPersonAssignment(person=person, project=project)
    person.setDefaultEmailText("person1@localhost")
    sequence.edit(person1 = person)

  def stepCreatePerson2(self, sequence=None, sequence_list=None, **kw):
    """
      Create Person 2
    """
    person = self.createPerson()
    person.setDefaultEmailText("person2@localhost")
    sequence.edit(person2 = person)

  def createPersonAssignment(self,person=None,project=None ):
    """
      Create a person Assigment and Assign to a Project.
    """
    # Create Assignment
    assignment = person.newContent(portal_type='Assignment')
    assignment.setDestinationProjectValue(project)
    assignment.setStartDate(DateTime()-365)
    assignment.setStopDate(DateTime()+365)
    self.portal.portal_workflow.doActionFor(assignment, 'open_action')

  def stepCheckBugNotification(self, sequence=None,
                                         sequence_list=None, **kw):
    """
    Check that notification works
    """
    bug = sequence.get('bug')
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEqual('dummy <loggedperson@localhost>', mfrom)
    self.assertEqual(['person1@localhost'], mto)
    message = message_from_string(messageText.decode())
    self.assertTrue(decode_header(message['Subject'])[0][0].endswith(bug.getTitle()))

  def stepCheckBugMessageNotification(self, sequence=None,
                                         sequence_list=None, **kw):
    """
    Check that notification works
    """
    bug = sequence.get('bug')
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual((), last_message)
    mfrom, mto, messageText = last_message
    self.assertEqual('person2@localhost', mfrom)
    self.assertEqual(['person1@localhost'], mto)
    message = message_from_string(messageText.decode())
    self.assertTrue(decode_header(message['Subject'])[0][0].endswith(bug.getTitle()))

  def stepSetSourceProject(self, sequence=None, sequence_list=None, **kw):
    """
      Set Source Project to a Bug
    """
    bug = sequence.get('bug')
    project = sequence.get('project')
    bug.setSourceProjectValue(project)

  def stepSetRequester(self, sequence=None, sequence_list=None, **kw):
    """
      Set Source Project to a Bug
    """
    bug = sequence.get('bug')
    person2 = sequence.get('person2')
    bug.setDestinationValue(person2)

  def stepCreateBug(self, sequence=None, sequence_list=None, **kw):
    """
      Create a dummy bug
    """
    portal_type = 'Bug'
    bug_module = self.portal.getDefaultModule(portal_type)
    bug = bug_module.newContent( portal_type = portal_type
                               , title  = 'Bug Title'
                               , description = 'Bug Description'
                               , start_date = self.datetime
                               , stop_date = self.datetime
                               )
    sequence.edit(bug = bug)

  def stepCreateBugMessage(self, sequence=None, sequence_list=None, **kw):
    """
      Create a dummy Bug Message
    """
    portal_type = 'Bug Line'
    bug = sequence.get('bug')
    person2 = sequence.get('person2')
    bug_message = bug.newContent( portal_type = portal_type
                                  , title  = 'Bug Message'
                                  , text_content = 'Bug Description'
                                )
    # usually the person who is creates the message is setted as source
    # by BugLine_init
    bug_message.setSourceValue(person2)
    sequence.edit(bug_message = bug_message)

  def stepPostBugMessage(self, sequence=None, sequence_list=None, **kw):
    """
      Post the bug message.
    """
    bug_message = sequence.get('bug_message')
    self.workflow_tool.doActionFor(bug_message, 'start_action')

  def stepCheckBugMessageIsDelivered(self, sequence=None, \
                                                     sequence_list=None, **kw):
    """
      check if the message is delivered the bug.
    """
    bug_message = sequence.get('bug_message')
    self.assertEqual(bug_message.getSimulationState(), 'delivered')

  def stepCheckBugMessage(self, sequence=None, sequence_list=None, **kw):
    """
      Check a dummy bug message
    """
    bug_message = sequence.get('bug_message')
    person = sequence.get('person1')
    self.assertEqual( [ person ] , bug_message.getDestinationValueList())
    self.assertTrue( bug_message.getStartDate() is not None)
    #self.assertEqual(bug_message.getSourceValue().getTitle(), 'dummy')

  def stepCheckBugMessageNotificationReAssign(self, sequence=None, sequence_list=None, **kw):
    """
      Check the bug message when re-assign
    """
    last_message = self.portal.MailHost._last_message
    self.assertNotEqual((), last_message)
    _, _, messageText = last_message
    from email.parser import Parser
    p = Parser()
    m = p.parsestr(messageText.decode())
    self.assertIn(b'Re-assign!', m.get_payload()[0].get_payload(decode=True))


  def stepCheckBugInit(self, sequence=None, sequence_list=None, **kw):
    """
      Create a dummy bug
    """
    bug = sequence.get('bug')
    self.assertEqual("#%s" % bug.getId(), bug.getReference())
    #self.assertEqual(bug_message.getSourceTradeValue().getTitle(), 'dummy')

  def stepCloneAndCheckBug(self, sequence=None, sequence_list=None, **kw):
    """
      Create a dummy bug
    """
    bug_to_clone = sequence.get('bug')
    self.assertNotEqual(len(bug_to_clone.contentValues()), 0)
    bug = bug_to_clone.Base_createCloneDocument(batch_mode=1)
    self.assertEqual("#%s" % bug.getId(), bug.getReference())
    self.assertEqual(len(bug.contentValues()), 0)

  def stepOpenBug(self, sequence=None, sequence_list=None, **kw):
    """
      Open the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'confirm_action', send_event=1)
    self.assertEqual(bug.getSimulationState(), 'confirmed')

  def stepAssignBug(self, sequence=None, sequence_list=None, **kw):
    """
      Close the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'set_ready_action', send_event=1)
    self.assertEqual(bug.getSimulationState(), 'ready')

  def stepResolveBug(self, sequence=None, sequence_list=None, **kw):
    """
      Close the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'stop_action', send_event=1)
    self.assertEqual(bug.getSimulationState(), 'stopped')

  def stepReAssignBug(self, sequence=None, sequence_list=None, **kw):
    """
      Re Assign the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 're_assign_action', send_event=1, comment='Re-assign!')
    self.assertEqual(bug.getSimulationState(), 'ready')

  def stepCloseBug(self, sequence=None, sequence_list=None, **kw):
    """
      Close the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'deliver_action', send_event=1)
    self.assertEqual(bug.getSimulationState(), 'delivered')

  def stepCancelBug(self, sequence=None, sequence_list=None, **kw):
    """
      Cancel the bug.
    """
    bug = sequence.get('bug')
    self.workflow_tool.doActionFor(bug, 'cancel_action', send_event=1)
    self.assertEqual(bug.getSimulationState(), 'cancelled')

  def stepSetTestedBug(self, sequence=None, sequence_list=None, **kw):
    """
      Set the bug as unit tested.
    """
    bug = sequence.get('bug')
    bug.setTested(True)
    self.assertEqual(bug.getTested(), True)

  def stepSetOldClosedDate(self, sequence=None, sequence_list=None, **kw):
    """
      Change Closed Date to a funky old value.
    """
    bug = sequence.get('bug')
    bug.setStopDate(self.datetime - 10)
    self.assertEqual(bug.getStopDate().Date(), (self.datetime - 10).Date()) # Check that datetime is fixed

  def stepCheckClosedDate(self, sequence=None, sequence_list=None, **kw):
    """
      Check that the closed date is set as today.
    """
    bug = sequence.get('bug')
    self.assertEqual(bug.getStopDate().Date(), self.datetime.Date())

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
                , 'stepCheckBugInit'
                , 'stepOpenBug'
                , 'stepTic'
                , 'stepSetOldClosedDate'
                , 'stepAssignBug'
                , 'stepTic'
                , 'stepResolveBug'
                , 'stepTic'
                , 'stepReAssignBug'
                , 'stepTic'
                , 'stepResolveBug'
                , 'stepTic'
                , 'stepCloseBug'
                , 'stepTic'
                , 'stepCheckClosedDate'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_02_setCheckBugNotification(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test that a closed bug has its stop date property updated.
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepLoginUsualUser'
                , 'stepCreateBug'
                , 'stepCreateProject'
                , 'stepCreatePerson1'
                , 'stepCreatePerson2'
                , 'stepSetSourceProject'
                , 'stepSetRequester'
                , 'stepTic'
                , 'stepOpenBug'
                , 'stepTic'
                , 'stepCheckBugNotification'
                , 'stepAssignBug'
                , 'stepTic'
                , 'stepCheckBugNotification'
                , 'stepResolveBug'
                , 'stepTic'
                , 'stepCheckBugNotification'
                , 'stepReAssignBug'
                , 'stepTic'
                , 'stepCheckBugNotification'
                , 'stepCheckBugMessageNotificationReAssign'
                , 'stepResolveBug'
                , 'stepTic'
                , 'stepCheckBugNotification'
                , 'stepCloseBug'
                , 'stepTic'
                , 'stepCheckBugNotification'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_03_setCheckBugNotification(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test that a closed bug has its stop date property updated.
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepLoginUsualUser'
                , 'stepCreateBug'
                , 'stepCreateProject'
                , 'stepCreatePerson1'
                , 'stepCreatePerson2'
                , 'stepSetSourceProject'
                , 'stepSetRequester'
                , 'stepTic'
                , 'stepOpenBug'
                , 'stepTic'
                , 'stepCheckBugNotification'
                , 'stepCreateBugMessage'
                , 'stepCheckBugMessage'
                , 'stepTic'
                , 'stepPostBugMessage'
                , 'stepTic'
                , 'stepCheckBugMessageIsDelivered'
                , 'stepCheckBugMessageNotification'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_04_StopDateUpdatedOnCancelWithUsualUser(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test that cancelBug with usual user.
    """
    if  not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepLoginUsualUser'
                , 'stepCreateBug'
                , 'stepOpenBug'
                , 'stepTic'
                , 'stepSetOldClosedDate'
                , 'stepCancelBug'
                , 'stepTic'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_05_setCheckBugClone(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test that a closed bug has its stop date property updated.
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreateBug',
                  'stepCheckBugInit',
                  'stepOpenBug',
                  'stepCloneAndCheckBug'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_06_BugLineClone(self):
    bug_portal_type = 'Bug'
    module = self.portal.getDefaultModule(portal_type=bug_portal_type)
    bug = module.newContent(portal_type=bug_portal_type)
    bug_line = bug.newContent(portal_type='Bug Line')
    cloned_bug_line = bug_line.Base_createCloneDocument(batch_mode=1)
    self.assertTrue(cloned_bug_line.getStartDate() > bug_line.getStartDate())

  def test_07_Bug_BugLineSendFastInput(self):
    bug_portal_type = 'Bug'
    module = self.portal.getDefaultModule(portal_type=bug_portal_type)
    bug = module.newContent(portal_type=bug_portal_type)

    text_content = 'text content'
    title = 'title'

    bug_line = bug.Bug_doBugLineSendFastInputAction(batch_mode=1, title=title,
        text_content=text_content)

    self.assertEqual(text_content, bug_line.getTextContent())
    self.assertEqual(title, bug_line.getTitle())
    self.assertEqual('delivered', bug_line.getSimulationState())

  def test_08_openResolvedBug(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
     Test that a bug is resolved, we can still reopen it
    """
    if not run: return
    sequence_list = SequenceList()
    step_list = [ 'stepCreateBug'
                , 'stepCheckBugInit'
                , 'stepOpenBug'
                , 'stepTic'
                , 'stepAssignBug'
                , 'stepTic'
                , 'stepResolveBug'
                , 'stepTic'
                , 'stepOpenBug'
                , 'stepTic'
                ]
    sequence_string = ' '.join(step_list)
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_09_ResolveBugWithDeletedBugLine(self):
    """
    verify that we can still resolve a bug with a
    deleted bug line
    """
    self.loginByUserName('mame')
    bug_portal_type = 'Bug'
    module = self.portal.getDefaultModule(portal_type=bug_portal_type)
    bug = module.newContent(portal_type=bug_portal_type)
    bug_line = bug.newContent(portal_type='Bug Line')
    bug_line.Base_createCloneDocument(batch_mode=1)
    self.workflow_tool.doActionFor(bug, 'confirm_action', send_event=1)
    self.assertEqual(bug.getSimulationState(), 'confirmed')
    self.tic()
    bug.deleteContent(id='2')
    self.tic()
    self.workflow_tool.doActionFor(bug, 'stop_action', send_event=1)
    self.assertEqual(bug.getSimulationState(), 'stopped')

  def test_posting_bug_line_updates_bug_modification_date(self):
    bug = self.portal.bug_module.newContent(portal_type='Bug')
    bug_modification_date = bug.getModificationDate()

    bug_line = bug.newContent(portal_type='Bug Line')
    self.assertEqual(bug.getModificationDate(), bug_modification_date)
    bug_line.start()
    self.commit()
    self.assertGreater(bug.getModificationDate(), bug_modification_date)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBug))
  return suite

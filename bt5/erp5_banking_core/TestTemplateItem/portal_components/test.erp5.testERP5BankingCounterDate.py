
##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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


# import requested python module
import os
from zLOG import LOG
from DateTime import DateTime
from Testing import ZopeTestCase
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from erp5.component.module.TestERP5BankingMixin import TestERP5BankingMixin

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

class TestERP5BankingCounterDate(TestERP5BankingMixin):
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet

  def getTitle(self):
    return "ERP5BankingCounterDate"

  def afterSetUp(self):
    # Initialise only once
    portal = self.getPortal()
    if getattr(portal.organisation_module, 'baobab_org', None) is None:
      self.initDefaultVariable()
      self.createManagerAndLogin()
      # now we need to create a user as Manager to do the test
      # in order to have an assigment defined which is used to do transition
      # Create an Organisation that will be used for users assignment
      self.checkUserFolderType()
      self.organisation = self.organisation_module.newContent(id='baobab_org', portal_type='Organisation',
                            function='banking', group='baobab',  site='testsite/paris')
      # define the user
      user_dict = {
          'super_user' : [['Manager'], self.organisation, 'banking/comptable', 'baobab', 'testsite/paris/surface/banque_interne/guichet_1']
        }
      # call method to create this user
      self.createERP5Users(user_dict)
      self.createFunctionGroupSiteCategory()
    else:
      # Set again some properties since they vanish between tests
      site = portal.portal_categories.site.testsite
      self.paris = site.paris
      self.madrid = site.madrid
      self.workflow_tool = portal.portal_workflow
    self.logout()
    self.loginByUserName('super_user')
    counter_date_module = self.getPortal().counter_date_module
    counter_date_module.manage_delObjects(ids=[x for x in counter_date_module.objectIds()])
    self.tic()

  def openCounterDate(self, date=None, site=None, id='counter_date_1', open=True, force_check=0):
    """
      Redefine openCounterDate here, taking code from TestERP5Banking.
      This is because "force_check", when false, skips entierly workflow
      scripts. As a workflow is responsible for setting the reference, it
      would make this test unable to open counter dates on a day other than
      current one.
    """
    if date is None:
      date = DateTime().Date()
    if not isinstance(date, str):
      date = date.Date()
    if site is None:
      site = self.testsite
    date_object = self.getCounterDateModule().newContent(id=id,
      portal_type='Counter Date', site_value=site, start_date=date)
    if open:
      self.workflow_tool.doActionFor(date_object, 'open_action',
        wf_id='counter_date_workflow', check_date_is_today=force_check)
    setattr(self, id, date_object)
    date_object.assignRoleToSecurityGroup()

  def test_01_CheckOpenCounterDateTwiceFail(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test that opening a counter date when there is a counter date opened fails.
    """
    if not run:
      return
    if not quiet:
      message = 'Check open CounterDate twice fails'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    self.openCounterDate(site=self.paris, id='counter_date_1')
    self.tic()
    self.openCounterDate(site=self.paris, id='counter_date_2', open=0)
    # open counter date and counter
    self.assertRaises(ValidationFailed,
                     self.workflow_tool.doActionFor,
                     self.counter_date_2, 'open_action',
                     wf_id='counter_date_workflow')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(
           ob=self.counter_date_2, name='history', wf_id='counter_date_workflow')
    # check its len is 2
    msg = workflow_history[-1]['error_message']
    self.assertTrue('there is already a counter date opened' in "%s" %(msg, ))

  def test_02_CheckOpenCounterDateWithOtherDateFail(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
      Test that opening a counter date on a non-current date fails.
    """
    if not run:
      return
    if not quiet:
      message = 'Check open CounterDate on non-current date fails'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    def openAndTest(id, date):
      self.openCounterDate(site=self.paris, id=id, date=date, open=0)
      # open counter date and counter
      counter_date = getattr(self, id)
      self.assertRaises(ValidationFailed,
                       self.workflow_tool.doActionFor,
                       counter_date, 'open_action',
                       wf_id='counter_date_workflow')
      # get workflow history
      workflow_history = self.workflow_tool.getInfoFor(
             ob=counter_date, name='history', wf_id='counter_date_workflow')
      # check its len is 2
      msg = workflow_history[-1]['error_message']
      self.assertTrue('the date is not today' in "%s" %(msg, ))
    now = DateTime()
    # Future
    openAndTest('1', now + 2) # Just in case midnight passes between "now" calculation and validation, add 2 instead of 1
    # Past
    openAndTest('2', now - 1)

  def test_03_CheckReferenceIsIncreasedEveryDay(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
     Test counter date reference generation.
     Rules:
     - starts at one
     - increasing by one
     - monotonous
     - year-scoped
     - site-scoped
    """
    if not run:
      return
    if not quiet:
      message = 'Check CounterDate reference generator behaviour'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    counter_date_module = self.getPortal().counter_date_module
    def openAndTest(site, date, reference):
      id = 'counter_date_%s_%s' % (date.strftime('%Y%m%d'), site.getId())
      self.openCounterDate(site=site, date=date, id=id)
      counter_date = getattr(self, id)
      self.assertEqual(counter_date.getReference(), reference)
      counter_date.close()
      self.tic()

    # Starts at one
    openAndTest(self.paris, DateTime('2008/01/01'), '1')
    # Increasing by one
    openAndTest(self.paris, DateTime('2008/01/02'), '2')
    # Monotonous: create one but leave it in draft, check same day
    self.openCounterDate(site=self.paris, id='counter_date_2008_01_03_paris_draft', date=DateTime('2008/01/03'), open=0)
    self.tic()
    openAndTest(self.paris, DateTime('2008/01/03'), '3')
    # Monotonous: create one but leave it in draft, check next day
    self.openCounterDate(site=self.paris, id='counter_date_2008_01_04_paris_draft', date=DateTime('2008/01/04'), open=0)
    self.tic()
    openAndTest(self.paris, DateTime('2008/01/05'), '4')
    # Site-scoped
    openAndTest(self.madrid, DateTime('2008/01/01'), '1')
    # Year-scoped
    openAndTest(self.paris, DateTime('2008/12/31'), '5')
    openAndTest(self.paris, DateTime('2009/01/01'), '1')

  def test_04_CheckOpenCounterDateTwiceWithoutActivitiesFail(self, quiet=QUIET,
    run=RUN_ALL_TEST):
    """
      Test that opening a counter date when there is a counter date opened
      fails, even when activites are not executed.
    """
    if not run:
      return
    if not quiet:
      message = 'Check open CounterDate twice without activities fails'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    self.openCounterDate(site=self.paris, id='counter_date_1')
    self.commit()
    self.openCounterDate(site=self.paris, id='counter_date_2', open=0)
    # open counter date and counter
    self.assertRaises(ValidationFailed,
                     self.workflow_tool.doActionFor,
                     self.counter_date_2, 'open_action',
                     wf_id='counter_date_workflow')


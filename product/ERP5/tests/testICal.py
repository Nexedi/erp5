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


from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Form.Form import ERP5Form


class TestICal(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "ICal Test"

  def getBusinessTemplateList(self):
    """  """
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade', 'erp5_project', 'erp5_crm',
            'erp5_ical_style')

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.request=self.app.REQUEST
    self.validateRules()
    self.makeDataObjects()

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def makeDataObjects(self, quiet=0, run=run_all_test):
    """
      Create some Pesons so that we have something to feed.
    """
    if hasattr(self.portal.person_module, 'one'):
      self.portal.person_module.manage_delObjects(['one'])
    one = self.portal.person_module.newContent(id="one", title="One", description="Person One")
    self.tic()

  def parseICalFeed(self,  feed_string):
    """
      Parse the feed.
      We always have one object in feed (in this test), so we can
      safely use dict to check what is inside.
    """
    feed = feed_string.split('\n')
    # split once, because link like 'URL:http://myhost...' can exist in feed_string
    feed = [s.split(':',  1) for s in feed if s]
    feed_dict = {}
    for line in feed:
      if line[0] == 'BEGIN' or line[0] == 'END':
        feed_dict[':'.join(line)] = line[1]
      else:
        feed_dict[line[0]] = line[1]
    return feed_dict

  def getICalFeed(self, module):
    """
      Get the feed using form rendered by ical_view pt
    """
    self.request.set('portal_skin', 'iCal');
    self.portal.portal_skins.changeSkin('iCal');

    feed_string = module.Folder_viewContentListAsICal()
    return self.parseICalFeed(feed_string)

  def test_01_renderEvent(self, quiet=0, run=run_all_test):
    """
      Events (like phone call) are rendered as events (not surprisingly).
      Here we check if the dates, categories and other properties are rendered correctly.
    """
    if not run: return
    module = self.portal.event_module
    event = module.newContent(id='one', title='Event One', portal_type='Phone Call')
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertTrue('BEGIN:VCALENDAR' in feed_dict)
    self.assertTrue('END:VCALENDAR' in feed_dict)
    self.assertTrue('BEGIN:VEVENT' in feed_dict)
    self.assertTrue('END:VEVENT' in feed_dict)
    self.assertEqual(feed_dict['SUMMARY'], 'Event One')
    # if not set start date, it must be same as creation date
    # if not set end date, it must be same as start date
    self.assertEqual(feed_dict['DTSTART'], event.getCreationDate().HTML4().replace('-','').replace(':',''))
    self.assertEqual(feed_dict['DTEND'], event.getCreationDate().HTML4().replace('-','').replace(':',''))
    self.assertEqual(feed_dict['CREATED'], event.getCreationDate().HTML4().replace('-','').replace(':',''))
    self.assertEqual(feed_dict['LAST-MODIFIED'], event.getModificationDate().HTML4().replace('-','').replace(':',''))
    self.assertEqual(feed_dict['URL'],  event.absolute_url())
    self.assertEqual(feed_dict['UID'], 'uuid%s' % event.getUid())
    # there is no description
    self.assertFalse('DESCRIPTION' in feed_dict)
    # current workflow state - draft
    self.assertEqual(feed_dict['STATUS'], 'TENTATIVE')

    # set start date, description and change workflow state - new
    event.plan()
    event.setStartDate('2007/08/15 08:30 UTC')
    event.setDescription('Event One description')
    self.tic()

    feed_dict = self.getICalFeed(module)
    # DSTART and DTEND are the date in UTC
    self.assertEqual(feed_dict['DTSTART'], '20070815T083000Z')
    # if not set end date, it must be same as start date
    self.assertEqual(feed_dict['DTEND'], '20070815T083000Z')
    self.assertEqual(feed_dict['STATUS'], 'TENTATIVE')
    self.assertEqual(feed_dict['DESCRIPTION'],  'Event One description')

    # check categorization
    sale_op = self.portal.sale_opportunity_module.newContent(portal_type='Sale Opportunity', title='New Opportunity', reference='NEWSALEOP')
    event.setFollowUp(sale_op.getRelativeUrl())
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertTrue(feed_dict['CATEGORIES'] in ('NEWSALEOP', 'New Opportunity')) # forward compatibility

    # set stop date and change workflow state - assigned
    event.confirm()
    event.start()
    event.setStopDate('2007/08/15 13:30 UTC')
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertEqual(feed_dict['DTEND'], '20070815T133000Z')
    self.assertEqual(feed_dict['STATUS'], 'CONFIRMED')

    # cancel event but first remove previously created
    module.manage_delObjects([event.getId()])
    event2 = module.newContent(title='Event Two', portal_type='Phone Call')
    event2.cancel()
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertEqual(feed_dict['STATUS'], 'CANCELLED')

  def test_02_renderTask(self, quiet=0, run=run_all_test):
    """
      Task - is rendered as "todo".
      Additionally, it has "status" and "percent-complete" fields which change
      when the task moves along task_workflow.
      Dates work the same way, so we don't have to repeat it
    """
    if not run: return
    module = self.portal.task_module
    task = module.newContent(id='one', title='Task One', start_date='2007/08/15')
    self.tic()

   # current workflow state - draft
    feed_dict = self.getICalFeed(module)
    self.assertTrue('BEGIN:VCALENDAR' in feed_dict)
    self.assertTrue('END:VCALENDAR' in feed_dict)
    self.assertTrue('BEGIN:VTODO' in feed_dict)
    self.assertTrue('END:VTODO' in feed_dict)
    self.assertEqual(feed_dict['SUMMARY'], 'Task One')
    self.assertEqual(feed_dict['STATUS'], 'NEEDS-ACTION')
    self.assertEqual(feed_dict.get('PERCENT-COMPLETE', '0'), '0') # when it is zero it doesn't have to be there
    # now we check categorization (while we can edit the object)
    project = self.portal.project_module.newContent(portal_type='Project',
                                                                          title='New Project',
                                                                          reference='NEWPROJ')
    task.setSourceProjectValue(project)
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertEqual(feed_dict['CATEGORIES'], 'NEWPROJ')

    # change workflow state - planned
    task.plan()
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertEqual(feed_dict['STATUS'], 'NEEDS-ACTION')
    self.assertEqual(feed_dict['PERCENT-COMPLETE'], '33')

    # change workflow state - ordered
    task.order()
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertEqual(feed_dict['STATUS'], 'IN-PROCESS')
    self.assertEqual(feed_dict['PERCENT-COMPLETE'], '66')

    # change workflow state - confirmed
    task.confirm()
    self.tic()

    feed_dict = self.getICalFeed(module)
    self.assertEqual(feed_dict['STATUS'], 'COMPLETED')
    self.assertEqual(feed_dict['PERCENT-COMPLETE'], '100')

  def test_03_renderJournal(self, quiet=0, run=run_all_test):
    """
    Everyting which is not event and task is rendered as journal.
    Here we render person module as iCal.
    In this case pt for render current form('Test_view') is default page template(form_view)
    """
    if not run: return
    self.request.set('portal_skin', 'iCal');
    self.portal.portal_skins.changeSkin('iCal');

    self.portal._setObject('Test_view',
                        ERP5Form('Test_view', 'View'))
    self.portal.Test_view.manage_addField('listbox', 'listbox', 'ListBox')

    listbox=self.portal.Test_view.listbox
    self.assertNotEquals(listbox, None)

    listbox.manage_edit_xmlrpc(
          dict(columns=[('title', 'Title'),
                        ('creation_date', 'Creation date'),
                        ('description','Description'),
                        ('Base_getICalComponent',  'Component')],
               sort=[('creation_date', 'descending')],
               list_action='list',
               list_method='searchFolder',
               count_method='countFolder',
               selection_name='ical_folder_selection'))

    module = self.portal.person_module
    one = self.portal.person_module.one
    feed_string = self.portal.person_module.Test_view()
    feed_dict = self.parseICalFeed(feed_string)

    self.assertTrue('BEGIN:VCALENDAR' in feed_dict)
    self.assertTrue('END:VCALENDAR' in feed_dict)
    self.assertTrue('BEGIN:VJOURNAL' in feed_dict)
    self.assertTrue('END:VJOURNAL' in feed_dict)
    self.assertEqual(feed_dict['SUMMARY'], 'One')
    self.assertEqual(feed_dict['DESCRIPTION'], 'Person One')
    self.assertEqual(feed_dict['CREATED'], one.getCreationDate().HTML4().replace('-','').replace(':',''))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestICal))
  return suite

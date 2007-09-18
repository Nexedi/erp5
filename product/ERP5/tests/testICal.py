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

"""
  TIMEZONE WARNING
  The ICal renderer does not take into account time zones, because clients can take care about it
  for themselves, so we use GMT time.
  This test assumes the person running the test is in the same time zone as me, which is usually true.
  It will be fixed some day.
  
  I have been investigating this a little, DateTime module caches the timezone
  very early in the initialisation process, so changing os.environ['TZ'] has
  no effect. For now, the easiest is to set TZ environ variable to something
  like 'Europe/France'

"""

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager

try:
  from transaction import get as get_transaction
except ImportError:
  pass


class TestICal(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "ICal Test"

  def getBusinessTemplateList(self):
    """  """
    return ('erp5_base', 'erp5_trade', 'erp5_project', 'erp5_crm',
            'erp5_ical_style')

  def afterSetUp(self):
    self.portal = self.getPortal()

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    uf._doAddUser('ERP5TypeTestCase', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def makeDataObjects(self, quiet=0, run=run_all_test):
    """
      Create some Pesons so that we have something to feed.
      (we create only one because we'd have sorting problems)
    """
    if hasattr(self.portal.person_module, 'one'):
      self.portal.person_module.manage_delObjects(['one'])
    one = self.portal.person_module.newContent(id="one", title="One", description="Person One")
    get_transaction().commit()
    one.reindexObject()
    self.tic()

  def getICalFeed(self, module):
    """
      Get and parse the feed.
      We always have one object in feed (in this test), so we can
      safely use dict to check what is inside.
    """
    feed_string = module.Folder_viewContentListAsICal()
    feed = feed_string.split('\n')
    feed = [s.split(':') for s in feed if s] 
    feed_dict = {}
    for line in feed:
      if line[0] == 'BEGIN' or line[0] == 'END':
        feed_dict[':'.join(line)] = line[1]
      else:
        feed_dict[line[0]] = line[1]
    return feed_dict

  def test_01_renderEvent(self, quiet=0, run=run_all_test):
    """
      Events (like phone call) are rendered as events (not surprisingly).
      Here we check if the dates are rendered correctly.
    """
    module = self.portal.event_module
    event = module.newContent(id='one', title='Event One', portal_type='Phone Call')
    get_transaction().commit()
    event.reindexObject()
    self.tic()
    feed_dict = self.getICalFeed(module)
    self.assertTrue('BEGIN:VCALENDAR' in feed_dict.keys())
    self.assertTrue('END:VCALENDAR' in feed_dict.keys())
    # it has no start_date so it shouldn't show up at all
    self.assertFalse('BEGIN:VEVENT' in feed_dict.keys())
    # set start date - should be present with end date calculated
    event.setStartDate('2007/08/15 10:30')
    event.reindexObject()
    self.tic()
    feed_dict = self.getICalFeed(module)
    self.assertTrue('BEGIN:VEVENT' in feed_dict.keys())
    self.assertEquals(feed_dict['SUMMARY'], 'Event One')
    self.assertEquals( # if this fail for you, try to set $TZ to Europe/Paris
        feed_dict['DTSTART'], '20070815T083000Z')
    self.assertEquals(feed_dict['DTEND'], '20070815T093000Z')
    self.assertEquals(feed_dict['CREATED'], event.getCreationDate().HTML4().replace('-','').replace(':',''))
    self.assertEquals(feed_dict['UID'], 'uuid%s' % event.getUid())
    # set stop date
    event.setStopDate('2007/08/15 15:30')
    event.reindexObject()
    self.tic()
    feed_dict = self.getICalFeed(module)
    self.assertEquals(feed_dict['DTEND'], '20070815T133000Z')
    # check categorization
    sale_op = self.portal.sale_opportunity_module.newContent(portal_type='Sale Opportunity', title='New Opportunity', reference='NEWSALEOP')
    event.setFollowUp(sale_op.getRelativeUrl())
    get_transaction().commit()
    event.reindexObject()
    sale_op.reindexObject()
    self.tic()
    feed_dict = self.getICalFeed(module)
    self.assertTrue(feed_dict['CATEGORIES'] in ('NEWSALEOP', 'New Opportunity')) # forward compatibility

  def test_02_renderTask(self, quiet=0, run=run_all_test):
    """
      Task - is rendered as "todo".
      Additionally, it has "status" and "percent-complete" fields which change
      when the task moves along task_workflow.
    """
    module = self.portal.task_module
    task = module.newContent(id='one', title='Task One', start_date='2007/08/15')
    get_transaction().commit()
    task.reindexObject()
    self.tic()
    # dates work the same way, so we don't have to repeat it
    # draft
    feed_dict = self.getICalFeed(module)
    self.assertTrue('BEGIN:VCALENDAR' in feed_dict.keys())
    self.assertTrue('END:VCALENDAR' in feed_dict.keys())
    self.assertEquals(feed_dict['SUMMARY'], 'Task One')
    self.assertTrue('BEGIN:VTODO' in feed_dict.keys())
    self.assertEquals(feed_dict['STATUS'], 'NEEDS-ACTION')
    self.assertEquals(feed_dict.get('PERCENT-COMPLETE', '0'), '0') # when it is zero it doesn't have to be there
    # now we check categorization (while we can edit the object)
    project = self.portal.project_module.newContent(portal_type='Project', title='New Project', reference='NEWPROJ')
    task.setSourceProjectValue(project)
    get_transaction().commit()
    project.reindexObject()
    task.reindexObject()
    self.tic()
    feed_dict = self.getICalFeed(module)
    self.assertEquals(feed_dict['CATEGORIES'], 'NEWPROJ')
    # planned
    task.plan()
    get_transaction().commit()
    feed_dict = self.getICalFeed(module)
    self.assertEquals(feed_dict['STATUS'], 'NEEDS-ACTION')
    self.assertEquals(feed_dict['PERCENT-COMPLETE'], '33')
    # ordered
    task.order()
    get_transaction().commit()
    feed_dict = self.getICalFeed(module)
    self.assertEquals(feed_dict['STATUS'], 'IN-PROCESS')
    self.assertEquals(feed_dict['PERCENT-COMPLETE'], '66')
    # confirmed
    task.confirm()
    get_transaction().commit()
    feed_dict = self.getICalFeed(module)
    self.assertEquals(feed_dict['STATUS'], 'COMPLETED')
    self.assertEquals(feed_dict['PERCENT-COMPLETE'], '100')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestICal))
  return suite

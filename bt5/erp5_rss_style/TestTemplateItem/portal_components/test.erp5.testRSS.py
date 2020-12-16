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

import time
import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager

from xml.dom.minidom import parseString



def getNodeContent(node):
  return node.childNodes[0].nodeValue

def getSubnodeContent(node, tagName, index=0):
  try:
    return getNodeContent(node.getElementsByTagName(tagName)[index])
  except IndexError:
    return None


class TestRSS(ERP5TypeTestCase):

  run_all_test = 1

  def getTitle(self):
    return "RSS Test"

  def getBusinessTemplateList(self):
    """  """
    return ('erp5_base', 'erp5_rss_style')

  def afterSetUp(self):
    self.portal = self.getPortal()
    self.makeDataObjects()
    #self.login()

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
    if hasattr(self.portal.person_module, 'two'):
      self.portal.person_module.manage_delObjects(['two'])
    self.portal.person_module.newContent(id="one", title="One", description="Person One")
    # We will be sorting persons by creationg date, and SQL sorting will fail
    # when documents are created within the same second. So sleep for one
    # second to make sorting behave reliably. This should not matter in real
    # use, but is a noisy issue in tests.
    time.sleep(1)
    self.portal.person_module.newContent(id="two", title="Two", description="Person Two")
    self.tic()

  def test_00_haveData(self, quiet=0, run=run_all_test):
    """
      Check we have people.
    """
    module = self.portal.person_module
    self.assertEqual(module.one.getTitle(), "One")
    self.assertEqual(module.two.getTitle(), "Two")

  def test_01_renderRSS(self, quiet=0, run=run_all_test):
    """
      View person module as RSS, parse XML, see if everything is there.
    """
    portal=self.getPortal()
    request=self.app.REQUEST

    request.set('portal_skin', 'RSS')
    portal.portal_skins.changeSkin('RSS')

    one = self.portal.person_module.one
    two = self.portal.person_module.two

    feed_string = self.portal.person_module.Folder_viewContentListAsRSS()
    doc = parseString(feed_string)
    rss = doc.childNodes[0]
    channel = rss.getElementsByTagName('channel')[0]
    self.assertEqual(len(rss.getElementsByTagName('channel')), 1)
    self.assertEqual(len(channel.getElementsByTagName('item')), 2)

    titles = [getNodeContent(n) for n in channel.getElementsByTagName('title')]
    titles.sort()
    self.assertEqual(titles, ['One', 'Persons',  'Two']) # there is channel title and person titles

    item = channel.getElementsByTagName('item')[0] # the two person, because we have default sorting in form
    self.assertEqual(getSubnodeContent(item, 'title'), 'Two')
    self.assertEqual(getSubnodeContent(item, 'description'), 'Person Two')
    self.assertEqual(getSubnodeContent(item, 'author'), 'seb')
    expected_link = '%s/view' %two.absolute_url()
    self.assertEqual(getSubnodeContent(item, 'link'), expected_link)
    self.assertEqual(len(item.getElementsByTagName('pubDate')), 1)
    # is date formatted correctly?
    self.assertEqual(two.getCreationDate().rfc822(), getSubnodeContent(item, 'pubDate'))

    item = channel.getElementsByTagName('item')[1] # the one person
    self.assertEqual(getSubnodeContent(item, 'title'), 'One')
    self.assertEqual(getSubnodeContent(item, 'description'), 'Person One')
    self.assertEqual(getSubnodeContent(item, 'author'), 'seb')
    expected_link = '%s/view' %one.absolute_url()
    self.assertEqual(getSubnodeContent(item, 'link'), expected_link)
    self.assertEqual(len(item.getElementsByTagName('pubDate')), 1)
    # is date formatted correctly?
    self.assertEqual(one.getCreationDate().rfc822(), getSubnodeContent(item, 'pubDate'))

  def test_02_renderRSS(self, quiet=0, run=run_all_test):
    """
      View person module as RSS, parse XML, see if everything is there.
      In this case pt for render current form('Test_view') is default page template
      and some listbox's columns(i.e. description) label not present in required channel fields
    """
    portal=self.getPortal()
    request=self.app.REQUEST

    request.set('portal_skin', 'RSS')
    portal.portal_skins.changeSkin('RSS')

    self.getPortal().manage_addProduct['ERP5Form'].addERP5Form('Test_view', 'View')
    portal.Test_view.manage_addField('listbox', 'listbox', 'ListBox')
    portal.Test_view.manage_addField('listbox_link',  'listbox_link',  'StringField')

    listbox=portal.Test_view.listbox
    self.assertNotEquals(listbox, None)
    listbox_link=portal.Test_view.listbox_link
    self.assertNotEquals(listbox_link,  None)

    listbox.manage_edit_xmlrpc(
        dict(columns=[('title', 'Title'),
                      ('creation_date', 'pubDate'),
                      ('Base_getRSSAuthor','author'),
                      ('link','link'),
                      ('absolute_url', 'guid')],
             sort=[('creation_date', 'descending')],
             list_action='list',
             search=1,
             select=1,
             list_method='searchFolder',
             count_method='countFolder',
             selection_name='rss_folder_selection'))

    listbox_link.manage_tales_xmlrpc(
        dict(default="python: cell.absolute_url()"))

    one = self.portal.person_module.one
    two = self.portal.person_module.two

    feed_string = self.portal.person_module.Test_view()
    doc = parseString(feed_string)
    rss = doc.childNodes[0]
    channel = rss.getElementsByTagName('channel')[0]
    self.assertEqual(len(rss.getElementsByTagName('channel')), 1)
    self.assertEqual(len(channel.getElementsByTagName('item')), 2)

    titles = [getNodeContent(n) for n in channel.getElementsByTagName('title')]
    titles.sort()
    self.assertEqual(titles, ['One', 'Persons',  'Two']) # there is channel title and person titles

    item = channel.getElementsByTagName('item')[0] # the two person, because we have default sorting in form
    self.assertEqual(getSubnodeContent(item, 'title'), 'Two')
    self.assertEqual(getSubnodeContent(item, 'description'), 'Person Two')
    self.assertEqual(getSubnodeContent(item, 'author'), 'seb')
    expected_link = two.absolute_url()
    self.assertEqual(getSubnodeContent(item, 'link'), expected_link)
    self.assertEqual(len(item.getElementsByTagName('pubDate')), 1)
    # is date formatted correctly?
    self.assertEqual(two.getCreationDate().rfc822(), getSubnodeContent(item, 'pubDate'))

    item = channel.getElementsByTagName('item')[1] # the one person
    self.assertEqual(getSubnodeContent(item, 'title'), 'One')
    self.assertEqual(getSubnodeContent(item, 'description'), 'Person One')
    self.assertEqual(getSubnodeContent(item, 'author'), 'seb')
    expected_link = one.absolute_url()
    self.assertEqual(getSubnodeContent(item, 'link'), expected_link)
    self.assertEqual(len(item.getElementsByTagName('pubDate')), 1)
    # is date formatted correctly?
    self.assertEqual(one.getCreationDate().rfc822(), getSubnodeContent(item, 'pubDate'))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRSS))
  return suite

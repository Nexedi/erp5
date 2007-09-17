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

from xml.dom.minidom import parseString

try:
  from transaction import get as get_transaction
except ImportError:
  pass


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
      (we create only one because we'd have sorting problems)
    """
    if hasattr(self.portal.person_module, 'one'):
      self.portal.person_module.manage_delObjects(['one'])
    one = self.portal.person_module.newContent(id="one", title="One", description="Person One")
    get_transaction().commit()
    one.reindexObject()
    self.tic()

  def test_00_haveData(self, quiet=0, run=run_all_test):
    """
      Check we have people.
    """
    module = self.portal.person_module
    self.assertEquals(module.one.getTitle(), "One")

  def test_01_renderRSS(self, quiet=0, run=run_all_test):
    """
      View person module as RSS, parse XML, see if everything is there.
    """
    one = self.portal.person_module.one
    feed_string = self.portal.person_module.Folder_viewContentListAsRSS()
    doc = parseString(feed_string)
    rss = doc.childNodes[0]
    channel = rss.getElementsByTagName('channel')[0]
    titles = [getNodeContent(n) for n in channel.getElementsByTagName('title')]
    titles.sort()
    self.assertEquals(titles, ['One', 'Persons']) # there is channel title and person title
    self.assertEquals(len(channel.getElementsByTagName('item')), 1)
    item = channel.getElementsByTagName('item')[0] # the one person
    self.assertEquals(getSubnodeContent(item, 'title'), 'One')
    self.assertEquals(getSubnodeContent(item, 'description'), 'Person One')
    self.assertEquals(getSubnodeContent(item, 'author'), 'seb')
    expected_link = one.absolute_url() + '/view'
    self.assertEquals(getSubnodeContent(item, 'link'), expected_link)
    self.assertEquals(len(item.getElementsByTagName('pubDate')), 1)
    # is date formatted correctly?
    self.assertEquals(one.getCreationDate().rfc822(), getSubnodeContent(item, 'pubDate'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRSS))
  return suite

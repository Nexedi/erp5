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
from DateTime import DateTime

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

  def makeDataObjects(self, quiet=0, run=run_all_test):
    """
      Create some Pesons so that we have something to feed.
    """
    now = DateTime()
    if hasattr(self.portal.support_request_module, 'sr1'):
      self.portal.support_request_module.manage_delObjects(['sr1'])
    if hasattr(self.portal.support_request_module, 'sr2'):
      self.portal.support_request_module.manage_delObjects(['sr2'])
    support_request_2 = self.portal.support_request_module.newContent(
      portal_type='Support Request',
      id="sr2",
      title="SR2"
    )
    support_request_1 = self.portal.support_request_module.newContent(
      portal_type='Support Request',
      id="sr1",
      title="SR1"
    )
    support_request_1.edit(
      start_date=now,
    )
    self.commit()
    support_request_2.reindexObject()
    support_request_1.reindexObject()
    self.tic()

  def test_00_haveData(self, quiet=0, run=run_all_test):
    """
      Check we have people.
    """
    module = self.portal.support_request_module
    self.assertEqual(module.sr1.getTitle(), "SR1")
    self.assertEqual(module.sr2.getTitle(), "SR2")

  def test_01_renderRSS(self, quiet=0, run=run_all_test):
    """
      View person module as RSS, parse XML, see if everything is there.
    """
    portal=self.getPortal()
    request=self.app.REQUEST

    request.set('portal_skin', 'RSS')
    portal.portal_skins.changeSkin('RSS')

    sr1 = self.portal.support_request_module.sr1
    sr2 = self.portal.support_request_module.sr2

    feed_string = self.portal.support_request_module.SupportRequestModule_viewLastSupportRequestListAsRss()
    doc = parseString(feed_string)
    rss = doc.childNodes[0]
    # self.assertEqual(feed_string, "hello")
    channel = rss.getElementsByTagName('channel')[0]
    self.assertEqual(len(rss.getElementsByTagName('channel')), 1)

    titles = [getNodeContent(n) for n in channel.getElementsByTagName('title')]
    titles.sort()
    self.assertEqual(titles[:2], ['SR1', 'SR2']) # there is channel title and person titles

    item = channel.getElementsByTagName('item')[0] # the Support Request

    self.assertEqual(getSubnodeContent(item, 'title'), 'SR1')

    sr1_link = sr1.absolute_url()
    hash_position = sr1_link.index('support_request_module')
    new_sr1_link = sr1_link[:hash_position] + '#/' + sr1_link[hash_position:]

    self.assertEqual(getSubnodeContent(item, 'link'), new_sr1_link)
    self.assertEqual(len(item.getElementsByTagName('pubDate')), 1)
    # is date formatted correctly?
    self.assertEqual(sr1.getCreationDate().rfc822(), getSubnodeContent(item, 'pubDate'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRSS))
  return suite
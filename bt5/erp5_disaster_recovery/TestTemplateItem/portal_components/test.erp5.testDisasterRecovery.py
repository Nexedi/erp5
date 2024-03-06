##############################################################################
#
# Copyright (c) 2002-2024 Nexedi SA and Contributors. All Rights Reserved.
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

class TestDisasterRecovery(ERP5TypeTestCase):
  """
  Test Disaster Recover
  """

  def test_missing_catalog(self):
    document = self.portal.person_module.newContent(
      portal_type='Person',
      title='Person for Disaster Recovery'
    )
    self.tic()

    _document = self.portal.portal_catalog.getResultValue(
      uid=document.getUid()
    )
    self.assertNotEqual(_document, None)
    self.assertEqual(document.getUid(), _document.getUid())

    self.portal.portal_catalog.uncatalog_object(uid=document.getUid())
    self.tic()
    _document = self.portal.portal_catalog.getResultValue(
      uid=document.getUid()
    )
    self.assertEqual(_document, None)

    self.portal.ERP5Site_recoverFromRestoration()
    self.tic()

    _document = self.portal.portal_catalog.getResultValue(
      uid=document.getUid()
    )
    self.assertNotEqual(_document, None)
    self.assertEqual(document.getUid(), _document.getUid())

  def test_catalog_but_deleted(self):
    if self.portal.person_module.getIdGenerator() != '_generatePerDayId':
      self.portal.person_module.setIdGenerator('_generatePerDayId')

    document = self.portal.person_module.newContent(
      portal_type='Person',
      title='Person for Disaster Recovery'
    )
    self.tic()

    _document = self.portal.portal_catalog.getResultValue(
      uid=document.getUid()
    )
    self.assertNotEqual(_document, None)
    self.assertEqual(document.getUid(), _document.getUid())

    # Force remove the  object w/o trigger updates on catalog
    self.portal.person_module._objects = tuple([
      i for i in self.portal.person_module._objects
                               if i['id'] != document.getId()])
    self.portal.person_module._delOb(document.getId())
    self.tic()

    connection = self.getSQLConnection()
    doc_list = connection.manage_test(
      "select * from catalog where path = '/erp5/%s'" % document.getRelativeUrl())
    self.assertEqual(len(doc_list), 1)

    doc_list = connection.manage_test("select * from catalog where uid = %s" % document.getUid())
    self.assertEqual(len(doc_list), 1)

    self.portal.ERP5Site_recoverFromRestoration()
    self.tic()

    ac = connection.manage_test("select * from catalog where uid = %s" % document.getUid())
    self.assertEqual(len(ac), 0)

    _document = self.portal.portal_catalog(uid=document.getUid())
    self.assertEqual(len(_document), 0)

  def test_cataloged_is_inconsistent(self):
    document = self.portal.person_module.newContent(
      portal_type='Person',
      title='Person for Disaster Recovery %s' % (
        str(self.portal.portal_ids.generateNewId(
         id_group=('erp5_disaster_recovery_test_id')))))
    self.tic()

    _document = self.portal.portal_catalog.getResultValue(
      uid=document.getUid()
    )
    self.assertNotEqual(_document, None)
    self.assertEqual(document.getUid(), _document.getUid())

    connection = self.getSQLConnection()
    connection.manage_test("update catalog set title = 'modified title' where uid = %s" % document.getUid())
    connection.manage_test("commit")
    self.commit()
    
    _document = self.portal.portal_catalog(title='modified title')
    self.assertEqual(len(_document), 1)

    _document = self.portal.portal_catalog(title=document.getTitle())
    self.assertEqual(len(_document), 0)

    self.portal.ERP5Site_recoverFromRestoration()
    self.tic()

    _document = self.portal.portal_catalog(title='modified title')
    self.assertEqual(len(_document), 0)

    _document = self.portal.portal_catalog(title=document.getTitle())
    self.assertEqual(len(_document), 1)
    _document = self.portal.portal_catalog(title=document.getTitle())
    self.assertEqual(_document[0].getUid(), document.getUid())
    

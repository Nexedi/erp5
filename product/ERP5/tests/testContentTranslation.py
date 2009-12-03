# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi KK, Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import transaction


class TestContentTranslation(ERP5TypeTestCase):
  """
  Test Content Translation
  """

  def getTitle(self):
    return 'Test Content Translation'

  def getBusinessTemplateList(self):

    return ('erp5_base',
            'erp5_content_translation',
            )

  def afterSetUp(self):
    # set up translation domain on Person type information.
    from Products.ERP5Type.Accessor.Translation import TRANSLATION_DOMAIN_CONTENT_TRANSLATION
    self.portal.portal_types.Person.changeTranslations(
      dict(first_name=TRANSLATION_DOMAIN_CONTENT_TRANSLATION,
           last_name=TRANSLATION_DOMAIN_CONTENT_TRANSLATION))

  def testContentTranslation(self):
    """
    Make sure that translatable properties can have content translation into
    the document and read/write translation text by special accessors.
    """
    portal = self.portal
    person = portal.person_module.newContent(id='yusei',
                                             portal_type='Person',
                                             first_name='Yusei',
                                             last_name='Tahara')
    portal.person_module.newContent(id='tarou',
                                    portal_type='Person',
                                    first_name='Tarou',
                                    last_name='Suzuki')
    portal.person_module.newContent(id='john',
                                    portal_type='Person',
                                    first_name='John',
                                    last_name='Smith')
    transaction.commit()
    self.tic()

    self.assertEqual(getattr(person, 'setJaKanaTranslatedFirstName', False),
                     False)
    self.assertEqual(getattr(person, 'getJaKanaTranslatedFirstName', False),
                     False)
    self.assert_(getattr(person, 'getEnTranslatedFirstName', False))
    self.assert_(getattr(person, 'getEnTranslatedFirstName', False))

    portal.Localizer._add_user_defined_language('Japanese Kana', 'ja-kana')
    portal.Localizer.add_language('ja-kana')
    transaction.commit()
    self.tic()

    self.assert_(getattr(person, 'setJaKanaTranslatedFirstName', False))
    self.assert_(getattr(person, 'getJaKanaTranslatedFirstName', False))

    person.setJaKanaTranslatedFirstName('タハラ')
    person.setJaKanaTranslatedLastName('ユウセイ')

    transaction.commit()
    self.tic()

    self.assert_('タハラ' in person.Base_viewContentTranslation())
    self.assert_('ユウセイ' in person.Base_viewContentTranslation())

    self.assertEqual(person.getJaKanaTranslatedFirstName(), 'タハラ')
    self.assertEqual(person.getJaKanaTranslatedLastName(), 'ユウセイ')
    self.assertEqual(person.getTranslatedTitle(language='ja-kana'),
                     'タハラ ユウセイ')

    # check with acquisition
    self.assertEquals(person.getAddress(), None)
    
    person.setDefaultAddressStreetAddress('Taito-ku Tokyo')
    self.assertEquals(person.getDefaultAddressStreetAddress(), 'Taito-ku Tokyo')

    person.setDefaultAddressJaKanaTranslatedStreetAddress('東京都 台東区')
    self.assertEquals(person.getDefaultAddressJaKanaTranslatedStreetAddress(), '東京都 台東区')
    self.assertEquals(person.getDefaultAddressTranslatedStreetAddress(language='ja-kana'), '東京都 台東区')

    # check acquired target
    address = person.getDefaultAddress()
    self.assertEquals(address.getStreetAddress(), 'Taito-ku Tokyo')
    self.assertEquals(address.getJaKanaTranslatedStreetAddress(), '東京都 台東区')
    self.assertEquals(address.getTranslatedStreetAddress(language='ja-kana'), '東京都 台東区')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestContentTranslation))
  return suite

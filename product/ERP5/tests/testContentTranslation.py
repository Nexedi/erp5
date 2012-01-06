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
from Products.ERP5Type.tests.utils import to_utf8
import transaction


class TestContentTranslation(ERP5TypeTestCase):
  """
  Test Content Translation
  """

  def getTitle(self):
    return 'Test Content Translation'

  def getBusinessTemplateList(self):

    return ('erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_content_translation',
            )

  def afterSetUp(self):
    # set up translation domain on Person type information.
    from Products.ERP5Type.Accessor.Translation import TRANSLATION_DOMAIN_CONTENT_TRANSLATION
    setTranslationDomain = self.portal.portal_types.Person.setTranslationDomain
    setTranslationDomain('first_name', TRANSLATION_DOMAIN_CONTENT_TRANSLATION)
    setTranslationDomain('last_name', TRANSLATION_DOMAIN_CONTENT_TRANSLATION)

  def testCatalogSearch(self):
    """
    Search a person's properties and translated properties with catalog.
    """
    portal = self.portal

    portal.Localizer._add_user_defined_language('Nobody Readable', 'nob-read')
    portal.Localizer.add_language('nob-read')
    transaction.commit()
    self.tic()

    person1 = portal.person_module.newContent(portal_type='Person',
                                              first_name='first_name_of_p1',
                                              last_name='last_name_of_p1')
    person2 = portal.person_module.newContent(portal_type='Person',
                                              first_name='first_name_of_p2',
                                              last_name='last_name_of_p2')
    person3 = portal.person_module.newContent(portal_type='Person',
                                              first_name='Yusuke',
                                              last_name='Muraoka')
    person1.setNobReadTranslatedFirstName('XXX')
    person1.setNobReadTranslatedLastName('YYY')
    person2.setNobReadTranslatedFirstName('---')
    person2.setNobReadTranslatedLastName('   ')
    person3.setNobReadTranslatedFirstName('友介')
    person3.setNobReadTranslatedLastName('村岡')
    self.assertEqual(person1.getNobReadTranslatedFirstName('XXX'), 'XXX')
    self.assertEqual(person1.getNobReadTranslatedLastName('YYY'), 'YYY')
    self.assertEqual(person2.getNobReadTranslatedFirstName('---'), '---')
    self.assertEqual(person2.getNobReadTranslatedLastName('   '), '   ')
    self.assertEqual(person3.getNobReadTranslatedFirstName('友介'), '友介')
    self.assertEqual(person3.getNobReadTranslatedLastName('村岡'), '村岡')
    transaction.commit()
    self.tic()

    result1 = portal.portal_catalog(content_translation_title='Yusuke')
    self.assertEquals(len(result1), 1)
    result_obj1 = result1[0].getObject()

    result2 = portal.portal_catalog(content_translation_title='友介')
    self.assertEquals(len(result2), 1)
    result_obj2 = result2[0].getObject()

    self.assertEquals(result_obj1, result_obj2)

    # re-catalog
    person3.setNobReadTranslatedFirstName('ゆうすけ')
    transaction.commit()
    self.tic()

    result3 = portal.portal_catalog(content_translation_title='友介')
    self.assertEquals(len(result3), 0)

    # un-catalog
    portal.person_module.manage_delObjects(person3.getId())
    transaction.commit()
    self.tic()

    result4 = portal.portal_catalog(content_translation_title='村岡')
    self.assertEquals(len(result4), 0)

    # columns test
    result5 = portal.portal_catalog(property_name='title')
    self.assertEquals(len(result5), 2)
    result6 = portal.portal_catalog(content_language='nob-read')
    self.assertEquals(len(result6), 2)
    result7 = portal.portal_catalog(translated_text='XXX YYY')
    self.assertEquals(len(result7), 1)
 
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

    ##
    # Add custom local.language
    ##
    portal.Localizer._add_user_defined_language('Japanese Kana', 'ja-kana')
    portal.Localizer.add_language('ja-kana')
    transaction.commit()
    self.tic()

    self.assert_(getattr(person, 'setJaKanaTranslatedFirstName', False))
    self.assert_(getattr(person, 'getJaKanaTranslatedFirstName', False))
    self.assert_(getattr(person, 'hasJaKanaTranslatedFirstName', False))

    self.assert_(not person.hasJaKanaTranslatedFirstName())

    # if there is no translation, original value is returned.
    self.assertEqual('Yusei', person.getTranslatedFirstName())
    self.assertEqual('Yusei Tahara', person.getTranslatedTitle())
    self.assertEqual('Yusei', person.getJaKanaTranslatedFirstName())
    # if no_original_value parameter is true, an empty string is returned.
    self.assertEqual('', person.getTranslatedFirstName(no_original_value=True))
    self.assertEqual('', person.getTranslatedTitle(no_original_value=True))
    self.assertEqual('', person.getJaKanaTranslatedFirstName(no_original_value=True))

    person.setJaKanaTranslatedFirstName('タハラ')
    person.setJaKanaTranslatedLastName('ユウセイ')

    self.assert_(person.hasJaKanaTranslatedFirstName())

    transaction.commit()
    self.tic()

    self.assert_('タハラ' in to_utf8(person.Base_viewContentTranslation()))
    self.assert_('ユウセイ' in to_utf8(person.Base_viewContentTranslation()))

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

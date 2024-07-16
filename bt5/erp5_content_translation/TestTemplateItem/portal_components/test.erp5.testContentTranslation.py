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

  def setUpOnce(self):
    # set up translation domain on Person type information.
    from Products.ERP5Type.Accessor.Translation import TRANSLATION_DOMAIN_CONTENT_TRANSLATION
    setTranslationDomain = self.portal.portal_types.Person.setTranslationDomain
    setTranslationDomain('first_name', TRANSLATION_DOMAIN_CONTENT_TRANSLATION)
    setTranslationDomain('last_name', TRANSLATION_DOMAIN_CONTENT_TRANSLATION)
    setTranslationDomain('title', TRANSLATION_DOMAIN_CONTENT_TRANSLATION)
    self.portal.portal_caches.manage_clearAllCache()

  def testCatalogSearch(self):
    """
    Search a person's properties and translated properties with catalog.
    """
    portal = self.portal

    portal.Localizer._add_user_defined_language('Nobody Readable', 'nob-read')
    portal.Localizer.add_language('nob-read')
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
    self.tic()

    result1 = portal.portal_catalog(content_translation_title='Yusuke')
    self.assertEqual(len(result1), 1)
    result_obj1 = result1[0].getObject()

    result2 = portal.portal_catalog(content_translation_title='友介')
    self.assertEqual(len(result2), 1)
    result_obj2 = result2[0].getObject()

    self.assertEqual(result_obj1, result_obj2)

    # re-catalog
    person3.setNobReadTranslatedFirstName('ゆうすけ')
    self.tic()

    result3 = portal.portal_catalog(content_translation_title='友介')
    self.assertEqual(len(result3), 0)

    # un-catalog
    portal.person_module.manage_delObjects(person3.getId())
    self.tic()

    result4 = portal.portal_catalog(content_translation_title='村岡')
    self.assertEqual(len(result4), 0)

    # Low level columns test. This behaviour is not guaranteed. I'm not sure
    # content_translation must be a search table - jerome
    result5 = portal.portal_catalog(property_name='title')
    self.assertGreaterEqual(len(result5), 2)
    result6 = portal.portal_catalog(content_language='nob-read')
    self.assertEqual(len(result6), 2)
    result7 = portal.portal_catalog(translated_text='XXX YYY')
    self.assertEqual(len(result7), 1)

  def testCatalogSearchTranslatedTitleScriptableKey(self):
    # Test 'translated_title' scriptable key.
    portal = self.portal

    portal.Localizer._add_user_defined_language('Nobody Readable', 'nob-read')
    portal.Localizer.add_language('nob-read')
    self.tic()

    person = portal.person_module.newContent(portal_type='Person',
                                             first_name='Yusuke',
                                             last_name='Muraoka')
    person.setNobReadTranslatedFirstName('友介')
    person.setNobReadTranslatedLastName('村岡')
    self.tic()

    # We can search either by the translated title
    self.assertEqual(person,
      portal.portal_catalog.getResultValue(translated_title='友介'))
    # Or the original title
    self.assertEqual(person,
      portal.portal_catalog.getResultValue(translated_title='Yusuke'))

    # The key also behave like "title" key, ie. we can use % for partial matches
    self.assertEqual(person,
      portal.portal_catalog.getResultValue(translated_title='Yusu%'))
    self.assertEqual(person,
      portal.portal_catalog.getResultValue(translated_title='%岡'))
    self.assertEqual(person,
      portal.portal_catalog.getResultValue(translated_title='%村%'))
    self.assertEqual(person,
      portal.portal_catalog.getResultValue(translated_title='Yus% OR %oka'))

    # Deleting translation should update content_translation table.
    person.setNobReadTranslatedFirstName('')
    person.setNobReadTranslatedLastName('')
    self.tic()
    self.assertEqual(None,
      portal.portal_catalog.getResultValue(translated_title='友介'))
    self.assertEqual(person,
      portal.portal_catalog.getResultValue(translated_title='Yusuke'))

    # documents for which translation is not set can also be found with
    # translated_title key
    not_translated_person = portal.person_module.newContent(portal_type='Person',
                                             first_name='Jérome',
                                             last_name='Perrin')
    self.tic()
    self.assertEqual(not_translated_person,
      portal.portal_catalog.getResultValue(translated_title='Jérome'))


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
    self.tic()

    self.assertEqual(getattr(person, 'setJaKanaTranslatedFirstName', False),
                     False)
    self.assertEqual(getattr(person, 'getJaKanaTranslatedFirstName', False),
                     False)
    self.assertTrue(getattr(person, 'getEnTranslatedFirstName', False))
    self.assertTrue(getattr(person, 'getEnTranslatedFirstName', False))

    ##
    # Add custom local.language
    ##
    portal.Localizer._add_user_defined_language('Japanese Kana', 'ja-kana')
    portal.Localizer.add_language('ja-kana')
    self.tic()

    self.assertTrue(getattr(person, 'setJaKanaTranslatedFirstName', False))
    self.assertTrue(getattr(person, 'getJaKanaTranslatedFirstName', False))
    self.assertTrue(getattr(person, 'hasJaKanaTranslatedFirstName', False))

    self.assertTrue(not person.hasJaKanaTranslatedFirstName())

    # if there is no translation, original value is returned.
    self.assertEqual(None, getattr(person, '__translation_dict', None))
    self.assertEqual('Yusei', person.getTranslatedFirstName())
    self.assertEqual('Yusei Tahara', person.getTranslatedTitle())
    self.assertEqual('Yusei', person.getJaKanaTranslatedFirstName())
    # if no_original_value parameter is true, an empty string is returned.
    self.assertEqual('', person.getTranslatedFirstName(no_original_value=True))
    self.assertEqual('', person.getTranslatedTitle(no_original_value=True))
    self.assertEqual('', person.getJaKanaTranslatedFirstName(no_original_value=True))
    # Make sure that until any value is set, we do not create useless __translation_dict
    self.assertEqual(None, getattr(person, '__translation_dict', None))

    person.setJaKanaTranslatedFirstName('タハラ')
    person.setJaKanaTranslatedLastName('ユウセイ')
    # Since we add some translated value, we now must have some data in __translation_dict
    translation_dict = getattr(person, '__translation_dict', None)
    self.assertNotEqual(None, translation_dict)
    self.assertEqual(set([('last_name', 'ja-kana'), ('first_name', 'ja-kana')]),
                     set(translation_dict.keys()))

    self.assertTrue(person.hasJaKanaTranslatedFirstName())

    self.tic()

    x = person.Base_viewContentTranslation()
    self.assertIn(u'タハラ', x)
    self.assertIn(u'ユウセイ', x)

    self.assertEqual(person.getJaKanaTranslatedFirstName(), 'タハラ')
    self.assertEqual(person.getJaKanaTranslatedLastName(), 'ユウセイ')
    self.assertEqual(person.getTranslatedTitle(language='ja-kana'),
                     'タハラ ユウセイ')

    # check with acquisition
    self.assertEqual(person.getAddress(), None)

    person.setDefaultAddressStreetAddress('Taito-ku Tokyo')
    self.assertEqual(person.getDefaultAddressStreetAddress(), 'Taito-ku Tokyo')

    person.setDefaultAddressJaKanaTranslatedStreetAddress('東京都 台東区')
    self.assertEqual(person.getDefaultAddressJaKanaTranslatedStreetAddress(), '東京都 台東区')
    self.assertEqual(person.getDefaultAddressTranslatedStreetAddress(language='ja-kana'), '東京都 台東区')

    # check acquired target
    address = person.getDefaultAddress()
    self.assertEqual(address.getStreetAddress(), 'Taito-ku Tokyo')
    self.assertEqual(address.getJaKanaTranslatedStreetAddress(), '東京都 台東区')
    self.assertEqual(address.getTranslatedStreetAddress(language='ja-kana'), '東京都 台東区')


  def test_getInstancePropertySet(self):
    """Translatable properies are returned by getInstancePropertySet
    """
    self.assertIn('en_translated_first_name',
      self.portal.portal_types.Person.getInstancePropertySet())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestContentTranslation))
  return suite

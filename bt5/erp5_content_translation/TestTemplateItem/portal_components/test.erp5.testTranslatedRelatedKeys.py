##############################################################################
# coding: utf-8
# Copyright (c) 2002-2020 Nexedi SA and Contributors. All Rights Reserved.
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

import mock

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestTranslatedRelatedKeys(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return (
        'erp5_base',
        'erp5_content_translation',
        'erp5_l10n_fr',
        'erp5_l10n_jp',
    )

  def afterSetUp(self):
    # For this test we will use:
    #  * title as "content translated properties" on Organisation
    #  * short_title as "content translated properties" on Organisation (because it contain a _,
    #    to make sure we are supporting properties with _)
    #  * some "group" categories and their translations in erp5_content
    #  * two organisations
    self.portal.portal_types.Organisation.setTranslationDomain(
        prop_name='title', domain='content_translation')
    self.portal.portal_types.Organisation.setTranslationDomain(
        prop_name='short_title', domain='content_translation')

    # clear cache because ERP5Site_getPortalTypeContentTranslationMapping uses
    # a cache.
    self.commit()
    self.portal.portal_caches.clearCacheFactory('erp5_content_long')

    # translations for categories
    message_catalog = self.portal.Localizer.erp5_content
    message_catalog.add_language('fr')
    message_catalog.add_language('ja')
    message_catalog.gettext('Nexedi', add=True)
    message_catalog.gettext('Another', add=True)
    message_catalog.message_edit('Nexedi', 'fr', u'Catégorie Nexedi', '')
    message_catalog.message_edit('Another', 'fr', u'Autre Catégorie', '')
    message_catalog.message_edit('Nexedi', 'ja', u'ネクセディカテゴリー', '')
    message_catalog.message_edit('Another', 'ja', u'別カテゴリー', '')

    # categories (which will be translated using erp5_content)
    group_base_category = self.portal.portal_categories.group
    if 'nexedi' not in group_base_category.objectIds():
      group_base_category.newContent(id='nexedi', title='Nexedi')
    if 'another' not in group_base_category.objectIds():
      group_base_category.newContent(id='another', title='Another')

    self.organisation_nexedi = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='Nexedi',
        short_title='Nexedi SA',
        group_value=group_base_category.nexedi,
    )
    self.organisation_nexedi.setFrTranslatedTitle("Nexedi")
    self.organisation_nexedi.setFrTranslatedShortTitle("Nexedi Société Anonyme")
    self.organisation_nexedi.setJaTranslatedTitle("ネクセディ")
    self.organisation_nexedi.setJaTranslatedShortTitle("ネクセディ 本社")
    self.organisation_another = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='Another not translated Organisation',
        group_value=group_base_category.another,
    )
    self.tic()

  def test_content_translation_search_folder(self):
    folder = self.portal.person_module.newContent(portal_type='Person')
    career_nexedi = folder.newContent(
        portal_type='Career', subordination_value=self.organisation_nexedi)
    career_another = folder.newContent(
        portal_type='Career', subordination_value=self.organisation_another)
    self.tic()

    localizer = self.portal.Localizer
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='ja',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  subordination__translated__title='ネクセディ')
          ], [career_nexedi])
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  subordination__translated__short_title='ネクセディ 本社')
          ], [career_nexedi])
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='fr',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  subordination__translated__title='Nexedi')
          ], [career_nexedi])
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='fr',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  subordination__translated__short_title='Nexedi Société Anonyme'
              )
          ], [career_nexedi])

    # if a translation exist for another language it is not used when language does
    # not match.
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='fr',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  subordination__translated__title='ネクセディ')
          ], [])

    # if property is not translated, the original propery can be used for searching
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='anything',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  subordination__translated__title='Another not translated Organisation'
              )
          ], [career_another])

    # if property is translated, but not in the selected language, the original property
    # can be used for searching
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='other',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  subordination__translated__title='Nexedi')
          ], [career_nexedi])

    # strict
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='ja',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  strict__subordination__translated__title='ネクセディ')
          ], [career_nexedi])

    # sort
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='ja',
    ):
      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  uid=(career_nexedi.getUid(), career_another.getUid()),
                  sort_on=[('subordination__translated__title', 'ASC')])
          ], [career_another, career_nexedi])

      self.assertEqual(
          [
              x.getObject() for x in folder.searchFolder(
                  uid=(career_nexedi.getUid(), career_another.getUid()),
                  sort_on=[('subordination__translated__title', 'DESC')])
          ], [career_nexedi, career_another])

    # select dict
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='ja',
    ):
      self.assertEqual(
          sorted(
              [
                  x.subordination__translated__title
                  for x in folder.searchFolder(
                      uid=(career_nexedi.getUid(), career_another.getUid()),
                      select_dict={'subordination__translated__title': None})
              ]),
          [
              'Another not translated Organisation',
              # XXX select dict is not really good, because we also select rows
              # for the original message (translation_language = "")
              'Nexedi',
              'ネクセディ',
          ])

  def test_erp5_content_search_folder(self):
    localizer = self.portal.Localizer
    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='ja',
    ):
      self.assertEqual(
          [
              x.getObject()
              for x in self.portal.organisation_module.searchFolder(
                  uid=(
                      self.organisation_nexedi.getUid(),
                      self.organisation_another.getUid()),
                  group__translated__title='ネクセディカテゴリー')
          ], [self.organisation_nexedi])

    with mock.patch.object(
        localizer,
        'get_selected_language',
        return_value='fr',
    ):
      self.assertEqual(
          [
              x.getObject()
              for x in self.portal.organisation_module.searchFolder(
                  uid=(
                      self.organisation_nexedi.getUid(),
                      self.organisation_another.getUid()),
                  group__translated__title='Catégorie Nexedi')
          ], [self.organisation_nexedi])

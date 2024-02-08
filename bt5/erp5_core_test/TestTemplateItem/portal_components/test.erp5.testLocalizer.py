# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest

import six

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Persistence import PersistentMapping
from zope.component.hooks import setSite


class TestLocalizer(ERP5TypeTestCase):
  def afterSetUp(self):
    self.message_catalog = self.portal.Localizer.erp5_ui
    if 'fr' not in self.message_catalog.get_available_languages():
      self.message_catalog.add_language('fr')
    self.message_catalog._messages.clear()

  def beforeTearDown(self):
    tmp_obj = getattr(self, 'tmp_obj', None)
    if tmp_obj is not None:
      tmp_obj.aq_parent.manage_delObjects(ids=[tmp_obj.getId(),])
      self.tic()

  def test_non_ascii_msgid(self):
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "This is 1€.")
    # newly created key should be unicode.
    self.assertNotIn(u'This is 1€.'.encode('utf-8'), self.message_catalog._messages)
    self.assertIn(u'This is 1€.', self.message_catalog._messages)
    self.message_catalog.message_edit(u'This is 1€.', 'fr', u"C'est 1€.", '')
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "C'est 1€.")
    self.assertNotIn(u'This is 1€.'.encode('utf-8'), self.message_catalog._messages)
    self.assertIn(u'This is 1€.', self.message_catalog._messages)

  @unittest.skipIf(six.PY3, "only makes sense for py2")
  def test_migrated_non_ascii_msgid(self):
    # register str key to simulate existing message that was already
    # created by old Localizer.
    self.message_catalog._messages['This is 1€.'] = PersistentMapping(
      {'fr':"C'est 1€.", 'note':'',})
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "C'est 1€.")
    # translate() should not create a unicode key if str key already exists.
    self.assertIn(u'This is 1€.'.encode('utf-8'), self.message_catalog._messages)
    self.assertNotIn(u'This is 1€.', self.message_catalog._messages)
    self.message_catalog.message_edit(u'This is 1€.', 'fr', u"Ceci est 1€.", '')
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "Ceci est 1€.")
    # message_edit() should not create a unicode key if str key already exists.
    self.assertIn(u'This is 1€.'.encode('utf-8'), self.message_catalog._messages)
    self.assertNotIn(u'This is 1€.', self.message_catalog._messages)

  def test_non_ascii_mapping(self):
    self.assertEqual(self.portal.Base_translateString('This is 1${currency}.', lang='fr',
                                                      mapping={'currency': '€'}),
                     "This is 1€.")
    if six.PY2:
      self.assertEqual(
        self.portal.Base_translateString(
          'This is 1${currency}.',
          lang='fr',
          mapping={'currency': u'€'}),
        "This is 1€.")
    self.message_catalog.message_edit(u'This is 1${currency}.', 'fr', u"C'est 1${currency}.", '')
    self.assertEqual(self.portal.Base_translateString('This is 1${currency}.', lang='fr',
                                                      mapping={'currency': '€'}),
                     "C'est 1€.")
    if six.PY2:
      self.assertEqual(
        self.portal.Base_translateString(
          'This is 1${currency}.',
          lang='fr',
          mapping={'currency': u'€'}),
        "C'est 1€.")

  def test_non_literal_mapping(self):
    self.assertEqual(self.portal.Base_translateString('This is ${obj}.', lang='fr',
                                                      mapping={'obj':[1,2]}),
                     "This is [1, 2].")
    self.message_catalog.message_edit(u'This is ${obj}.', 'fr', u"C'est ${obj}.", '')
    self.assertEqual(self.portal.Base_translateString('This is ${obj}.', lang='fr',
                                                      mapping={'obj':[1,2]}),
                     "C'est [1, 2].")

  def test_import_migrated_non_ascii_msgid(self):
    # register str key to simulate existing message that was already
    # created by old Localizer.
    self.message_catalog._messages['This is 1€.'] = PersistentMapping(
      {'fr':"C'est 1€.", 'note':'',})
    self.message_catalog.po_import(
      'fr',
      'msgid "This is 1€."\nmsgstr "Ceci est 1€."')
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "Ceci est 1€.")
    # po_import() converts existing str key to unicode key.
    self.assertNotIn(u'This is 1€.'.encode('utf-8'), self.message_catalog._messages)
    self.assertIn(u'This is 1€.', self.message_catalog._messages)

  def test_localizer_transle_in_activity(self):
    self.assertEqual(self.portal.Base_translateString('This is 1€.', lang='fr'),
                     "This is 1€.")
    self.message_catalog.message_edit(u'This is 1€.', 'fr', u"C'est 1€.", '')
    skin = self.portal.portal_skins.custom
    createZODBPythonScript(
      skin, 'test_activity', '',
      "context.setComment(context.Base_translateString('This is 1€.', lang='fr'))",
      )
    tmp_obj = self.portal.portal_templates.newContent()
    self.tic()
    tmp_obj.activate().test_activity()
    # here we don't call self.tic() that calls self.portal that
    # reinvoke setSite(portal).
    setSite()
    self.commit()
    while self.portal.portal_activities.getMessageList():
      self.portal.portal_activities.process_timer(None, None)
    self.assertEqual(tmp_obj.getComment(), "C'est 1€.")

  def test_get_selected_language(self):
    # default selected language is en
    self.assertEqual('en', self.portal.Localizer.get_selected_language())

  def test_translationContext(self):
    self.message_catalog._messages['This is 1€.'] = PersistentMapping(
      {'fr':"C'est 1€.", 'note':'',})
    localizer = self.portal.Localizer
    with localizer.translationContext('fr'):
      self.assertEqual('fr', localizer.get_selected_language())
      self.assertEqual("C'est 1€.",
        self.portal.Base_translateString("This is 1€."))
    # outside of this context manager we are back to english
    self.assertEqual('en', localizer.get_selected_language())
    self.assertEqual("This is 1€.",
      self.portal.Base_translateString("This is 1€."))

  def test_translationContextActivity(self):
    portal = self.portal
    self.message_catalog._messages['This is 1€.'] = PersistentMapping(
      {'fr':"C'est 1€.", 'note':'',})
    localizer = portal.Localizer

    createZODBPythonScript(portal.portal_skins.custom,
        'test_script', '', """
def assertEquals(a, b):
  if a != b:
    raise AssertionError("%r != %r" % (a, b))
localizer = context.getPortalObject().Localizer
with localizer.translationContext('fr'):
  assertEquals('fr', localizer.get_selected_language())
  assertEquals("C'est 1€.", context.Base_translateString("This is 1€."))
# outside of this context manager we are back to english
assertEquals('en', localizer.get_selected_language())
assertEquals("This is 1€.", context.Base_translateString("This is 1€."))
""")

    # normal activity
    portal.portal_activities.activate().test_script()
    self.tic()
    # after activity execution we are still in english
    self.assertEqual('en', localizer.get_selected_language())
    self.assertEqual("This is 1€.",
      self.portal.Base_translateString("This is 1€."))

    # execute activity with group_method
    portal.portal_activities.activate(group_method_id=None).test_script()
    self.tic()
    # after activity execution we are still in english
    self.assertEqual('en', localizer.get_selected_language())
    self.assertEqual("This is 1€.",
      self.portal.Base_translateString("This is 1€."))

  def test_default_not_changed(self):
    """
    When there is no translation available for a given message, the default
    value (e.g. the original message) must be returned
    """
    message = "   This is 1€ non-translated    "

    # Base_translateString == Localizer.translate() currently, which calls
    # zope.i18n.translate and sets 'default' to 'message' before passing it to
    # MessageCatalog (Localizer.erp5_ui.translate)
    self.assertEqual(message, self.portal.Base_translateString(message))
    translated = self.portal.Localizer.translate('ui', message)
    if six.PY2:
      translated = translated.encode('utf-8')
    self.assertEqual(message, translated)

    # default=None, thus 'message' was previously stripped before being set as
    # 'default' value (MessageCatalog.gettext)
    self.assertEqual(message, self.portal.Localizer.erp5_ui.translate(message))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestLocalizer))
  return suite

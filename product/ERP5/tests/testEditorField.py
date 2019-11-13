# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006, 2009 Nexedi SA and Contributors.
# All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
#          Jean-Paul Smets <jp@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest

from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DocumentTemplate.DT_Util import html_quote

class TestEditorField(ERP5TypeTestCase, ZopeTestCase.Functional):
  """
    The goal of this test is to cover the different application cases
    of EditorField in ERP5 CRM, ERP5 Web, etc. and make sure that
    proxy fields are designed in a consistent way. This test has
    been created after some changes in erp5_core had impact
    on other business templates.

    Please refer to the ERP5 developer howto for more explanation
      http://www.erp5.org/HowToDisplayOrEditHTML
  """
  manager_username = 'zope'
  manager_password = 'zope'

  def getTitle(self):
    return "EditorField"

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager', ], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_web',
            'erp5_ingestion',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_crm',
            'erp5_forge',
            )

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()
    self.web_page_module = self.portal.web_page_module
    self.web_site_module = self.portal.web_site_module
    self.event_module = self.portal.event_module
    portal.Localizer.manage_changeDefaultLang(language = 'en')
    self.portal_id = self.portal.getId()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.web_page_module)
    self.clearModule(self.portal.person_module)

  def getDefaultSitePreference(self):
    return self.getPreferenceTool().default_site_preference

  def _testPreferredDocumentEditor(self, event, preferred_editor, editor, form_id, field_id):
    """
      Common code to test if current document (event)
      is using appropriate editor (editor) as defined
      in preferences
    """
    site_preference = self.getDefaultSitePreference()
    site_preference.setPreferredTextEditor(preferred_editor)
    if site_preference.getPreferenceState() != 'global':
      site_preference.enable()
    # commit transaction, are preferences are in transaction cache
    self.commit()

    # Make sure preferred editor was set on preference
    self.assertEqual(self.getDefaultSitePreference().getPreferredTextEditor(), preferred_editor)
    # then on portal preferences
    self.assertEqual(self.getPreferenceTool().getPreferredTextEditor(), preferred_editor)
    # Make sure editor field preference is also set
    form = getattr(event, form_id)
    field = getattr(form, field_id)
    self.assertEqual(dict(field.get_value('renderjs_extra'))['editor'], editor)

  def _isFCKEditor(self, html_text, field_id, text_content):
    """
      Tries to find in the HTML page string portions
      which show that text content is displayed using
      FCKEditor for the given field_id

      html_text -- the HTML string to analyze

      field_id -- the id of the field in the form

      text_content -- the embedded text content
    """
    html_text = html_text.encode('utf-8')
    match_string1 = 'data-gadget-editable="field_%s"' % field_id
    match_string2 = 'data-gadget-value="%s"' % html_quote(text_content)
    if html_text.find(match_string1) == -1:
      print html_text
      print match_string1
      return False
    if html_text.find(match_string2) == -1:
      print html_text
      print match_string2
      return False
    return True

  def _isTextAreaEditor(self, html_text, field_id, text_content):
    """
      Tries to find in the HTML page string portions
      which show that text content is displayed using
      TextArea for the given field_id

      html_text -- the HTML string to analyze

      field_id -- the id of the field in the form

      text_content -- the embedded text content
    """
    html_text = html_text.encode('utf-8')
    match_string1 = 'data-gadget-editable="field_%s"' % field_id
    match_string2 = 'data-gadget-value="%s"' % html_quote(text_content)
    if html_text.find(match_string1) == -1:
      print html_text
      print match_string1
      import pdb; pdb.set_trace()
      return False
    if html_text.find(match_string2) == -1:
      print html_text
      print match_string2
      import pdb; pdb.set_trace()
      return False
    return True

  def _isReadOnlyEditor(self, html_text, document, text_content):
    """
      Tries to find in the HTML page string portions
      which show that text content is displayed in read
      only mode with 'page' CSS class in a <div>

      html_text -- the HTML string to analyze

      document -- the document which content is displayed in
                  read only mode
    """
    html_text = html_text.encode('utf-8')
    match_string1 = "data-gadget-editable="
    match_string2 = 'data-gadget-value="%s"' % html_quote(text_content)
    if html_text.find(match_string1) != -1:
      print html_text
      print match_string1
      return False
    if html_text.find(match_string2) == -1:
      print html_text
      print match_string2
      return False
    return True

  def test_EditSimpleEmailEventFCKEditorHTML(self):
    """
      Create an event, make sure portal preferences are set as
      FCKEditor and make sure FCKEditor is displayed in the
      default view of a CRM event

      In this case we use HTML content for the test.
    """
    # Create an event
    event = self.event_module.newContent(portal_type='Note')
    text_content = """<p>Hé Hé\nHo Ho\nHi Hi</p>"""
    event.setContentType('text/html')
    event.setTextContent(text_content)

    # Set FCKEditor as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(event, 'fck_editor', 'fck_editor', 'Event_view', 'my_text_content')

    # Make sure generated HTML is based on FCKEditor
    html_text = event.view()
    self.assertTrue(self._isFCKEditor(html_text, 'my_text_content', text_content))

    # Set a fake file on Event and make sure no more editor is displayed
    # and that instead a div with page CSS style appears with stripped HTML
    event.setData('fake')
    self.assertFalse(event.Event_view.my_text_content.get_value('editable'))
    html_text = event.view()
    self.assertTrue(self._isReadOnlyEditor(html_text, event, 'fake'))

  def test_EditSimpleEmailEventFCKEditorText(self):
    """
      Create an event, make sure portal preferences are set as
      FCKEditor and make sure FCKEditor is displayed in the
      default view of a CRM event

      In this case we use Text content for the test.
    """
    # Create an event
    event = self.event_module.newContent(portal_type='Note')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    event.setContentType('text/plain')
    event.setTextContent(text_content)

    # Set FCKEditor as preferred editor and make sure text_area is used since
    # we are not doing HTML
    self._testPreferredDocumentEditor(event, 'fck_editor', 'text_area', 'Event_view', 'my_text_content')

    # Make sure generated HTML is based on TextArea since this is not HTML
    html_text = event.view()
    self.assertTrue(self._isTextAreaEditor(html_text, 'my_text_content', text_content))

    # Set a fake file on Event and make sure no more editor is displayed
    # and that instead a div with page CSS style appears with stripped HTML
    event.setData('fake')
    self.assertFalse(event.Event_view.my_text_content.get_value('editable'))
    html_text = event.view()
    self.assertTrue(self._isReadOnlyEditor(html_text, event, 'fake'))

  def test_EditSimpleEmailEventTextAreaHTML(self):
    """
      Create an event, make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the
      default view of a CRM event

      In this case we use HTML content for the test.
    """
    # Create an event
    event = self.event_module.newContent(portal_type='Note')
    text_content = """<p>Hé Hé\nHo Ho\nHi Hi</p>"""
    event.setContentType('text/html')
    event.setTextContent(text_content)

    # Set TextArea as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(event, 'text_area', 'text_area', 'Event_view', 'my_text_content')

    # Make sure generated HTML is based on TextArea
    html_text = event.view()
    self.assertTrue(self._isTextAreaEditor(html_text, 'my_text_content', text_content))

    # Set a fake file on Event and make sure no more editor is displayed
    # and that instead a div with page CSS style appears with stripped HTML
    event.setData('fake')
    self.assertFalse(event.Event_view.my_text_content.get_value('editable'))
    html_text = event.view()
    self.assertTrue(self._isReadOnlyEditor(html_text, event, 'fake'))

  def test_EditSimpleEmailEventTextAreaText(self):
    """
      Create an event, make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the
      default view of a CRM event

      In this case we use Text content for the test.
    """
    # Create an event
    event = self.event_module.newContent(portal_type='Note')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    event.setContentType('text/plain')
    event.setTextContent(text_content)

    # Set TextArea as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(event, 'text_area', 'text_area', 'Event_view', 'my_text_content')

    # Make sure generated HTML is based on TextArea
    html_text = event.view()
    self.assertTrue(self._isTextAreaEditor(html_text, 'my_text_content', text_content))

    # Set a fake file on Event and make sure no more editor is displayed
    # and that instead a div with page CSS style appears with stripped HTML
    event.setData('fake')
    self.assertFalse(event.Event_view.my_text_content.get_value('editable'))
    html_text = event.view()
    self.assertTrue(self._isReadOnlyEditor(html_text, event, 'fake'))

  def test_EditWebPageFCKEditorHTML(self):
    """
      Create a web page. Make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the
      editor view of a Web Page.

      In this case we use HTML content for the test.
    """
    # Create a web page
    page = self.web_page_module.newContent(portal_type='Web Page')
    text_content = """<p>Hé Hé\nHo Ho\nHi Hi</p>"""
    page.setContentType('text/html')
    page.setTextContent(text_content)

    # Set FCKEditor as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(page, 'fck_editor', 'fck_editor', 'WebPage_viewEditor', 'my_text_content')

    # Make sure default view is read only
    html_text = page.WebPage_view()
    self.assertFalse(page.WebPage_view.my_text_content.get_value('editable'))
    self.assertTrue(self._isReadOnlyEditor(html_text, page, page.getTextContent()))

  def test_EditWebPageFCKEditorText(self):
    """
      Create a web page. Make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the
      editor view of a Web Page.

      In this case we use Text content for the test.
    """
    # Create a web page
    page = self.web_page_module.newContent(portal_type='Web Page')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    page.setContentType('text/plain')
    page.setTextContent(text_content)

    # Set FCKEditor as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(page, 'fck_editor', 'text_area', 'WebPage_viewEditor', 'my_text_content')

    # Make sure default view is read only
    html_text = page.WebPage_view()
    self.assertFalse(page.WebPage_view.my_text_content.get_value('editable'))
    self.assertTrue(self._isReadOnlyEditor(html_text, page, page.getTextContent()))

  def test_EditWebPageTextAreaHTML(self):
    """
      Create a web page. Make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the
      editor view of a Web Page.

      In this case we use HTML content for the test.
    """
    # Create a web page
    page = self.web_page_module.newContent(portal_type='Web Page')
    text_content = """<p>Hé Hé\nHo Ho\nHi Hi</p>"""
    page.setContentType('text/html')
    page.setTextContent(text_content)

    # Set TextArea as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(page, 'text_area', 'text_area', 'WebPage_viewEditor', 'my_text_content')

    # Make sure default view is read only
    html_text = page.WebPage_view()
    self.assertFalse(page.WebPage_view.my_text_content.get_value('editable'))
    self.assertTrue(self._isReadOnlyEditor(html_text, page, page.getTextContent()))

  def test_EditWebPageTextAreaText(self):
    """
      Create a web page. Make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the
      editor view of a Web Page.

      In this case we use Text content for the test.
    """
    # Create a web page
    page = self.web_page_module.newContent(portal_type='Web Page')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    page.setContentType('text/plain')
    page.setTextContent(text_content)

    # Set TextArea as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(page, 'text_area', 'text_area', 'WebPage_viewEditor', 'my_text_content')

    # Make sure default view is read only
    html_text = page.WebPage_view()
    self.assertFalse(page.WebPage_view.my_text_content.get_value('editable'))
    self.assertTrue(self._isReadOnlyEditor(html_text, page, page.getTextContent()))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestEditorField))
  return suite

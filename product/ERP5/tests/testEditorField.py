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

import re
import unittest

import transaction
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from Products.ERP5Type.tests.utils import createZODBPythonScript

class TestEditorField(ERP5TypeTestCase, ZopeTestCase.Functional):
  """
    The goal of this test is to cover the different application cases
    of EditorField in ERP5 CRM, ERP5 Web, etc. and make sure that 
    proxy fields are designed in a consistent way. This test has 
    been created after some changes in erp5_core had impact
    on other business templates.
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
    return ('erp5_base',
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
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.web_page_module)
    self.clearModule(self.portal.person_module)

  def getDefaultSitePreference(self):
    return self.getPreferenceTool().default_site_preference

  def _testPreferredDocumentEditor(self, event, editor, form_id, field_id):
    """
      Common code to test if current document (event)
      is using appropriate editor (editor) as defined 
      in preferences
    """
    self.getDefaultSitePreference().setPreferredTextEditor(editor)
    if self.getDefaultSitePreference().getPreferenceState() == 'global':
      self.getDefaultSitePreference()._clearCache()
    else:
      self.getDefaultSitePreference().enable()

    # Make sure preferred editor was set on preference
    self.assertEquals(self.getDefaultSitePreference().getPreferredTextEditor(), editor)
    # then on portal preferences
    self.assertEquals(self.getPreferenceTool().getPreferredTextEditor(), editor)
    # Make sure editor field preference is also set
    form = getattr(event, form_id)
    field = getattr(form, field_id)
    self.assertEquals(field.get_value('text_editor'), editor)

  def _isFCKEditor(self, html_text, field_id, text_content):
    """
      Tries to find in the HTML page string portions
      which show that text content is displayed using
      FCKEditor for the given field_id

      html_text -- the HTML string to analyze

      field_id -- the id of the field in the form

      text_content -- the embedded text content
    """
    match_string1 = "var oFCKeditor      = new FCKeditor('field_%s');" % field_id
    match_string2 = "oFCKeditor.Value    = '%s';" % ('\\n'.join(text_content.splitlines()))
    if html_text.find(match_string1) == -1:
      return False
    if html_text.find(match_string2) == -1:
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
    match_string = """name="field_%s" >%s</textarea>""" % (field_id, text_content)
    if html_text.find(match_string) == -1:
      return False
    return True

  def _isReadOnlyEditor(self, html_text, document):
    """
      Tries to find in the HTML page string portions
      which show that text content is displayed in read
      only mode with 'page' CSS class in a <div>

      html_text -- the HTML string to analyze

      document -- the document which content is displayed in 
                  read only mode
    """
    text_content = document.asStrippedHTML()
    # Some reformatting needed to simulate page templates
    text_content = '<br />\n'.join(text_content.split('<br />'))
    match_string1 = """<div class="input">%s</div>""" % text_content
    match_string2 = """"<div class="field page"""
    if html_text.find(match_string1) == -1:
      print html_text
      print match_string1
      return False
    if html_text.find(match_string2) == -1:
      print html_text
      print match_string2
      return False
    return True

  def test_EditSimpleEmailEventFCKEditor(self):
    """
      Create an event, make sure portal preferences are set as
      FCKEditor and make sure FCKEditor is displayed in the 
      default view of a CRM event
    """
    # Create an event
    event = self.event_module.newContent(portal_type='Note')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    event.setTextFormat('text/html')
    event.setTextContent(text_content)
   
    # Set FCKEditor as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(event, 'fck_editor', 'Event_view', 'my_text_content')

    # Make sure generated HTML is based on FCKEditor
    request=self.app.REQUEST
    request.set('URLPATH2', '/arbitrary/path') # A hack to make sure FCKEditor page template renders
    html_text = event.view()
    self.assertTrue(self._isFCKEditor(html_text, 'my_text_content', text_content))

    # Set a fake file on Event and make sure no more editor is displayed
    # and that instead a div with page CSS style appears with stripped HTML
    event.setData('fake')
    self.assertFalse(event.Event_view.my_text_content.get_value('editable'))
    html_text = event.view()
    self.assertTrue(self._isReadOnlyEditor(html_text, event))

  def test_EditSimpleEmailEventTextArea(self):
    """
      Create an event, make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the 
      default view of a CRM event
    """
    # Create an event
    event = self.event_module.newContent(portal_type='Note')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    event.setTextFormat('text/html')
    event.setTextContent(text_content)
   
    # Set FCKEditor as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(event, 'text_area', 'Event_view', 'my_text_content')

    # Make sure generated HTML is based on FCKEditor
    html_text = event.view()
    self.assertTrue(self._isTextAreaEditor(html_text, 'my_text_content', text_content))

    # Set a fake file on Event and make sure no more editor is displayed
    # and that instead a div with page CSS style appears with stripped HTML
    event.setData('fake')
    self.assertFalse(event.Event_view.my_text_content.get_value('editable'))
    html_text = event.view()
    self.assertTrue(self._isReadOnlyEditor(html_text, event))

  def test_EditWebPageFCKEditor(self):
    """
      Create a web page. Make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the 
      editor view of a Web Page.
    """
    # Create a web page
    page = self.web_page_module.newContent(portal_type='Web Page')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    page.setTextFormat('text/html')
    page.setTextContent(text_content)

    # Set FCKEditor as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(page, 'fck_editor', 'WebPage_viewEditor', 'my_text_content')

    # Make sure default view is read only
    html_text = page.WebPage_view()
    self.assertFalse(page.WebPage_view.text_content.get_value('editable'))
    self.assertTrue(self._isReadOnlyEditor(html_text, page))

  def test_EditWebPageTextArea(self):
    """
      Create a web page. Make sure portal preferences are set as
      TextArea and make sure TextArea is displayed in the 
      editor view of a Web Page.
    """
    # Create a web page
    page = self.web_page_module.newContent(portal_type='Web Page')
    text_content = """Hé Hé\nHo Ho\nHi Hi"""
    page.setTextFormat('text/html')
    page.setTextContent(text_content)

    # Set FCKEditor as preferred editor and make sure it is taken into account
    self._testPreferredDocumentEditor(page, 'text_area', 'WebPage_viewEditor', 'my_text_content')

    # Make sure default view is read only
    html_text = page.WebPage_view()
    self.assertFalse(page.WebPage_view.text_content.get_value('editable'))
    self.assertTrue(self._isReadOnlyEditor(html_text, page))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestEditorField))
  return suite

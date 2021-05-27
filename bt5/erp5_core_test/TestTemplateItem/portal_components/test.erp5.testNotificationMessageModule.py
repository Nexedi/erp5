# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Romain Courteaud <romain@nexedi.com>
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

import textwrap
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript


class TestNotificationMessageModule(ERP5TypeTestCase):
  """
  Test notification message module
  """
  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def afterSetUp(self):
    self.portal.acl_users._doAddUser('erp5user', self.newPassword(), ['Auditor', 'Author'], [])
    self.portal.acl_users._doAddUser('manager', self.newPassword(), ['Manager'], [])
    self.portal.email_from_address = 'site@example.invalid'
    self.loginByUserName('erp5user')

  def beforeTearDown(self):
    self.abort()
    # clear modules if necessary
    module_list = (self.portal.notification_message_module,)
    for module in module_list:
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def test_notification_tool_getDocumentValue(self):
    module = self.portal.notification_message_module
    tool = self.portal.portal_notifications
    self.loginByUserName('manager')
    #Test Document A in english
    n_m_en = module.newContent(portal_type='Notification Message',
                               reference='A',
                               language='en',
                               version='01')
    n_m_en.validate()
    self.tic()
    result = tool.getDocumentValue(reference='A')
    self.assertEqual(result.getRelativeUrl(), n_m_en.getRelativeUrl())
    result = tool.getDocumentValue(reference='A', language='fr')
    self.assertEqual(result.getRelativeUrl(), n_m_en.getRelativeUrl())
    #Same Document A in French
    n_m_fr = module.newContent(portal_type='Notification Message',
                               reference='A',
                               language='fr',
                               version='01')
    n_m_fr.validate()
    self.tic()
    result = tool.getDocumentValue(reference='A')
    self.assertEqual(result.getRelativeUrl(), n_m_en.getRelativeUrl())
    result = tool.getDocumentValue(reference='A', language='fr')
    self.assertEqual(result.getRelativeUrl(), n_m_fr.getRelativeUrl())
    #Duplicate Document A French with upgraded version
    n_m_fr_02 = module.newContent(portal_type='Notification Message',
                                  reference='A',
                                  language='fr',
                                  version='02')
    n_m_fr_02.validate()
    self.tic()
    result = tool.getDocumentValue(reference='A')
    self.assertEqual(result.getRelativeUrl(), n_m_en.getRelativeUrl())
    result = tool.getDocumentValue(reference='A', language='fr')
    self.assertEqual(result.getRelativeUrl(), n_m_fr_02.getRelativeUrl())

  def test_substitution_content(self):
    """Tests that content and subject have string.Template based substitutions
    """
    module = self.portal.notification_message_module
    createZODBPythonScript(self.portal,
                           'NotificationMessage_getDummySubstitionMapping',
                           '**kw',
                           '''return dict(a="b")''')
    doc = module.newContent(portal_type='Notification Message',
                            title='Test ${a}',
                            content_type='text/plain',
                            text_content='substitution text: ${a}',
                            text_content_substitution_mapping_method_id=
                            'NotificationMessage_getDummySubstitionMapping')

    mime, text = doc.convert('txt')
    self.assertEqual('text/plain', mime)
    self.assertEqual('substitution text: b', text.rstrip())

    self.assertEqual('Test b', doc.asSubjectText())

  def test_substitution_content_parameters(self):
    """Tests that we can pass parameters to convert to the substitution method,
    by using substitution_method_parameter_dict """
    module = self.portal.notification_message_module
    createZODBPythonScript(self.portal,
                           'NotificationMessage_getDummySubstitionMapping',
                           '**kw',
                           '''return kw''')
    doc = module.newContent(portal_type='Notification Message',
                            title='Test ${a}',
                            text_content='substitution text: ${a}',
                            content_type='text/plain',
                            text_content_substitution_mapping_method_id=
                            'NotificationMessage_getDummySubstitionMapping')

    _, text = doc.convert('txt',
                             substitution_method_parameter_dict=dict(a='b'))
    self.assertEqual('substitution text: b', text.rstrip())

  def test_substitution_content_and_convert(self):
    """Tests that substitution also works with different target format.
    """
    module = self.portal.notification_message_module
    createZODBPythonScript(self.portal,
                           'NotificationMessage_getDummySubstitionMapping',
                           '**kw',
                           '''return dict(a="b")''')
    doc = module.newContent(portal_type='Notification Message',
                            content_type='text/html',
                            text_content='substitution text: <em>${a}</em>',
                            text_content_substitution_mapping_method_id=
                            'NotificationMessage_getDummySubstitionMapping')

    _, text = doc.convert('txt')
    self.assertEqual('substitution text: b', text.rstrip())

  def test_safe_substitution_content(self):
    """Tests that 'safe' substitution is performed, unless safe_substitute is
    explicitly passed to False.
    """
    module = self.portal.notification_message_module
    createZODBPythonScript(self.portal,
                           'NotificationMessage_getDummySubstitionMapping',
                           '**kw',
                           '''return dict(a="b")''')
    doc = module.newContent(portal_type='Notification Message',
                            title='${b}',
                            content_type='text/plain',
                            text_content='substitution text: ${b}',
                            text_content_substitution_mapping_method_id=
                            'NotificationMessage_getDummySubstitionMapping')

    _, text = doc.convert('txt')
    self.assertEqual('substitution text: ${b}', text.rstrip())
    self.assertEqual('${b}', doc.asSubjectText())

    self.assertRaises(KeyError, doc.convert, 'txt', safe_substitute=False)
    self.assertRaises(KeyError, doc.convert, 'html', safe_substitute=False)
    self.assertRaises(KeyError, doc.asSubjectText, safe_substitute=False)

  def test_substitution_lazy_dict(self):
    """Substitution script just needs to return an object implementing
    __getitem__ protocol.
    """
    module = self.portal.notification_message_module
    createZODBPythonScript(
        self.portal, 'NotificationMessage_getDummySubstitionMapping', '**kw',
        textwrap.dedent(
            '''\
            class DynamicDict:
              def __getitem__(self, key):
                return "(dynamic key: %s)" % key
            return DynamicDict()
            '''))
    doc = module.newContent(
        portal_type='Notification Message',
        content_type='text/plain',
        text_content='substitution text: ${a}',
        text_content_substitution_mapping_method_id='NotificationMessage_getDummySubstitionMapping'
    )

    mime, text = doc.convert('txt')
    self.assertEqual('text/plain', mime)
    self.assertEqual('substitution text: (dynamic key: a)', text)

# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

import six
import sys
import traceback

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

"""Test for ERP5 callables, is ERP5 documents to be used in portal_skins
or portal_workflow
"""


class TestERP5PythonScript(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return 'erp5_core',

  def afterSetUp(self):
    folder = self.portal.portal_skins.custom
    folder.manage_addProduct['ERP5'].addPythonScriptThroughZMI(
      id=self.id()
    )
    self.script = folder.get(self.id())
    self.commit()

  def beforeTearDown(self):
    self.abort()
    self.portal.portal_skins.custom.manage_delObjects([self.id()])
    self.tic()

  def test_default_params(self):
    self.assertEqual(self.script.getParameterSignature(), '')

  def test_set_params(self):
    self.script.setParameterSignature('foo')
    self.assertEqual(self.script.getParameterSignature(), 'foo')
    self.script.setParameterSignature('')
    self.assertEqual(self.script.getParameterSignature(), '')
    self.script.setParameterSignature('bar')
    self.assertEqual(self.script.getParameterSignature(), 'bar')
    self.script.setParameterSignature(None) # Base_edit calls with None
    self.assertEqual(self.script.getParameterSignature(), '')

  def test_manage_addPythonScriptThroughZMI(self):
    resp = self.publish(
      '/{}/portal_skins/manage_addProduct/ERP5/addPythonScriptThroughZMIForm'.format(self.portal.getId()),
      basic='%s:%s' % (self.manager_username, self.manager_password),
      handle_errors=False,
    )
    self.assertIn(b'ERP5 Python Scripts', resp.getBody())
    self.assertIn(b'addPythonScriptThroughZMI', resp.getBody())

  def test_call(self):
    self.script.setBody('return "Hello"')
    self.assertEqual(self.script(), "Hello")

    self.script.setParameterSignature('who')
    self.script.setBody('return "Hello " + who')
    self.assertEqual(self.script("world"), "Hello world")

    if six.PY2:
      filename = 'ERP5 Python Script'
    else:
      filename = 'ERP5 Python Script:%s' % self.script.getPath()

    try:
      self.script(123)
    except TypeError:
      _, _, tb = sys.exc_info()
      # python script code is visible in traceback
      self.assertEqual(
        traceback.format_tb(tb)[-1],
        '  File "%s", line 1, in %s\n'
        '    return "Hello " + who\n' % (filename, self.id())
      )
    else:
      self.fail('Exception not raised')


class TestERP5WorkflowScript(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return 'erp5_core',

  def afterSetUp(self):
    wf = self.portal.portal_workflow.newContent(
      portal_type='Workflow',
      id=self.id()
    )
    self.script = wf.newContent(
      portal_type='Workflow Script',
      reference='test_script',
    )
    self.commit()

  def beforeTearDown(self):
    self.abort()
    self.portal.portal_workflow.manage_delObjects([self.id()])
    self.tic()

  def test_default_params(self):
    self.assertEqual(self.script.getParameterSignature(), 'state_change')

  def test_call(self):
    self.script.setBody('return "Hello " + state_change')
    self.assertEqual(self.script("world"), "Hello world")

    if six.PY2:
      filename = 'ERP5 Workflow Script'
    else:
      filename = 'ERP5 Workflow Script:%s' % self.script.getPath()

    try:
      self.script(123)
    except TypeError:
      _, _, tb = sys.exc_info()
      # python script code is visible in traceback
      self.assertEqual(
        traceback.format_tb(tb)[-1],
        ('  File "%s", line 1, in script_test_script\n'
        '    return "Hello " + state_change\n') % filename
      )
    else:
      self.fail('Exception not raised')

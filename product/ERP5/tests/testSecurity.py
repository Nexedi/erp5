# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import six
import sys
import os
import unittest
from types import MethodType
from Acquisition import aq_base
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityInfo import ACCESS_NONE, ACCESS_PRIVATE
if six.PY3:
  from ZPublisher import zpublish_mark


# You can invoke security tests in your favourite collection of business templates
# by using TestSecurityMixin like the following :
#
# from Products.ERP5.tests.testERP5Security import TestSecurityMixin
# class TestMySecurity(TestSecurityMixin):
#   def getBusinessTemplateList(self):
#     return (...)

class TestSecurityMixin:

  def _prepareDocumentList(self):
    if getattr(self, '_prepareDocumentList_finished', None):
      return
    portal_types = self.portal.portal_types
    portal_type_dict = {}
    def createSubObject(obj):
      portal_type = obj.getPortalType()
      type_info = getattr(portal_types, portal_type, None)
      if type_info is None:
        return
      for i in type_info.getTypeAllowedContentTypeList():
        if i in portal_type_dict:
          continue
        portal_type_dict[i] = True
        try:
          o = obj.newContent(portal_type=i, created_by_builder=True)
          createSubObject(o)
        except:
          pass
    for i in self.portal.objectValues():
      if getattr(aq_base(i), 'getPortalType', None) is not None:
        createSubObject(i)
    self._prepareDocumentList_finished = True

  def _isMethodPublishable(self, method):
    has_docstring = method.__doc__
    if sys.version_info < (3, 13):
      # Since py3.13 leading spaces are stripped from docstring by the
      # interpreter and end up being not publishable anymore
      has_docstring = has_docstring and not method.__doc__.lstrip()
    if six.PY3:
      return zpublish_mark(method, has_docstring)
    else:
      return has_docstring

  def _hasImplicitSecurity(self, obj, method_id, method):
    return not (hasattr(method, '__roles__') or
          getattr(obj, '%s__roles__' % method_id,
                  ACCESS_NONE) not in (ACCESS_PRIVATE, ACCESS_NONE))

  def _checkObjectAllMethodProtection(self, obj):
    error_dict = {}
    allowed_method_id_list = ['om_icons',]
    for method_id in dir(obj):
      if method_id.startswith('_') or method_id in allowed_method_id_list or not callable(getattr(obj, method_id, None)):
        continue
      method = getattr(obj, method_id)
      if isinstance(method, MethodType) and \
        getattr(method, '__name__', None) is not None and \
        getattr(method, '__module__', None) is not None and \
        self._isMethodPublishable(method) and self._hasImplicitSecurity(obj, method_id, method):
        if method.__module__ == 'Products.ERP5Type.Accessor.WorkflowState' and method.__code__.co_name == 'serialize':
          continue
        func_code = method.__code__
        if not hasattr(func_code, 'co_filename'): # ERP5 Accessor
          func_code = method.__func__.__class__.__init__.__code__
        error_dict[(func_code.co_filename, func_code.co_firstlineno)] = method_id
    return error_dict

  def test_method_protection(self):
    """
    This test will list all implicitly Public methods in any objects in ZODB.
    i.e. those who have a docstring but have no security declaration.
    """
    self._prepareDocumentList()
    app = self.portal.aq_parent
    meta_type_set = set([None])
    error_dict = {}
    for _, obj in app.ZopeFind(app, search_sub=1):
      meta_type = getattr(obj, 'meta_type', None)
      if meta_type in meta_type_set:
        continue
      meta_type_set.add(meta_type)
      error_dict.update(self._checkObjectAllMethodProtection(obj))

    error_list = []
    for (filename, lineno), method_id in sorted(error_dict.items()):
      # ignore security problems with non ERP5 documents, unless running in debug mode.
      if (# ignore ZODB Components tested by CodingStyleTest for each bt5
          ((six.PY2 and not filename.startswith('<portal_components')) or
           (six.PY3 and not filename.startswith('erp5://'))) and
          (os.environ.get('erp5_debug_mode') or '/erp5/' in filename)):
        error_list.append('%s:%s %s' % (filename, lineno, method_id))
      else:
        print(('Ignoring missing security definition or missing docstring on public methods'
               'for %s in %s:%s ' % (method_id, filename, lineno)))
    if error_list:
      message = ('\nThe following %s methods have a docstring without security '
                 'assertions or are public methods with an empty docstring not '
                 'publishable anymore with Python >= 3.13.\n\t%s' \
                 % (len(error_list), '\n\t'.join(error_list)))
      self.fail(message)

  def _getTestedWorkflowValueList(self):
    return self.portal.portal_workflow.objectValues()

  def test_workflow_transition_protection(self):
    """
    This test will list all workflow transitions and check the existence of guard.
    """
    error_list = []
    for wf in self._getTestedWorkflowValueList():
      if wf.__class__.__name__ in ['InteractionWorkflowDefinition', 'Interaction Workflow']:
        continue
      for transition in wf.getTransitionValueList():
        if transition.getTriggerType() == 0:
          # Automatic transition without guard is safe
          continue
        if not transition.isGuarded():
          error_list.append('%s/transitions/%s' % (wf.getId(), transition.getId()))
    if error_list:
      message = '\nThe following %s workflow transitions are not guarded.\n\t%s' \
                    % (len(error_list), '\n\t'.join(sorted(error_list)))
      self.fail(message)

class TestSecurity(ERP5TypeTestCase, TestSecurityMixin):

  def getTitle(self):
    return "Security Test"

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestSecurity))
  return suite

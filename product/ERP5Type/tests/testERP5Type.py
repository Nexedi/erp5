# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
"""
WARNING: This file has been kept for aq_reset/aq_dynamic parts only (all
other Tests are in erp5_core_test:testERP5Type) which is deprecated in favor
of Portal Type as Classes and ZODB Components
"""

import pickle
import unittest
import warnings
import six
from Acquisition import aq_base
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.ZopeGuards import guarded_import
from Products.ERP5Type.tests.utils import LogInterceptor, createZODBPythonScript

class TestERP5Type(ERP5TypeTestCase, LogInterceptor):
    """
    Tests ERP5TypeInformation and per portal type generated accessors.
    """
    # Some helper methods
    def getTitle(self):
      return "ERP5Type"

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return ('erp5_base',
              # delivery_causality_workflow
              'erp5_simulation')

    def afterSetUp(self):
      self.login()
      # all those tests does strange things with Person type, so we won't
      # filter content types to add inside Person.
      person_type_object = self.getTypesTool().getTypeInfo('Person')
      person_type_object.filter_content_types = 0
      self.commit()

      # save workflow chain for Person type
      self.person_workflow_list = person_type_object.getTypeWorkflowList()

    def beforeTearDown(self):
      self.abort()
      # THIS IS UGLY, WE MUST REMOVE AS SOON AS POSSIBLE, NOT COMPATIBLE
      # WITH LIVE TEST
      for module in [ self.getPersonModule(),
                      self.getOrganisationModule(),
                      self.getCategoryTool().region ]:
        module.manage_delObjects(list(module.objectIds()))

      person_type_object = self.getTypesTool().getTypeInfo('Person')
      # set Person.acquire_local_roles back.
      if getattr(self, 'person_acquire_local_roles', None) is not None:
        person_type_object.acquire_local_roles = self.person_acquire_local_roles

      # restore workflows for other tests
      person_type_object.setTypeWorkflowList(self.person_workflow_list)

      super(TestERP5Type, self).beforeTearDown()

    # _aq_reset should be called implicitly when the system configuration
    # changes:
    def test_aq_reset_on_portal_types_properties_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      ti = self.getTypesTool()['Person']
      base_category_list = ti.getTypeBaseCategoryList()
      # this test is poorly isolated, and the _19*_ add destination
      # to the base categories
      if 'destination' not in base_category_list:

        self.assertFalse(hasattr(doc, 'getDestination'))
        ti.edit(type_base_category_list=
          base_category_list + ['destination'])

        self.commit()
        self.assertTrue(hasattr(doc, 'getDestination'))
      else:
        self.assertTrue(hasattr(doc, 'getDestination'))
        base_category_list.remove('destination')
        ti.edit(type_base_category_list=base_category_list)

        self.commit()
        self.assertFalse(hasattr(doc, 'getDestination'))

    def test_aq_reset_on_type_workflow_list_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      self.assertFalse(hasattr(doc, 'getCausalityState'))
      # chain the portal type with a workflow that has 'causality_state' as
      # state variable name, this should regenerate the getCausalityState
      # accessor. This test might have to be updated whenever
      # delivery_causality_workflow changes.
      person_type_object = self.getTypesTool().getTypeInfo('Person')
      person_type_object.setTypeWorkflowList(['delivery_causality_workflow'])

      self.commit()
      self.assertTrue(hasattr(doc, 'getCausalityState'))

    def test_aq_reset_on_workflow_method_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      person_type_object = self.portal.portal_types._getOb('Person')
      person_type_object.setTypeWorkflowList(person_type_object.getTypeWorkflowList() + ['delivery_causality_workflow'])

      self.commit()
      self.assertTrue(hasattr(doc, 'diverge'))

      wf = self.portal.portal_workflow.delivery_causality_workflow
      from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
      dummy_transition = wf.newContent(portal_type='Workflow Transition',
                                       reference='dummy_workflow_method',
                                       trigger_type=TRIGGER_WORKFLOW_METHOD)
      self.commit()
      self.assertTrue(hasattr(doc, 'dummyWorkflowMethod'))

      wf.deleteContent(dummy_transition.getId())
      self.commit()
      self.assertFalse(hasattr(doc, 'dummyWorkflowMethod'))

    def test_aq_reset_on_workflow_state_variable_change(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      person_type_object = self.portal.portal_types._getOb('Person')
      person_type_object.setTypeWorkflowList(person_type_object.getTypeWorkflowList() + ['delivery_causality_workflow'])

      self.commit()
      self.assertTrue(hasattr(doc, 'getCausalityState'))
      wf = self.portal.portal_workflow._getOb('delivery_causality_workflow')
      if wf.getPortalType() == 'Workflow':
        wf._edit(state_variable='dummy_state')
      else:
        wf.setStateVariable('dummy_state')

      self.commit()
      self.assertTrue(hasattr(doc, 'getDummyState'))

    # ... other cases should be added here




    # Tests for _aq_dynamic patch. Probably not in the right place.
    def test_aq_dynamic(self):
      doc = self.portal.person_module.newContent(portal_type='Person')
      from Acquisition import Explicit

      class Ok(Explicit):
        aq_dynamic_calls = []
        def _aq_dynamic(self, name):
          self.aq_dynamic_calls.append(name)
          return 'returned_attr'

      ok = Ok().__of__(doc)
      self.assertEqual('returned_attr', getattr(ok, 'attr'))
      self.assertEqual(ok.aq_dynamic_calls, ['attr'])

    def test_aq_dynamic_exception(self):
      # if an exception is raised in _aq_dynamic, it should not be hidden
      doc = self.portal.person_module.newContent(portal_type='Person')
      from Acquisition import Explicit

      class NotOk(Explicit):
        def _aq_dynamic(self, name):
          raise ValueError()

      not_ok = NotOk().__of__(doc)
      self.assertRaises(ValueError, getattr, not_ok, 'attr')
      if six.PY3:
        self.assertRaises(ValueError, hasattr, not_ok, 'attr')
      else:
        self.assertFalse(hasattr(not_ok, 'attr'))

    def test_renameObjectsReindexSubobjects(self):
      """Test that renaming an object with subobjects causes them to be
         reindexed (their path must be updated).
      """
      folder = self.getOrganisationModule()
      sql_catalog = self.portal.portal_catalog.getSQLCatalog()
      initial_id = 'foo'
      final_id = 'bar'
      subdocument_id = 'sub'
      object = folder.newContent(portal_type='Organisation', id=initial_id)
      object.newContent(id=subdocument_id)
      self.tic()
      folder = self.getOrganisationModule()
      folder.manage_renameObjects([initial_id], [final_id])
      self.tic()
      folder = self.getOrganisationModule()
      subdocument = folder[final_id][subdocument_id]
      subdocument_record = sql_catalog.getRecordForUid(subdocument.uid)
      self.assertEqual(subdocument.getPath(), subdocument_record.path)

    def test_products_document_legacy(self):
      """check document classes defined in Products/*/Document/*.py
      """
      # note: this assertion below checks Alarm is really a legacy document class.
      # if one day Alarm is moved to component, then this test needs to be updated
      # with another module that lives on the file system.
      import Products.ERP5.Document.Alarm
      self.assertIn('product/ERP5/Document/Alarm.py', Products.ERP5.Document.Alarm.__file__)

      # document classes are also dynamically loaded in Products.ERP5Type.Document module
      from Products.ERP5Type.Document.Alarm import Alarm as Alarm_from_ERP5Type  # pylint:disable=import-error,no-name-in-module
      self.assertIs(Alarm_from_ERP5Type, Products.ERP5.Document.Alarm.Alarm)

      # a new temp constructor is created
      from Products.ERP5Type.Document import newTempAlarm  # pylint:disable=import-error,no-name-in-module
      self.assertIn(Alarm_from_ERP5Type, newTempAlarm(self.portal, '').__class__.mro())

      # temp constructors are deprecated, they issue a warning when called
      import mock
      with mock.patch('Products.ERP5Type.Utils.warnings.warn') as warn:
          newTempAlarm(self.portal, '')
      warn.assert_called_with(
          'newTemp*(self, ID) will be removed, use self.newContent(temp_object=True, id=ID, portal_type=...)',
          DeprecationWarning, 2)

    def test_newTempBase(self):
      # Products.ERP5Type.Document.newTempBase is another (not recommended) way
      # of creating temp objects
      import Products.ERP5Type.Document
      o = Products.ERP5Type.Document.newTempBase(self.portal, 'id')
      self.assertEqual(o.getId(), 'id')
      self.assertEqual(o.getPortalType(), 'Base Object')
      self.assertTrue(o.isTempObject())
      self.assertTrue(guarded_import("Products.ERP5Type.Document", fromlist=["newTempBase"]))

    def _test_temp_object_persistent(self, temp_object):
      # Temp objects can not be stored in ZODB
      self.assertTrue(temp_object.isTempObject())

      # they can be pickled
      self.assertTrue(pickle.dumps(aq_base(temp_object)))
      # they can be unpickled
      import ZODB.broken
      self.assertNotIsInstance(
          pickle.loads(pickle.dumps(aq_base(temp_object))),
          ZODB.broken.Broken,
      )

      # but they can not be saved in ZODB accidentally
      self.portal.person_module.oops = temp_object
      self.assertRaisesRegex(Exception, "Temporary objects can't be pickled", self.commit)
      self.abort()

    def test_temp_object_persistent(self):
      temp_object = self.portal.person_module.newContent(portal_type='Person', temp_object=True)
      self._test_temp_object_persistent(temp_object)

    def test_newTempBase_persistent(self):
      import Products.ERP5Type.Document
      temp_object = Products.ERP5Type.Document.newTempBase(self.portal, 'id')
      self._test_temp_object_persistent(temp_object)

    def test_objectValues(self):
      person = self.portal.person_module.newContent(portal_type='Person')
      createZODBPythonScript(person, 'test_script', '', '')
      script = person['test_script']
      self.assertIn(script, person.objectValues())
      self.assertNotIn(script, person.objectValues(portal_type='Person'))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Type))
  return suite

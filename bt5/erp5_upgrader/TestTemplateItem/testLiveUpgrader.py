##############################################################################
#
# Copyright (c) 2002-2011 Nexedi SA and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
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


from Products.ERP5Type.tests.ERP5TypeLiveTestCase import ERP5TypeLiveTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
import transaction

class TestLiveUpgrader(ERP5TypeLiveTestCase):
  """
    Configurator Mixin Class
  """
  def afterSetUp(self):
    self.login(user_name='test_configurator_user')
    self.upgrade_object_test_id = "upgrade_object_test"
    self.erp5_site_global_id = getattr(self.portal, 'erp5_site_global_id', None)
    self.beforeTearDown()
    self.portal.portal_activities.unsubscribe()

  def beforeTearDown(self):
    """ Restore original state """
    self.portal.portal_activities.subscribe()
    custom = self.portal.portal_skins.custom

    for script_id in ['ERP5Site_getUpgraderSignature', 'ERP5Site_getUpgraderSignature']: 
      if script_id in custom.objectIds():
        custom.manage_delObjects([script_id])

    if self.upgrade_object_test_id in self.portal.portal_categories.objectIds():
       self.portal.portal_categories.manage_delObjects([self.upgrade_object_test_id])

    if self.upgrade_object_test_id in self.portal.portal_gadgets.objectIds():
       self.portal.portal_gadgets.manage_delObjects([self.upgrade_object_test_id])

    self.portal._updateProperty('erp5_site_global_id', self.erp5_site_global_id)
    
    property_sheet_list = self.portal.portal_types.Person.getTypePropertySheetList()
    new_property_sheet_list = [ i for i in property_sheet_list if i !="Account" ]
    self.portal.portal_types.Person.setTypePropertySheetList(new_property_sheet_list)
    self.assertFalse("Account" in self.portal.portal_types.Person.getTypePropertySheetList())

    self.stepTic()
    ERP5TypeLiveTestCase.beforeTearDown(self)

  def test_UpgradeSignatureAPI(self):
    """
      test If the script that defines the signature follow
      the API defined here. This will prevent mistakes
      or change API Definition.
    """
    signature_key_list = ('alarm_dict',
                          'release',
                          'product',
                          'bt5_base_url_list',
                          'workflow_chain_dict',
                          'required_bt5_id_list',
                          'upgradable_bt5_id_list',
                          'update_catalog_bt5_id_list',
                          'before_triggered_bt5_id_dict',
                          'after_triggered_bt5_id_dict',
                          'reinstalable_bt5_id_list',
                          'keep_original_dict',
                          'object_action_dict',
                          'integrity_verification_script_id_list',
                          'catalog_filter_dict',
                          'update_role_portal_type_list',
                          'portal_type_property_sheet_list',
                          'erp5_site_property_dict',
                          'upgrade_object_class_list',
                          'recatalog',
                          'alarm_tool_configuration_list'
    )
    signature = self.portal.ERP5Site_getUpgraderSignature()
    self.assertEquals(sorted(signature_key_list), sorted(signature.keys()))

  def test_StandardUpgraderSignature(self):
    """ Test default behaviours provided by default ERP5Site_getUpgraderSignature
    """
    signature = self.portal.ERP5Site_getUpgraderSignature()
    # By default we do not recatalog the instance
    self.assertEquals(signature['recatalog'], False)

    # By default we do not upgrade manually the workflow
    self.assertEquals(signature['workflow_chain_dict'], None)

    # By Default we do not upgrade Catalog Filters
    self.assertEquals(signature['catalog_filter_dict'], None)

    # By Default there is no extra properties to set.
    self.assertEquals(signature['erp5_site_property_dict'], {})

    # Do not enable alarms by default
    self.assertEquals(signature['alarm_tool_configuration_list'], ())

    # By default we upgrade software, products, bt5 and so on.
    self.assertTrue(signature['alarm_dict']["system_upgrader"])
    self.assertTrue(signature['alarm_dict']["product_upgrader"])
    self.assertTrue(signature['alarm_dict']["bt5_upgrader"])
    self.assertTrue(signature['alarm_dict']["finalize_upgrader"])

    # By default there is nothing to fix on skin Selection.
    # (rafael) Is it really necessary?
    self.assertFalse(self.portal.ERP5Site_setupUpgraderSkinSelection())

  def testUpgradeObjectWorkflowState(self):
    """
      Create a test to ERP5Site_upgradeObjectList which aims to update
      Objects which are in bad workflow state or have a bad property.
      
      Signature API:

        { BUSINESS_TEMPLATE_TITLE : (
	                 (OBJECT_PATH,
	                  SCRIPT TO COLLECT INFORMATION,
                          RETURN EXPECTED THAT INDICATES THE OBJECT IS BROKEN, 
			  SCRIPT USED TO FIX ),
	                 ),
        }
    """
    signature_code = {'erp5_core':( ('portal_categories/%s' % self.upgrade_object_test_id,
                                     'getValidationState', 
                                     'embedded', 
                                     'publish'),)}
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                   'ERP5Site_getUpgraderSignature', "item=None",
                                    "return " + str(signature_code))
    transaction.commit()
    self.assertEquals(self.portal.ERP5Site_getUpgraderSignature(), signature_code)
    self.assertEquals(self.portal.ERP5Site_upgradeObjectList(), [])
    test_object = self.portal.portal_categories.newContent(id=self.upgrade_object_test_id,
                                             portal_type="Base Category")
    self.assertEquals(test_object.getValidationState(), 'embedded')
    self.assertNotEquals(self.portal.ERP5Site_upgradeObjectList(), [])
    self.assertNotEquals(self.portal.ERP5Site_upgradeObjectList(upgrade="1"), [])
    self.assertEquals(test_object.getValidationState(), 'published')

  def testUpgradeObjectClass(self):
    """
      Verify if all objects from one class are migrated to
      another class.
    """
    to_class_as_string = 'Products.ERP5Type.Document.Folder.Folder'
    signature_code = ( ('portal_gadgets', 
                        'ERP5Site_testUpgradeObjectClass',
                        to_class_as_string, 
                        'Products.ERP5Type.Document.Gadget.Gadget', 
                        'ERP5Site_testUpgradeObjectClass'), )

    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                   'ERP5Site_getUpgraderSignature', "item=None",
                                    "return " + str(signature_code))
    transaction.commit()
    self.assertEquals(self.portal.ERP5Site_getUpgraderSignature(), signature_code)
    # Nothing to upgrade
    self.assertEquals(self.portal.ERP5Site_upgradeObjectClass(), [])

    # Create one broken object
    gadget = self.portal.portal_gadgets.newContent(portal_type="Gadget", 
                                                   id=self.upgrade_object_test_id)
    self.stepTic()

    createZODBPythonScript(self.getPortal().portal_skins.custom,
                         "test_upgradeObject", 'x', 'return [1]')
    test_script = self.getPortal().portal_skins.custom.test_upgradeObject
    self.portal.portal_gadgets.upgradeObjectClass(
                                 test_script,
                                 gadget.__class__,
                                 to_class_as_string,
                                 test_script)

    transaction.commit()
    self.assertNotEquals(self.portal.ERP5Site_upgradeObjectClass(), [])
    self.assertEquals(self.portal.ERP5Site_upgradeObjectClass(upgrade=1),
                        [(gadget.getRelativeUrl(), 'ERP5 Gadget')])
    self.stepTic()
    self.assertEquals(self.portal.ERP5Site_upgradeObjectClass(), [])

  def test_UpgradeGlobalPropertyList(self):
    """
     Verify if the upgrade is needed
    """
    if getattr(self.portal, 'erp5_site_global_id', None) is not None:
      self.portal._updateProperty('erp5_site_global_id', "SOME_KEY")

    signature_code = {'erp5_site_global_id': self.upgrade_object_test_id}
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                   'ERP5Site_getUpgraderSignature', "item=None",
                                    "return " + str(signature_code))
    transaction.commit()
    self.assertEquals(self.portal.ERP5Site_getUpgraderSignature(), signature_code)
    self.assertEquals(self.portal.ERP5Site_upgradeGlobalPropertyList(), 
                      ["Upgrade Required for Global Properties."])

    self.assertEquals(["Upgrade Executed for Global Properties (erp5_site_global_id)."], 
                      self.portal.ERP5Site_upgradeGlobalPropertyList(upgrade=1))

    self.stepTic()
    self.assertEquals(self.portal.ERP5Site_upgradeGlobalPropertyList(), [])
    self.assertEquals(getattr(self.portal, 'erp5_site_global_id', None),
                      self.upgrade_object_test_id)

  def test_UpgradeWorkflowChain(self):
    """
     Upgrade the workflow chain if required.
    """
    workflow_tool = self.portal.portal_workflow
    workflow_dict = workflow_tool.getWorkflowChainDict()
    signature_code = workflow_dict
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                   'ERP5Site_getUpgraderSignature', "item=None",
                                    "return " + str(signature_code))
    transaction.commit()

    self.assertEquals(self.portal.ERP5Site_upgradeWorkflowChain(), [])

    original_person_chain = workflow_dict["chain_Person"]
    # Modify installed workflow chain.
    workflow_dict["chain_Person"] = ''
    workflow_tool.manage_changeWorkflows(default_chain = '', 
                                         props = workflow_dict)
    self.assertEquals(workflow_tool.getWorkflowChainDict()["chain_Person"],
                      "")
    self.assertEquals(self.portal.ERP5Site_upgradeWorkflowChain(),
                      ["Upgrade Required for Workflow Chain."])

    self.assertEquals(self.portal.ERP5Site_upgradeWorkflowChain(upgrade=1),
                      ["Upgrade Executed for Workflow Chain."])
    self.stepTic()
    self.assertEquals(self.portal.ERP5Site_upgradeWorkflowChain(),[])
    self.assertEquals(workflow_tool.getWorkflowChainDict()["chain_Person"],
                      original_person_chain)

  def test_RunVerificationScriptDontRaise(self):
    """ Test if the script ERP5Site_runVerificationScript is 
        bullet of proof, and always return a result.
    """
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                   'ERP5Site_raise', "",
                                    "raise ValueError('Error')")
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                   'ERP5Site_return', "",
                                   "return ['A']")

    failure = self.portal.ERP5Site_runVerificationScript("ERP5Site_raise")
    self.failUnless("Script ERP5Site_raise fail to run" in failure,
                    "'Script ERP5Site_raise fail to run not' in %s" % failure)
    self.assertEquals('ERP5Site_return : \n - A ',
       self.portal.ERP5Site_runVerificationScript("ERP5Site_return"))

  def test_UpgradePortalTypePropertySheet(self):
    """
      Test for Upgrate Portal Type Property Sheet script.
    """
    signature_code = (('Account', ["Person"]), )
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                                   'ERP5Site_getUpgraderSignature', "item=None",
                                    "return " + str(signature_code))
    transaction.commit()
    self.assertEquals(self.portal.ERP5Site_getUpgraderSignature(), signature_code)
    self.assertEquals(self.portal.ERP5Site_upgradePortalTypePropertySheet(),
                      ["Person doesn't has Account associated."])
    self.assertEquals(self.portal.ERP5Site_upgradePortalTypePropertySheet(upgrade=1),
                      ["Associate PropertySheet Account into Portal Type Person."])
    self.stepTic()
    self.assertEquals(self.portal.ERP5Site_upgradePortalTypePropertySheet(), [])


  def test_recreateActivities(self):
    """
      The activities should be recreated after upgrade products.
    """
    object_to_test = self.portal.portal_simulation
    createZODBPythonScript(self.getPortal().portal_skins.custom,
                   'ERP5Site_testRecreateActivityScript', "",
                   "context.manage_addProperty('custom_property_without_meaning', 'I was there', 'string')")

    transaction.commit()
    object_to_test.activate().ERP5Site_testRecreateActivityScript()

    transaction.commit()
    # Verify if the final activity is created.
    self.assertTrue(object_to_test.hasActivity(method_id="ERP5Site_testRecreateActivityScript"))
    self.portal.portal_activities.activate().ERP5Site_clearActivities()
    transaction.commit()
    self.assertTrue(object_to_test.hasActivity(method_id="ERP5Site_testRecreateActivityScript"))
    self.assertTrue(self.portal.portal_activities.hasActivity(method_id='ERP5Site_clearActivities'))
    self.stepTic()
    self.assertFalse(object_to_test.hasActivity(method_id="ERP5Site_testRecreateActivityScript"))
    self.assertFalse(self.portal.portal_activities.hasActivity(method_id='ERP5Site_clearActivities'))
    self.assertEquals(object_to_test.getProperty('custom_property_without_meaning'),
                      'I was there')

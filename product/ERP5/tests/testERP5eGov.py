# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                 Mayoro DIAGNE <mayoro@gmail.com>
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


import unittest
import transaction

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.utils import FileUpload

from zLOG import LOG
import os

TEST_FILES_HOME = os.path.join(os.path.dirname(__file__), 'test_data')

def makeFilePath(name):
  return os.path.join(os.path.dirname(__file__), 'test_data', name)

def makeFileUpload(name, as_name=None):
  if as_name is None:
    as_name = name
  path = makeFilePath(name)
  return FileUpload(path, as_name)

class TestEgov(ERP5TypeTestCase):
  """
  This is the list of test for erp5_egov

  """
  # define all username corresponding to all roles used in eGov
  assignor_login = 'chef'
  assignee_login = 'agent'
  auditor_login = 'reviewer'
  associate_login = 'agent_requested'

  def getBusinessTemplateList(self):
    """return list of business templates to be installed. """
    bt_list = ['erp5_core_proxy_field_legacy',
               'erp5_full_text_myisam_catalog',
               'erp5_base',
               'erp5_web',
               'erp5_ingestion_mysql_innodb_catalog',
               'erp5_ingestion',
               'erp5_dms',
               'erp5_egov_mysql_innodb_catalog',
               'erp5_egov']
    return bt_list

  def getTitle(self):
    return "Test ERP5 EGov"

  #XXX mayoro: these functions will be removed and replaced by subscriptions
  def createCitizenUser(self):
    """
    Create a user with Agent role to allow create and submit requests
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('citizen', '', ['Agent',], [])

  def createAgentUser(self):
    """
    Create a user with Agent role to allow create and submit requests
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('agent', '', ['Assignee',], [])

  def createValidatorUser(self):
    """
    Create a user with Agent role to allow create and submit requests
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('major', '', ['Assignor',], [])

  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList():
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:]:
        if not cat in path.objectIds():
          path = path.newContent(
            portal_type='Category',
            id=cat,)
        else:
          path = path[cat]
    self.tic()
    transaction.commit()
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """Returns a list of categories that should be created."""
    return ('group/client','group/client/dgid/di', 'group/client/dgid/bf',
            'function/impots/taxes_indirectes', 'function/impots/section/chef',
            'role/citoyen', 'role/citoyen/national', 'role/citoyen/etranger', 'role/gouvernement',
            'role/entreprise', 'role/entreprise/agence', 'role/entreprise/siege', 'role/entreprise/succursale', 
            'function/entreprise/mandataire')

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager', 'Assignor','Assignee'], [])
    self.login('seb')
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)
    self.portal = self.getPortalObject()
    self.createCategories()
    # enable preferences
    pref = self.portal.portal_preferences._getOb(
                  'flare_cache_preference', None)
    if pref is not None:
      if pref.getPreferenceState() == 'disabled':
        pref.enable()
    pref = self.portal.portal_preferences._getOb(
                  'egov_preference', None)
    if pref is not None:
      if pref.getPreferenceState() == 'disabled':
        pref.enable()

    transaction.commit()
    self.tic()
    #set up the instance
    self.portal.EGov_setUpInstance()

  def beforeTearDown(self):
    """
    remove all created objects between two tests, tests are stand-alone
    """
    transaction.abort()
    for module in [ self.getPersonModule(),
                    self.getOrganisationModule(),
                      ]:
      module.manage_delObjects(list(module.objectIds()))

    vat_portal_type = self.portal.portal_types.getTypeInfo('Vat Declaration')
    vat_module_portal_type = self.portal.portal_types.getTypeInfo('Vat Declaration Module')
    if vat_portal_type is not None and vat_module_portal_type is not None:
      vat_module = self.portal.getDefaultModule('Vat Declaration')
      self.portal.portal_types.manage_delObjects([vat_portal_type.getId(), vat_module_portal_type.getId()])
      self.portal.manage_delObjects([vat_module.getId(),]) 
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    self.tic()

  def changeSkin(self, skin_name):
    """
      Change current Skin
    """
    request = self.app.REQUEST
    self.portal.portal_skins.changeSkin(skin_name)
    request.set('portal_skin', skin_name)

  def createNewProcedure(self):
    """
     This function create a new EGov Type   
    """
    return self.portal.portal_types.newContent(portal_type='EGov Type')


  def fillProcedureForm(self, procedure=None, procedure_title='fooo'):
    """
     This function fill the form of a given procedure. Filled field allow to 
     generate portal_type and portal_type module of this procedure, it also allow
     configuring securities of the new module and renaming actions   
    """
    # initialize values for new procedure
    # use accessors to verify if they are dynamically generated
    if procedure is None:
      return
    procedure.setOrganisationDirectionService('client/dgid/di')
    procedure.setProcedureTitle(procedure_title)
    procedure.setProcedurePublicationSection('impots/taxes_indirectes')
    procedure.setProcedureTarget('entreprise')
    procedure.setStepAuthentication(1)
    procedure.setStepPrevalidation(1)
    procedure.setStepAttachment(1)
    procedure.setStepPostpayment(1)
    procedure.setStepDecision(1)
    procedure.setStepRemittance(1)
    # add one attchment
    procedure.setAttachmentTitle1('Justificatif numero 1')
    procedure.setAttachmentRequired1(1)
    procedure.setAttachmentModel1('PDF')
    procedure.setAttachmentJustificative1(1)

    # add security configuration
    # define security for agent to process (assignor)
    procedure.setInvolvedServiceGroup1('client/dgid/di')
    procedure.setInvolvedServiceFunction1('impots/section/chef')
    procedure.setInvolvedServiceProcess1(0)
    procedure.setInvolvedServiceValidate1(1)
    procedure.setInvolvedServiceView1(0)
    procedure.setInvolvedServiceAssociate1(0)
    # define security for agent to just process assigned
    # applications (Assignee)
    procedure.setInvolvedServiceGroup2('client/dgid/di')
    procedure.setInvolvedServiceFunction2('impots/inspecteur')
    procedure.setInvolvedServiceProcess2(1)
    procedure.setInvolvedServiceValidate2(0)
    procedure.setInvolvedServiceView2(0)
    procedure.setInvolvedServiceAssociate2(0)

    # define security for external agent to contribute
    # in processing (Associate)
    procedure.setInvolvedServiceGroup3('client/dgid/bf')
    procedure.setInvolvedServiceFunction3('impots/section/chef')
    procedure.setInvolvedServiceProcess3(0)
    procedure.setInvolvedServiceValidate3(0)
    procedure.setInvolvedServiceView3(0)
    procedure.setInvolvedServiceAssociate3(1)

    # define security for agent to just view (auditor)
    procedure.setInvolvedServiceGroup2('client/dgid/di')
    procedure.setInvolvedServiceFunction2('impots')
    procedure.setInvolvedServiceProcess2(0)
    procedure.setInvolvedServiceValidate2(0)
    procedure.setInvolvedServiceView2(1)
    procedure.setInvolvedServiceAssociate2(0)

    # configure portal_type for displaying subobjects
    scribus_file_name = 'Certificat_Residence.sla'
    pdf_file_name = 'Certificat_Residence.pdf'
    pdf_file_data = makeFileUpload(pdf_file_name)
    scribus_file_data = makeFileUpload(scribus_file_name)
    procedure.edit(scribus_form_file=scribus_file_data,
            pdf_form_file=pdf_file_data)
    self.tic()
    transaction.commit()
    self.tic()

  def test_01_new_procedure_creation(self):
    """ 
    this test create one procedure, initialize it by some datas, validate it
    to generate the module and portal_types and verify some properties  
    """
    procedure = self.createNewProcedure()
    self.fillProcedureForm(procedure, 'vat declaration')
    procedure.validate()
    vat_module = self.portal.getDefaultModule('Vat Declaration')
    self.assertEquals(vat_module.getId(), 'vat_declaration_module')
    vat_portal_type = self.portal.portal_types.getTypeInfo('Vat Declaration')
    self.assertEquals(vat_portal_type.getId(), 'Vat Declaration')
    self.assertTrue(vat_portal_type.getDefaultScribusFormValue().getData()
                                                 not in ('', None))
    self.assertTrue(vat_portal_type.getDefaultPdfFormValue().getData()
                                                 not in ('', None))
    id_generator = vat_module.getIdGenerator()
    self.assertEquals(id_generator, '_generatePerDayId')

  def test_02_application_creation(self):
    """
    This test create a procedure: vat declaration and use it with a simple user
    to just create a vat declaration and access it in different mode
    """
    procedure = self.createNewProcedure()
    self.fillProcedureForm(procedure, 'vat declaration')
    procedure.validate()
    self.createCitizenUser()
    self.logout()
    self.login('citizen')
    #Allow citizen to have Agent role to create application
    vat_module = self.portal.getDefaultModule('Vat Declaration')
    vat_declaration = vat_module.newContent(portal_type='Vat Declaration')
    # test form generation
    # change to EGov skin which is defined in erp5_egov
    self.changeSkin('EGov') 
    vat_declaration.view()
    vat_declaration.PDFType_viewAsPdf()
    application_dict = vat_declaration.PDFDocument_getApplicationIncomeDict()
    self.assertEquals(len(application_dict), 1)
    report_section_list = vat_declaration.PDFDocument_getReportSectionList()
    self.assertEquals(len(report_section_list), 1)
    vat_declaration.PDFDocument_viewHistory()

  def test_03_submit_application(self):
    """
    This test create an application fill it, join required
    attachments and submit it 
    """
    procedure = self.createNewProcedure()
    self.fillProcedureForm(procedure, 'vat declaration')
    procedure.validate()
    self.createCitizenUser()
    self.logout()
    self.login('citizen')
    #Allow citizen to have Agent role to create application
    vat_module = self.portal.getDefaultModule('Vat Declaration')
    vat_declaration = vat_module.newContent(portal_type='Vat Declaration')
    # test form generation
    # change to EGov skin which is defined in erp5_egov
    self.changeSkin('EGov') 
    self.assertEquals('draft', vat_declaration.getValidationState())
    missing_file = vat_declaration.PDFDocument_getRequirementCount()
    self.assertEquals(missing_file, 1)  
    type_allowed_content_type_list = vat_declaration.getTypeInfo().getTypeAllowedContentTypeList()
    type_allowed_content_type_list.append('PDF')
    vat_declaration.getTypeInfo().setTypeAllowedContentTypeList(type_allowed_content_type_list)
    vat_declaration.getTypeInfo().setTypeHiddenContentTypeList(type_allowed_content_type_list)
    vat_declaration.newContent(portal_type='PDF', title='Justificatif numero 1')
    self.tic()
    transaction.commit()
    missing_file = vat_declaration.PDFDocument_getRequirementCount()
    self.assertEquals(missing_file, 0)
    self.portal.portal_workflow.doActionFor(vat_declaration, 'submit_draft_action')
    self.assertEquals('submitted', vat_declaration.getValidationState())

  def test_05_process_application(self):
    """
    This test process a submitted application and verify allowed transition
    according to steps define in the procedure 
    """
    procedure = self.createNewProcedure()
    self.fillProcedureForm(procedure, 'vat declaration')
    procedure.validate()
    self.createCitizenUser()
    self.logout()
    self.login('citizen')
    #Allow citizen to have Agent role to create application
    vat_module = self.portal.getDefaultModule('Vat Declaration')
    vat_declaration = vat_module.newContent(portal_type='Vat Declaration')
    # test form generation
    # change to EGov skin which is defined in erp5_egov
    self.changeSkin('EGov') 
    self.portal.portal_workflow.doActionFor(vat_declaration, 'submit_draft_action')
    self.assertEquals('submitted', vat_declaration.getValidationState())
    self.createAgentUser()
    self.logout()
    self.login('agent')
    vat_declaration.view()
    vat_declaration.PDFDocument_getApplicationIncomeDict()
    vat_declaration.PDFDocument_getReportSectionList()
    vat_declaration.PDFDocument_viewHistory()
    self.portal.portal_workflow.doActionFor(vat_declaration, 'receive_action')
    if vat_declaration.getTypeInfo().getStepReviewRequest() is None:
      self.assertEquals('completed', vat_declaration.getValidationState())
    """
    else:
      self.assertEquals('receivable', vat_declaration.getValidationState())
      self.assertEquals(vat_declaration.getTypeInfo().getStepReviewRequest(),None)
      self.portal.portal_workflow.doActionFor(vat_declaration, 'assign_action')
      self.assertEquals('assigned', vat_declaration.getValidationState())
      self.createValidatorUser()
      self.logout()
      self.login('major')
      self.portal.portal_workflow.doActionFor(vat_declaration, 'complete_action')
      self.assertEquals('completed', vat_declaration.getValidationState())
    """

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestEgov))
  return suite


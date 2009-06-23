##############################################################################
# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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
import os, sys
import unittest

import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from string import zfill
import sys
from zLOG import LOG
from Products.ERP5Type.Message import Message

# dependency order
target_business_templates = (
  'erp5_base',
  'erp5_trade',

  'erp5_pdf_editor',
  'erp5_pdf_style',
  'erp5_pdm',
  'erp5_accounting',
  'erp5_invoicing',

  'erp5_apparel',

##   'erp5_banking_core',
##   'erp5_banking_cash',
##   'erp5_banking_check',
##   'erp5_banking_inventory',

  'erp5_budget',
  'erp5_public_accounting_budget',

  'erp5_consulting',

  'erp5_ingestion',
  'erp5_ingestion_mysql_innodb_catalog',
  'erp5_crm',

  'erp5_web',
  'erp5_dms',

  'erp5_commerce',

  'erp5_forge',

  'erp5_immobilisation',

  'erp5_item',

  'erp5_mrp',

  'erp5_payroll',

  'erp5_project',

  'erp5_calendar',

  'erp5_l10n_fr',
  'erp5_l10n_ja',
  'erp5_l10n_pl_PL',
  'erp5_l10n_pt-BR',
)

class TestTranslation(ERP5TypeTestCase):
  run_all_test = 1
  domain = 'erp5_ui'
  lang = 'en'

  def getTitle(self):
    return "Translation Test"

  def getBusinessTemplateList(self):
    """  """
    return target_business_templates

  def getTranslation(self, msgid):
    
    result = self.portal.Localizer.erp5_ui.gettext(
          msgid, default='')
    #result = self.portal.Localizer.translate(
        #domain=self.domain, msgid=msgid, lang=self.lang)
    if (result == msgid) and (self.lang != 'en'):
      #result = None
      result = self.portal.Localizer.erp5_ui.gettext(msgid)
    return result.encode('utf8')

  def logMessage(self, message):
    self.message += '%s\n' % message

  def checkWorkflowStateTitle(self, quiet=0, run=run_all_test):
    """
    Test workflow state title translation.
    Check that using portal_catalog can not return strange results to the user.
    Each translation must be only related to one state ID.
    """
    if not run: return
    self.message = '\n'

    translation_dict = {}

    workflow_tool = self.portal.portal_workflow
    for workflow_id in workflow_tool.objectIds():
      workflow = workflow_tool._getOb(workflow_id)
      class_name = workflow.__class__.__name__
      if class_name == 'DCWorkflowDefinition':
        for state in workflow.states.items():
          state_title = state[1].title
          state_id = state[0]
	  msgid = '%s [state in %s]' % (state_title, workflow_id)
          translated_state_title = self.getTranslation(msgid)

          if translated_state_title is not None:
            if translation_dict.has_key(translated_state_title):
              translation_dict[translated_state_title].add(state_id)
            else:
              translation_dict[translated_state_title] = set([state_id])


    for key, value in translation_dict.items():
      if len(value) == 1:
        translation_dict.pop(key)

    if translation_dict != {}:
      # State ID has multiple translation associated, and it leads to
      # unexpected results for the user when using portal catalog.
      rejected_key_list = translation_dict.keys()
      result_dict = dict([(x, []) for x in rejected_key_list])
      error_dict =  dict([(x, []) for x in rejected_key_list])
      error = 0

      # Browse all workflows to ease fixing this issue.
      for workflow in self.portal.portal_workflow.objectValues():
        if workflow.__class__.__name__ == 'DCWorkflowDefinition':
          workflow_id = workflow.id
          workflow_dict = {}
          for state_id, state in workflow.states._mapping.items():
            state_title = state.title
            translated_state_title = \
              self.portal.Localizer.erp5_ui.gettext(state_title, lang=self.lang)
            if translated_state_title in rejected_key_list:
              result_dict[translated_state_title].append(
                  (workflow_id, state_id, state_title))

      # XXX To be improved
      not_used_workflow_id_list = []
      for key, item_list in result_dict.items():
        wrong_state_id_list = [x[1] for x in item_list]
        for workflow_id, wrong_state_id, state_title in item_list:
          if workflow_id not in not_used_workflow_id_list:
            workflow = self.portal.portal_workflow._getOb(workflow_id)
            state_id_list = []
            for state_id in workflow.states._mapping.keys():
              if (state_id in wrong_state_id_list) and \
                  (state_id != wrong_state_id):
                state_id_list.append(state_id)

            if len(state_id_list) != 0:
              error_dict[key].append((
                workflow_id, wrong_state_id, state_title, state_id_list))
              error = 1
      
      if error:
        for key, item_list in error_dict.items():
          if len(item_list) != 0:
            self.logMessage("\n'%s'" % key.encode('utf-8'))
            self.logMessage('\t### Conflicting workflow with common states (ie, what user can see) ###')
            for item in item_list:
              # XXX Improve rendering
              self.logMessage(
                  "\t%r\t%r\t'%s'\t%r" % \
                  item)
            self.logMessage('\n\t### All conflicting workflows (ie, problems asking to happen) ###')
            for item in result_dict[key]:
              # XXX Improve rendering
              self.logMessage(
                  "\t%r\t%r\t'%s'" % \
                  item)
        
        self.fail(self.message)

  def test_01_EnglishTranslation(self, quiet=0, run=run_all_test):
    """
    Test English translation
    """
    self.lang = 'en'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_02_FrenchTranslation(self, quiet=0, run=run_all_test):
    """
    Test French translation
    """
    self.lang = 'fr'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_03_JapaneseTranslation(self, quiet=0, run=run_all_test):
    """
    Test Japanese translation
    """
    self.lang = 'ja'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_04_PolishTranslation(self, quiet=0, run=run_all_test):
    """
    Test Polish translation
    """
    self.lang = 'pl'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)

  def test_05_PortugueseTranslation(self, quiet=0, run=run_all_test):
    """
    Test Portuguese translation
    """
    self.lang = 'pt-BR'
    self.checkWorkflowStateTitle(quiet=quiet, run=run)
    
  def test_06_FrenchTranslationOfMessageWithContext(self, quiet=0,
         run=run_all_test):
    """
    Test French translation
    """
    self.lang = 'fr'
    
    message_catalog = self.portal.Localizer.erp5_ui
    message_catalog.gettext('Validated', add=1)
    message_catalog.gettext("Draft",add=1)
    message_catalog.gettext("Validated [state in item_workflow]", add=1)
    message_catalog.message_edit(
              'Validated', self.lang, 'Validé'.decode('utf8'), '')
    message_catalog.message_edit(
    "Validated [state in item_workflow]",self.lang,"En bon usage", '')
    message_catalog.message_edit('Draft', self.lang, '', '')
    organisation_module = self.getPortal().organisation_module
    organisation = organisation_module.newContent(
                  portal_type='Organisation',
                  title = 'My Organisation')
    organisation.validate()
    item_module = self.getPortal().item_module
    item = item_module.newContent(portal_type='Item',
                                  title = 'Lot A')
                                  

    transaction.commit()
    self.tic()
    self.portal.Localizer.get_selected_language = lambda: self.lang
    
    self.assertEquals(
         item.getTranslatedValidationStateTitle(),'Draft')
    item.validate()
    self.assertEquals(item.getTranslatedValidationStateTitle(),
                              "En bon usage") 
    self.assertEquals(
         organisation.getTranslatedValidationStateTitle(),'Validé')
    
    
     
    
  def test_standard_translated_related_keys(self):
    # make sure we can search by "translated_validation_state_title" and
    # "translated_portal_type"
    message_catalog = self.portal.Localizer.erp5_ui
    lang = 'fr'
    if lang not in [x['id'] for x in
        self.portal.Localizer.get_languages_map()]:
      self.portal.Localizer.manage_addLanguage(lang)

    message_catalog.gettext('Draft', add=1)
    message_catalog.gettext('Person', add=1)
    message_catalog.message_edit('Draft', lang, 'Brouillon', '')
    message_catalog.message_edit('Person', lang, 'Personne', '')

    person_1 = self.portal.person_module.newContent(portal_type='Person')
    person_1.validate()
    person_2 = self.portal.person_module.newContent(portal_type='Person')
    organisation = self.portal.organisation_module.newContent(
                            portal_type='Organisation')
    
    transaction.commit()
    self.tic()

    # patch the method, we'll abort later
    self.portal.Localizer.get_selected_language = lambda: lang
    self.assertEquals(set([person_1, person_2]),
        set([x.getObject() for x in
          self.portal.portal_catalog(translated_portal_type='Personne')]))
    LOG("ORGANISATION TEST",0,organisation)
   
    self.assertEquals(set([person_2, organisation]),
        set([x.getObject() for x in
          self.portal.portal_catalog(translated_validation_state_title='Brouillon',
                                     portal_type=('Person', 'Organisation'))]))
    self.assertEquals([person_2],
        [x.getObject() for x in
          self.portal.portal_catalog(translated_validation_state_title='Brouillon',
                                     translated_portal_type='Personne')])
    transaction.abort()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTranslation))
  return suite
